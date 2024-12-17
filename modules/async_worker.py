# OLD CODE START ###

from asyncio import tasks
import copy
import datetime
import os
import random
import sys
import threading
import traceback
from typing import List, Optional


import PIL
import PIL.Image
import numpy as np
import time

from torch import Tensor, tensor

from h3_utils import logging_util
from modules.imagen_utils.imagen_patch_utils.patch import patch_all
from unavoided_globals import unavoided_global_vars
from extras import face_crop, preprocessors
from extras.expansion import safe_str
from extras.censor import default_censor
from modules.imagen_utils.inpaint_worker import InpaintWorker
from modules.imagen_utils.upscale.upscaler import perform_upscale
from unavoided_globals.unavoided_global_vars import PatchSettings
from unavoided_globals.global_model_management import global_model_management
from h3_utils.model_file_config import (
    PyraCanny,
    CPDS,
    ImagePromptAdapterFace,
    ImagePromptClipVIsion,
    ImagePromptAdapterNegative,
    ImagePromptAdapterPlus
)
from h3_utils.model_file_config import (
    UpscaleModel,
    InpaintModelFiles,
    ControlNetTasks,
    SDXL_HyperSDLoRA,
    SDXL_LCM_LoRA,
    SDXL_LightningLoRA,
)



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import h3_utils.config as config
import h3_utils.flags as flags
from h3_utils.logging_util import LoggingUtil
from h3_utils.sdxl_prompt_expansion_utils import apply_arrays, apply_style, fooocus_expansion, get_random_style
from h3_utils.flags import LORA_FILENAMES, Overrides, Performance, Steps

import extras.ip_adapter as ip_adapter

from modules.util import apply_wildcards, ensure_three_channels, erode_or_dilate, get_image_shape_ceil, get_shape_ceil, parse_lora_references_from_prompt, remove_empty_str, remove_performance_lora, resample_image, resize_image, set_image_shape_ceil
from modules.imagen_utils.private_logger import log
from modules.default_pipeline import DefaultPipeline
from modules.core import apply_controlnet, apply_freeu, encode_vae, numpy_to_pytorch

from unavoided_globals.unavoided_global_vars import (
    patch_settings_GLOBAL_CAUTION,
    opModelSamplingDiscrete,
    opModelSamplingContinuousEDM,
    apply_patch_settings,
)

import ldm_patched.modules.model_management

patch_all()

GlobalConfig = config.LAUNCH_ARGS

logger = LoggingUtil(name="ImageTaskProcessor").get_logger()

class EarlyReturnException(BaseException):
    pass

class ImageTaskProcessor:
    def __init__(self):
        self.initialize_processor()
        self.preview_yelder = None

    def initialize_processor(self):
        self.pid = os.getpid()
        self.pipeline = DefaultPipeline()
        
        self.log_messages: list = []
        self.yields: list = []
        self.current_progress: int = 1
        self.total_progress: int = 100

        self.generation_task: config.ImageGenerationObject = None
        self.generation_tasks: List[config.ImageGenerationObject] = []

        self.ip_adapter = ip_adapter.IpaAdapterManagement()

        self.update_progress(f"Initialized ImageTaskProcessor with PID {self.pid}", 0)

    def initialize_current_task(self, new_task: config.ImageGenerationObject = None):
        new_task._prepare_downloads()
        new_task._prepare_controlnet_model_downloads()
        new_task.download_models()
        self.generation_task = new_task
        self.patch_settings = PatchSettings()
        self.inpaint_worker: InpaintWorker = None

        self.results = []
        self.goals = []
        self.imgs = []
        self.tasks: List[config.TaskletObject] = []

        self.all_steps = 0
        self.step = 0
        self.callback_steps = 0
        self.preparation_steps = 0
        self.original_steps = -1

        self.prepared_inpaint_mask = None
        self.tiled = False
        
        self.processing = False
        self.processing_status = False

        self.skip_prompt_processing = False
        self.use_synthetic_refiner = False
        self.use_prompt_expansion = False
        self.use_styles = False

        self.extra_positive_prompts: List[str] = []
        self.extra_negative_prompts: List[str] = []
        self.base_model_additional_loras: List[str] = []

        self.controlnet_pyracanny_path: Optional[str] = None
        self.controlnet_cpds_path: Optional[str] = None
        self.clip_vision_path: Optional[str] = None
        self.ip_negative_path: Optional[str] = None
        self.ip_adapter_path: Optional[str] = None
        self.ip_adapter_face_path: Optional[str] = None
        self.inpaint_head_model_path: Optional[str] = None
        self.inpaint_patch_model_path: Optional[str] = None
        self.upscale_model_path: Optional[str] = None

        self.final_scheduler_name: Optional[str] = None

        self.initial_latent: Optional[Tensor] = None

        self.denoising_strength: float = 1.0 # Default value

        self.cleanup_bowl = []

        self.set_steps()
        self.check_refiner_not_same_as_base_model()
        self.get_defaults_per_performance()
        self.prepare_attributes()
        self.update_controlnet_models()


    def yield_result(self, imgs: list, do_not_show_finished_images=False):
        """Processes a list of images, optionally censors NSFW content, and updates the results."""
        imgs = self.censor_images_if_needed(imgs)
        self.results += imgs


    # OK
    def censor_images_if_needed(self, imgs: list) -> list:
        """Censors NSFW content in images if the configuration requires it."""
        if GlobalConfig.black_out_nsfw:
            self.update_progress("Censoring NSFW content")
            imgs = default_censor(imgs)
        return imgs

    # OK
    def process_tasklet(_self, prepared_task: config.TaskletObject):
        """Processes a single image generation tasklet."""
        parent_task: config.ImageGenerationObject = _self.generation_task

        _self.final_scheduler_name = _self.patch_samplers()
        _self.update_progress(f"Final scheduler: {_self.final_scheduler_name}")
        _self.interrupt_if_needed()
        _self.processing = True
        
        
        processing_start_time = time.perf_counter()
        preparation_steps = _self.current_progress
        id = _self.tasks.index(prepared_task)
        uid = prepared_task.uid

        """
        def callback(step, x0, x, total_steps):
        global_model_management.throw_exception_if_processing_interrupted()
        y = None
        if previewer is not None and not disable_preview:
            y = previewer(x0, previewer_start + step, previewer_end)
        if callback_function is not None:
            callback_function(previewer_start + step, x0, x, previewer_end, y)
        
        """
        def _callback(step, x0, x, total_steps, y, preview_yelder=_self.preview_yelder):
            if step == 0:
                _self.callback_steps = 0
            _self.callback_steps += (100 - preparation_steps) / float(_self.all_steps)
            logger.debug(f"Callback step: {step + 1}/{total_steps}, image {id + 1}/{len(_self.tasks)}")
            is_finished = step == total_steps - 1
            if preview_yelder is not None:
                #TODO REMOVE
                pass
            if not is_finished:
                _self.yields.append(['preview', (
                    int(_self.current_progress + _self.callback_steps),
                    f'Sampling step {step + 1}/{_self.all_steps}, image {id + 1}/{len(_self.tasks)} ...'), y, uid])
            
            elif is_finished:
                _self.yields.append(['finish', (
                    _self.current_progress + 100,
                    f'Image {id + 1}/{len(_self.tasks)} finished ...'), y, uid])
                
            else:
                raise EarlyReturnException()
            

        if 'cn' in _self.goals:
            prepared_task.encoded_positive_cond, 
            prepared_task.encoded_negative_cond = \
                _self.get_conditions_from_input_img_controlnet(
                prepared_task.encoded_positive_cond, 
                prepared_task.encoded_negative_cond)

        imgs = _self.pipeline.process_diffusion(
            # Shared parameters of all tasklets
            steps=parent_task.steps,
            switch=parent_task.refiner_switch,
            width=parent_task.width,
            height=parent_task.height,
            image_seed=parent_task.seed,
            sampler_name=parent_task.sampler_name,
            cfg_scale=parent_task.cfg_scale,
            refiner_swap_method=parent_task.refiner_swap_method,
            disable_preview=parent_task.developer_options.disable_preview,
            
            # Tasklet-specific parameters
            positive_cond=prepared_task.encoded_positive_cond,
            negative_cond=prepared_task.encoded_negative_cond,
            
            # Class / function bound parameters
            callback=_callback,
            scheduler_name=_self.final_scheduler_name,
            latent=_self.initial_latent,
            denoise=_self.denoising_strength,
            tiled=_self.tiled,
            inpaintworker=_self.inpaint_worker,
        )

        _self.cleanup_vars([prepared_task.encoded_positive_cond, prepared_task.encoded_negative_cond])

        imgs = _self.post_process_images(imgs)
        # current_progress = int(self.current_progress + (100 - preparation_steps) / float(self.all_steps) * parent_task.steps)
        _self.update_progress(f"Saving image to system ...")
        img_paths = save_images(imgs, "webp")
        _self.update_progress(f"Image saved to system.")
        for _img in imgs:
            _self.yields.append(['result', (100, f'Image {id + 1}/{len(_self.tasks)} finished ...'), _img, uid])
        # TODO: Log the image paths
        processing_time = time.perf_counter() - processing_start_time
        print(f"Processing time: {processing_time:.2f} seconds")
        _self.processing = False
        return imgs, img_paths

    # OK
    def cleanup_vars(self, vars: list) -> None:
        """Cleans up variables after processing a task."""
        for var in vars:
            if isinstance(var, np.ndarray):
                del var
            else:
                self.update_progress("Variable is not a numpy array, skipping deletion and setting to none.", 0)
                var = None

    # OK
    def interrupt_if_needed(self):
        """Interrupts the current processing if the last stop is not False."""
        if self.processing:
            # GLOBAL VAR CALL
            global_model_management.interrupt_current_processing()
            self.processing = False

    # OK
    def get_conditions_from_input_img_controlnet(self, positive_cond, negative_cond):
        if self.generation_task.controlnet_tasks:
            for controlnet_task in self.generation_task.controlnet_tasks:
                if controlnet_task.name [ControlNetTasks.CPDS.name, ControlNetTasks.PyraCanny.name]:
                    positive_cond, negative_cond = apply_controlnet(
                        positive_cond,
                        negative_cond,
                        self.pipeline.loaded_ControlNets[controlnet_task.models[0].full_path()], # Only has one model
                        controlnet_task.img,
                        controlnet_task.weight,
                        0,
                        controlnet_task.stop,
                    )
        return positive_cond, negative_cond

    # OK
    def post_process_images(self, imgs):
        """Post-processes images using the inpaint worker if available."""
        if self.inpaint_worker:
            imgs = [self.inpaint_worker.post_process(x) for x in imgs]
        else:
            self.update_progress("No inpaint worker available, skipping post-processing", 0)
        return imgs

    # OK
    def process_prompt(self):
        """Processes the prompt and prepares tasks for image generation."""
        self.prepare_prompts()
        self.prepare_loras()

        self.pipeline.refresh_everything(
            refiner_model_name=self.generation_task.refiner_model,
            base_model_name=self.generation_task.base_model_name,
            loras=self.generation_task.loras,
            base_model_additional_loras=self.base_model_additional_loras,
            use_synthetic_refiner=self.use_synthetic_refiner,
            vae_name=self.generation_task.vae_name
        )

        self.pipeline.set_clip_skip(self.generation_task.clip_skip)
        self.update_progress(f"Processing prompts ...", 0)

        self.create_tasks()
        return

    # OK
    def prepare_prompts(self):
        """Prepares and returns the main and negative prompts."""
        prompts = remove_empty_str([safe_str(p) for p in self.generation_task.prompt.splitlines()], default="")
        negative_prompts = remove_empty_str([safe_str(p) for p in self.generation_task.negative_prompt.splitlines()], default="")
        self.generation_task.prompt = prompts[0]
        self.generation_task.negative_prompt = negative_prompts[0]

        self.extra_positive_prompts = prompts[1:] if len(prompts) > 1 else []
        self.extra_negative_prompts = negative_prompts[1:] if len(negative_prompts) > 1 else []

        # Advance progress
        if self.use_prompt_expansion and self.generation_task.prompt:
            self.use_prompt_expansion = True
        return 

    # OK
    def prepare_loras(self):
        """Prepares and returns the loras for the task."""
        task: config.ImageGenerationObject = self.generation_task
        updated_lora_filenames = remove_performance_lora(LORA_FILENAMES, self.generation_task.performance_selection)
        loras, prompt = parse_lora_references_from_prompt(task.prompt, task.loras, flags.max_lora_number, lora_filenames=updated_lora_filenames)
        loras += self.generation_task.performance_loras
        self.generation_task.loras = loras
        return 

    # OK
    def create_tasks(self):
        """Creates tasks for image generation."""
        tasks = []
        self.update_progress("Creating tasks ...")
        for i in range(self.generation_task.image_number):
            uid = self.generation_task.uid
            task_seed, task_rng = self.get_task_seed_and_rng(i)

            task_prompt, task_negative_prompt, task_extra_positive_prompts, task_extra_negative_prompts = self.get_task_prompts(task_rng, i)

            positive_basic_workloads, negative_basic_workloads = self.get_basic_workloads(
                task_prompt, task_negative_prompt, task_extra_positive_prompts, task_extra_negative_prompts)

            task_styles = self.get_task_styles(task_prompt, positive_basic_workloads, task_rng)

            tasks.append(self.create_a_tasklet(task_seed, task_prompt, task_negative_prompt, positive_basic_workloads,
                                               negative_basic_workloads, task_styles, task_extra_positive_prompts,
                                               task_extra_negative_prompts, uid))
        if self.use_prompt_expansion:
            tasks = self.expand_prompts(tasks)
        self.encode_prompts(tasks)
        self.tasks = tasks
        return True

    # OK
    def get_task_seed_and_rng(self, i):
        """Returns the task seed and random number generator."""
        if self.generation_task.developer_options.disable_seed_increment:
            task_seed = self.generation_task.seed
        else:
            task_seed = (self.generation_task.seed + i) % (GlobalConfig.max_seed + 1)
        task_rng = random.Random(task_seed)
        return task_seed, task_rng

    # OK
    def get_task_prompts(self, task_rng, i):
        """Returns the task prompts and extra prompts."""
        task_prompt = apply_wildcards(self.generation_task.prompt, task_rng, i, self.generation_task.read_wildcards_in_order)
        task_prompt = apply_arrays(task_prompt, i)
        task_negative_prompt = apply_wildcards(self.generation_task.negative_prompt, task_rng, i, self.generation_task.read_wildcards_in_order)
        extra_positive_prompts = [apply_wildcards(pmt, task_rng, i, self.generation_task.read_wildcards_in_order) for pmt in
                                  remove_empty_str([safe_str(p) for p in self.generation_task.prompt.splitlines()][1:], default="")]
        extra_negative_prompts = [apply_wildcards(pmt, task_rng, i, self.generation_task.read_wildcards_in_order) for pmt in
                                  remove_empty_str([safe_str(p) for p in self.generation_task.negative_prompt.splitlines()][1:], default="")]

        return task_prompt, task_negative_prompt, extra_positive_prompts, extra_negative_prompts
        

    # OK
    def get_basic_workloads(self, task_prompt, task_negative_prompt, task_extra_positive_prompts, task_extra_negative_prompts):
        """Returns the basic workloads for positive and negative prompts."""
        positive_basic_workloads = [task_prompt] + task_extra_positive_prompts
        negative_basic_workloads = [task_negative_prompt] + task_extra_negative_prompts
        return remove_empty_str(positive_basic_workloads, default=task_prompt), remove_empty_str(negative_basic_workloads, default=task_negative_prompt)

    # OK
    def get_task_styles(self, task_prompt, positive_basic_workloads: list, task_rng):
        """Returns the task styles."""
        task_styles = self.generation_task.styles.copy()
        if self.use_styles:
            placeholder_replaced = False
            for j, s in enumerate(task_styles):
                if s == flags.random_style_name:
                    s = get_random_style(task_rng)
                    task_styles[j] = s
                p, n, style_has_placeholder = apply_style(s, positive=task_prompt)
                if style_has_placeholder:
                    placeholder_replaced = True
                positive_basic_workloads.extend(p)
            if not placeholder_replaced:
                positive_basic_workloads.insert(0, task_prompt)
        return task_styles

    # OK
    def create_a_tasklet(self, task_seed, task_prompt, task_negative_prompt, positive_basic_workloads,
                         negative_basic_workloads, task_styles, task_extra_positive_prompts, task_extra_negative_prompts, uid):
        """Creates and returns a task dictionary."""
        self.update_progress(f"Creating task dictionary for seed {task_seed} ...", 0)
        tasklet_object = config.TaskletObject(
            task_seed=task_seed,
            task_prompt=task_prompt,
            task_negative_prompt=task_negative_prompt,
            positive_basic_workloads=positive_basic_workloads,
            negative_basic_workloads=negative_basic_workloads,
            expansion="",
            encoded_positive_cond=None,
            encoded_negative_cond=None,
            positive_top_k=len(positive_basic_workloads),
            negative_top_k=len(negative_basic_workloads),
            log_positive_prompt="\n".join([task_prompt] + task_extra_positive_prompts),
            log_negative_prompt="\n".join([task_negative_prompt] + task_extra_negative_prompts),
            styles=task_styles,
            uid=uid
        )
        #self.update_progress(f"Tasklet: {tasklet_object}", 0)
        self.update_progress(f"Tasklet created with uid {uid}.", 0)
        return tasklet_object

    # OK
    def expand_prompts(self, tasks: List[config.TaskletObject]):
        """Expands the prompts for task."""
        for i, task in enumerate(tasks):
            self.update_progress(f"Expanding prompt i + 1 ...", 0)
            expansion = self.pipeline.final_expansion(task.task_prompt, task.task_seed)
            self.update_progress(f"[Prompt Expansion] {expansion}", 0)
            task.expansion = expansion
            task.positive_basic_workloads = copy.deepcopy(task.positive_basic_workloads) + [expansion]
        return tasks

    # OK
    def encode_prompts(self, tasks: List[config.TaskletObject]):
        """Encodes the prompts for each task."""
        
        i = 1
        for task in tasks:
            logger.info(f"Encoding positive {i + 1} ...")
            self.update_progress(f"Encoding positive #{i + 1} ...", 0)
            task.encoded_positive_cond = self.pipeline.clip_encode(texts=task.positive_basic_workloads, pool_top_k=task.positive_top_k)
            i += 1

        i = 1
        for task in tasks:
            if abs(float(self.generation_task.cfg_scale) - 1.0) < 1e-4:
                self.update_progress(f"Encoding negative #{i + 1} ...", 0)
                task.encoded_negative_cond = self.pipeline.clone_cond(task.encoded_positive_cond)
            else:
                self.update_progress(f"Encoding negative #{i + 1} ...", 0)
                task.encoded_negative_cond = self.pipeline.clip_encode(texts=task.negative_basic_workloads, pool_top_k=task.negative_top_k)
            i += 1

    # TODO? This one could be async, using its own pid etc to patch
    # OK
    def process_all_tasks(self):
        """Processes all tasks in the generation queue."""
        self.update_progress(f"Processing all tasks ...", 0)
        for task in self.generation_tasks:
            if not task.has_been_processed:
                self.process_single_task(task)
                task.has_been_processed = True
        self.update_progress(f"All tasks processed.", 0)


    # OK
    def prepare_task_for_processing(self, task: config.ImageGenerationObject):
        """Processes a single task from the generation queue."""
        self.preparation_start_time = time.perf_counter()
        self.initialize_current_task(task)

        apply_patch_settings(self.pid, task)
        if task.input_image:
             self.prepare_image_inputs()

        self.pipeline.refresh_controlnets([self.controlnet_pyracanny_path, self.controlnet_cpds_path])
        self.ip_adapter.load_ip_adapter(self.clip_vision_path, self.ip_negative_path, self.ip_adapter_path)
        self.ip_adapter.load_ip_adapter(self.clip_vision_path, self.ip_negative_path, self.ip_adapter_face_path)

        overrides: config.Overrides = self.get_overrides(task.steps, task.height, task.width)

        task.steps = overrides.steps
        task.refiner_switch = overrides.switch
        task.width = overrides.width
        task.height = overrides.height

        if not self.skip_prompt_processing:
            self.process_prompt()

        self.update_progress(f'[Parameters] Sampler = {task.sampler_name} - {task.scheduler_name}', 0)
        self.update_progress(f'[Parameters] Steps = {task.steps} - {task.refiner_switch}', 0)

        if 'vary' in self.goals:
            self.apply_vary()

        if 'upscale' in self.goals:
            (
                direct_return,
                task.uov_input_image,
                self.denoising_strength,
                initial_latent,
                tiled,
                width,
                height,
            ) = self.apply_upscale()
            if direct_return:
                d = [('Upscale (Fast)', 'upscale_fast', '2x')]
                # TODO: Ensure log works
                # self.uov_input_image_path = log(task.uov_input_image, d, output_format=task.output_format)
                self.yield_result([task.uov_input_image])
                return

        if 'inpaint' in self.goals:
            self.update_progress("NOT IMPLEMENTED YET", 0)
            """ (denoising_strength, 
             initial_latent, 
             width, 
             height, 
             current_progress) = apply_inpaint() """

        if 'cn' in self.goals:
            self.apply_control_nets()
            if task.developer_options.debugging_cn_preprocessor:
                return

        self.patch_freeu_to_core()

        second_overrides: config.Overrides = self.get_overrides(task.steps, task.height, task.width)
        task.steps = second_overrides.steps
        self.all_steps = second_overrides.steps * task.image_number

        images_to_enhance = []
        if 'enhance' in self.goals:
            task.image_number = 1
            images_to_enhance += [task.enhance_input_image]
            task.height, task.width, _ = task.enhance_input_image.shape
            # input image already provided, processing is skipped
            self.generation_task.steps = 0
            self.yield_result([self.generation_task.enhance_input_image])

        if task.enhance_task:
            enhance_ctrl = task.enhance_task
            enhance_upscale_steps = self.generation_task.performance_selection.steps()
            if 'upscale' in enhance_ctrl.enhance_uov_method:
                if 'fast' in enhance_ctrl.enhance_uov_method:
                    enhance_upscale_steps = 0
                else:
                    enhance_upscale_steps = task.performance_selection.steps_uov()
            enhance_upscale_overrides = self.get_overrides(enhance_upscale_steps, task.width, task.height)

            enhance_upscale_steps_total = task.image_number * enhance_upscale_overrides.steps
            self.all_steps += enhance_upscale_steps_total

        # if task.enhance_task:
        # enhance_overrides = self.task.get_overrides()
        # TODO Get lenght of overwrite params inside OverWriteControls
        # task.all_steps = self.generation_task.image_number * len(task.enhance_task) * enhance_overrides.steps

        self.all_steps = max(1, self.all_steps)

        self.update_progress(f"Denosing strength: {self.denoising_strength}")
        self.update_progress(f"Steps: {task.steps}", 0)

        if self.initial_latent:
            log_shape = initial_latent['samples'].shape
        else:
            log_shape = f'Image Space {(task.height, task.width)}'

        self.update_progress(f'[Parameters] Initial Latent shape: {log_shape}', 0)

        preparation_time = time.perf_counter() - self.preparation_start_time
        print(f'Preparation time: {preparation_time:.2f} seconds')

        return True

    # OK
    def patch_freeu_to_core(self):
        if not self.generation_task.freeu_controls:
            return
        self.update_progress(f"FreeU is enabled!", 0)
        self.pipeline.final_unet = apply_freeu(
            self.pipeline.final_unet,
            self.generation_task.freeu_controls.freeu_b1,
            self.generation_task.freeu_controls.freeu_b2,
            self.generation_task.freeu_controls.freeu_s1,
            self.generation_task.freeu_controls.freeu_s2,
        )

    def process_single_task(self, task):
        self.prepare_task_for_processing(task)
        task: config.ImageGenerationObject = self.generation_task 
        try:
            self.processing = False
            for tasklet in self.tasks:
                imgs, img_paths =  self.process_tasklet(tasklet)
                self.update_progress(f"Tasklet processed.", 0)
                self.update_progress(f"[{tasklet}, {imgs}, {img_paths}]", 0)

            #self.generate_image_wall_if_needed(task)
            self.yields.append(["finish", self.results, task.uid])
            self.pipeline.prepare_text_encoder(async_call=True)
        except Exception as e:
            self.update_progress(f"Error processing task: {e}", 0)
            traceback.print_exc()
            self.yields.append(["finish", self.results])
        finally:
            self.cleanup_after_task()

    def generate_image_wall_if_needed(self, task):
        """Generates an image wall if the task requires it."""
        """ if task.developer_options.generate_grid and len(self.results) > 2:
            wall = build_image_wall(task.results)
            task.results.append(wall) """
        
        raise NotImplementedError("generate_image_wall_if_needed is not implemented yet.")

    # OK
    def cleanup_after_task(self):
        """Cleans up after processing a task."""
        if self.pid in patch_settings_GLOBAL_CAUTION:
            del patch_settings_GLOBAL_CAUTION[self.pid]
    pass

    """ def start_worker_thread(self):
        "Starts the worker thread."
        threading.Thread(target=WHAT HERE?, daemon=True).start() """

    def worker(self):
        """Placeholder for the worker function."""
        # Implement the worker logic here
        pass

    def stop_processing(self):
        """Stops the processing of the current task."""
        if self.processing:
            self.interrupt_if_needed()
            self.cleanup_after_task()
            self.processing = False

    # OK
    def update_progress(self, status: str = None, step: int = 1):
        """ self.current_progress += 1
        percentage = self.current_progress / self.total_progress * 100
        # Inspiration for a print that overwrites itself
        #   sys.stdout.write('\r')
        #   sys.stdout.write("[%-20s] %d%%" % ('='*i, 5*i))
        #   sys.stdout.flush()
        percentage = int(percentage)
        sys.stdout.write("\r")
        sys.stdout.write(f"[{'=' * percentage}{' ' * (100 - percentage)}] {percentage}%")
        sys.stdout.flush() """

        bar_max_length = 100
        
        self.current_progress += step
        percentage = self.current_progress / self.total_progress * 100
        percentage = percentage/10
        percentage = int(percentage)

        # Clear the previous output
        sys.stdout.write("\033[F")  # Move cursor up one line
        sys.stdout.write("\033[K")  # Clear the line 

        # Move the old status upwards
        sys.stdout.write("\033[A")
        
        # Print the status
        if status:
            sys.stdout.write(f"Status: {status}\n")

        # Print the progress bar

        sys.stdout.write(f"[{'=' * percentage}{' ' * (10 - percentage)}] {percentage}%\n")
        sys.stdout.flush() # This is needed to actually print the status

    # TODO
    # Start the worker thread? How to implement?
    # start_worker_thread()

    # OK
    def prepare_image_inputs(self):
        ip_mode = self.generation_task.image_input_mode
        inpaint_options = self.generation_task.inpaint_options
        task: config.ImageGenerationObject = self.generation_task

        # TODO Move to it's own object, setup funcs
        if ip_mode == flags.INPUT_IMAGE_MODES_CLASS.uov or ip_mode == flags.INPUT_IMAGE_MODES_CLASS.ip \
        and task.mix_image_prompt_and_vary_upscale:            

            self.prepare_upscale() # TODO

            _inpaint_image = task.input_image['image']
            _inpaint_image = ensure_three_channels(_inpaint_image)

            _inpaint_mask = task.input_image['mask'][:,:, 0]

        if ip_mode == flags.INPUT_IMAGE_MODES_CLASS.inpaint or \
            ip_mode == flags.INPUT_IMAGE_MODES_CLASS.ip and task.mix_image_prompt_and_inpaint:

            if inpaint_options.use_advanced_inpaint_masking:
                _prepared_input_mask_image = np.maximum(
                    self.generation_task.input_mask_image['image'],
                    self.generation_task.input_mask_image['mask'])
                # if isinstance(self.generation_task.prepared_inpaint_mask_image_upload, np.ndarray) and self.generation_task.inpaint_mask_image_upload.ndim == 3:
                height, width, _channels = _prepared_input_mask_image.shape                
                _prepared_input_mask_image = resample_image(
                    _prepared_input_mask_image, width, height)

                _prepared_input_mask_image = np.mean(_prepared_input_mask_image, axis=2) 
                # TODO Magic numbers...
                _prepared_input_mask_image = (
                    _prepared_input_mask_image > 127).astype(np.uint8) * 255

                self.prepared_inpaint_mask = np.maximum(_inpaint_mask, _prepared_input_mask_image)

            if inpaint_options.inpaint_erode_or_dilate:
                self.prepared_inpaint_mask = erode_or_dilate(_inpaint_mask, inpaint_options.inpaint_erode_or_dilate)

            if inpaint_options.invert_mask:
                self.prepared_inpaint_mask = 255 - _inpaint_mask

            if isinstance(_inpaint_image, np.ndarray) and isinstance(_inpaint_mask, np.ndarray) \
                    and (np.any(_inpaint_mask > 127) or len(inpaint_options.outpaint_selections) > 0):

                self.upscale_model_path = UpscaleModel.download_model()
                if inpaint_options.inpaint_engine_version:
                    self.update_progress('Downloading inpainter ...', 0)
                    self.inpaint_head_model_path = InpaintModelFiles.InpaintHead.download_model()
                    self.inpaint_patch_model_path = InpaintModelFiles.download_based_on_version(inpaint_options.inpaint_engine_version)
                    self.base_model_additional_loras += [(self.inpaint_patch_model_path, 1.0)]
                    self.update_progress(f'[Inpaint] Current inpaint model is {self.inpaint_patch_model_path}', 0)

                    if self.generation_task.refiner_model:
                        self.use_synthetic_refiner = True
                        self.generation_task.refiner_switch = 0.8
                else:
                    self.inpaint_head_model_path, self.inpaint_patch_model_path = None, None
                    self.update_progress(f'[Inpaint] Parameterized inpaint is disabled.', 0)
                if inpaint_options.inpaint_additional_prompt:
                    if not self.generation_task.prompt:
                        self.generation_task.prompt = inpaint_options.inpaint_additional_prompt
                    else:
                        self.generation_task.prompt = inpaint_options.inpaint_additional_prompt + '\n' + self.generation_task.prompt
                self.goals.append('inpaint')

        if self.generation_task.image_input_mode == flags.INPUT_IMAGE_MODES_CLASS.ip or \
                self.generation_task.mix_image_prompt_and_vary_upscale or \
                self.generation_task.mix_image_prompt_and_inpaint:
            self.goals.append('cn')
            self.update_progress('Downloading control models ...', 0)
            self.update_controlnet_models()

        if self.generation_task.image_input_mode == 'enhance' and self.generation_task.enhance_input_image:
            self.update_progress('Getting input image for enhancement ...', 0)
            self.goals.append('enhance')
            self.skip_prompt_processing = True
            self.generation_task.enhance_input_image = ensure_three_channels(self.generation_task.input_image['image'])
        return True
    # OK
    def set_steps(self):
        task: config.ImageGenerationObject = self.generation_task
        perf_name = task.performance_selection.name
        task.steps = task.steps if task.steps != -1 else Steps[perf_name].value
        self.original_steps = self.original_steps if self.original_steps != -1 else task.steps
    # OK
    def check_refiner_not_same_as_base_model(self):
        task: config.ImageGenerationObject = self.generation_task
        if task.base_model_name == task.refiner_model:
            task.refiner_model = None
    # OK
    def get_overrides(self, steps: int, height: int, width: int) -> Overrides:
        task: config.ImageGenerationObject = self.generation_task
        overrides = task.overwrite_controls
        if not overrides:
            return Overrides(
                steps=steps, 
                switch=task.refiner_switch, 
                width=width, 
                height=height
                )

        if overrides.overwrite_step > 0:
            steps = overrides.overwrite_step
        switch = int(round(steps * task.refiner_switch))
        if overrides.overwrite_switch > 0:
            switch = overrides.overwrite_switch
        if overrides.overwrite_width > 0:
            width = overrides.overwrite_width
        if overrides.overwrite_height > 0:
            height = overrides.overwrite_height

        return_obj = Overrides(
            steps=steps,
            switch=switch,
            width=width,
            height=height,
        )
        return return_obj
    # OK
    def get_defaults_per_performance(self):
        task: config.ImageGenerationObject = self.generation_task
        if task.refiner_model:
            print(f"Refiner disabled in {task.performance_selection.name} mode.")
        match task.performance_selection:
            case Performance.HYPER_SD:
                self._set_hyper_sd_defaults()
            case Performance.LIGHTNING:
                self._set_lightning_defaults()
            case Performance.EXTREME_SPEED:
                self._set_lcm_defaults()  
    # OK
    def _set_hyper_sd_defaults(self):
        task: config.ImageGenerationObject = self.generation_task
        task.performance_loras += [(SDXL_HyperSDLoRA.download_model(), 0.8)]
        task.refiner_model = None
        task.sampler_name = "dpmpp_sde_gpu"
        task.scheduler_name = "karras"
        task.sample_sharpness = 0.0
        task.cfg_scale = 1.0
        task.adaptive_cfg = 1.0
        task.refiner_switch = 1.0
        task.adm_scaler_positive = 1.0
        task.adm_scaler_negative = 1.0
        task.adm_scaler_end = 0.0
        return
    # OK
    def _set_lightning_defaults(self):
        task: config.ImageGenerationObject = self.generation_task
        print("Enter Lightning mode.")
        task.performance_loras += [SDXL_LightningLoRA.download_model(), 1.0]
        task.refiner_model = None
        task.sampler_name = "euler"
        task.scheduler_name = "sgm_uniform"
        task.sample_sharpness = 0.0
        task.cfg_scale = 1.0
        task.adaptive_cfg = 1.0
        task.refiner_switch = 1.0
        task.adm_scaler_positive = 1.0
        task.adm_scaler_negative = 1.0
        task.adm_scaler_end = 0.0
        return
    # OK
    def _set_lcm_defaults(self):
        print("Enter LCM mode.")
        task: config.ImageGenerationObject = self.generation_task
        task.performance_loras += [
            (True, SDXL_LCM_LoRA.download_model(), 1.0)
        ]
        task.refiner_model = None
        task.sampler_name = "lcm"
        task.scheduler_name = "lcm"
        task.sample_sharpness = 0.0
        task.cfg_scale = 1.0
        task.adaptive_cfg = 1.0
        task.refiner_switch = 1.0
        task.adm_scaler_positive = 1.0
        task.adm_scaler_negative = 1.0
        task.adm_scaler_end = 0.0
    # OK
    def prepare_attributes(self):
        task: config.ImageGenerationObject = self.generation_task
        if task.inpaint_options:
            task.inpaint_options.outpaint_selections = [o.lower() for o in task.inpaint_options.outpaint_selections]
        if task.uov_method:
            task.uov_method = task.uov_method.lower()

        if task.enhance_task:
            task.enhance_task.enhance_uov_method = task.enhance_task.enhance_uov_method.lower()
        if fooocus_expansion in task.styles:
            self.use_prompt_expansion = True 
            task.styles.remove(fooocus_expansion)
        self.use_styles = len(task.styles) > 0

        task.aspect_ratio = task.aspect_ratio.split('*')
        task.aspect_ratio = [int(x) for x in task.aspect_ratio]

        task.width, task.height = task.aspect_ratio
    # OK
    def update_controlnet_models(self):
        task: config.ImageGenerationObject = self.generation_task
        if task.controlnet_tasks:
            for controlnet_task in task.controlnet_tasks:
                self.update_progress(f'Downloading controlnet model for {controlnet_task.name} ...', 0)
                for model in controlnet_task.models:
                    model.download_model()
                    self.controlnet_pyracanny_path = PyraCanny.full_path()
                    self.controlnet_cpds_path = CPDS.full_path()
                    self.clip_vision_path = ImagePromptClipVIsion.full_path()
                    self.ip_negative_path = ImagePromptAdapterNegative.full_path()
                    self.ip_adapter_path = ImagePromptAdapterPlus.full_path()
                    self.ip_adapter_face_path = ImagePromptAdapterFace.full_path()

    def apply_vary(self):
        task: config.ImageGenerationObject = self.generation_task

        if 'subtle' in task.uov_method:
            self.denoising_strength = 0.5
        if 'strong' in task.uov_method:
            self.denoising_strength = 0.85
        if task.overwrite_controls.overwrite_vary_strength > 0:
            denoising_strength = task.overwrite_controls.overwrite_vary_strength

        shape_ceil = get_image_shape_ceil(uov_input_image)
        if shape_ceil < 1024:
            self.update_progress(f'[Vary] Image is resized because it is too small.', 0)
            shape_ceil = 1024
        elif shape_ceil > 2048:
            self.update_progress(f'[Vary] Image is resized because it is too big.', 0)
            shape_ceil = 2048
        uov_input_image = set_image_shape_ceil(uov_input_image, shape_ceil)
        initial_pixels = numpy_to_pytorch(uov_input_image)

        self.update_progress('VAE encoding ...')

        candidate_vae, _ = self.pipeline.get_candidate_vae(
                steps=task.steps,
                switch=task.refiner_switch,
                denoise=denoising_strength,
                refiner_swap_method=task.refiner_swap_method
            )
        initial_latent = encode_vae(vae=candidate_vae, pixels=initial_pixels)
        B, C, H, W = initial_latent['samples'].shape
        width = W * 8
        height = H * 8
        self.update_progress(f'Final resolution is {str((width, height))}.', 0)

        task.uov_input_image = uov_input_image
        self.denoising_strength = denoising_strength
        self.initial_latent = initial_latent
        task.width = width
        task.height = height

        self.cleanup_bowl.append(uov_input_image)
        self.cleanup_bowl.append(initial_latent)

        return True

    def apply_upscale(self):
        task: config.ImageGenerationObject = self.generation_task
        H, W, C = task.uov_input_image.shape
        self.update_progress(f"Upscaling image from {str((W, H))}...")
        uov_input_image = perform_upscale(uov_input_image)
        self.update_progress(f'Image upscaled.', 0)
        if '1.5x' in task.uov_method:
            f = 1.5
        elif '2x' in task.uov_method:
            f = 2.0
        else:
            f = 1.0
        shape_ceil = get_shape_ceil(H * f, W * f)
        if shape_ceil < 1024:
            self.update_progress(f'[Upscale] Image is resized because it is too small.', 0)
            uov_input_image = set_image_shape_ceil(uov_input_image, 1024)
            shape_ceil = 1024
        else:
            uov_input_image = resample_image(uov_input_image, width=W * f, height=H * f)
        image_is_super_large = shape_ceil > 2800
        if 'fast' in task.uov_method:
            direct_return = True
        elif image_is_super_large:
            logger.info('Image is too large. Directly returned the SR image. '
                    'Usually directly return SR image at 4K resolution '
                    'yields better results than SDXL diffusion.')
            direct_return = True
        else:
            direct_return = False
        if direct_return:
            return (
                direct_return,
                uov_input_image,
                None,
                None,
                None,
                None,
                None,
            )

        tiled = True
        denoising_strength = 0.382
        if task.overwrite_controls.overwrite_upscale_strength > 0:
            denoising_strength = task.overwrite_controls.overwrite_upscale_strength
        initial_pixels = numpy_to_pytorch(uov_input_image)
        self.update_progress('VAE encoding ...')
        candidate_vae, _ = self.pipeline.get_candidate_vae(
                steps=task.steps,
                switch=task.refiner_switch,
                denoise=denoising_strength,
                refiner_swap_method=task.refiner_swap_method
            )
        initial_latent = encode_vae(
                vae=candidate_vae,
                pixels=initial_pixels, tiled=True)
        B, C, H, W = initial_latent['samples'].shape
        self.cleanup_bowl.append(initial_latent)
        width = W * 8
        height = H * 8
        self.update_progress(f'Final resolution is {str((width, height))}.', 0)
        return (
            direct_return,
            uov_input_image,
            denoising_strength,
            initial_latent,
            tiled,
            width,
            height,
        )

    def apply_control_nets(self):
        task: config.ImageGenerationObject = self.generation_task
        debug_cn = task.developer_options.debugging_cn_preprocessor
        skip_cn = task.developer_options.skipping_cn_preprocessor
        for cn_task in [_cn_task for _cn_task in task.controlnet_tasks if _cn_task.name.lower() == 'pyracanny']:
            cn_img = resize_image(
                ensure_three_channels(cn_task.img), width=task.width, height=task.height
            )

            if not skip_cn:
                cn_img = preprocessors.canny_pyramid(
                    cn_img,
                    task.canny_low_threshold,
                    task.canny_high_threshold)

            cn_img = ensure_three_channels(cn_img)
            cn_task.img = numpy_to_pytorch(cn_img)
            if task.developer_options.debugging_cn_preprocessor:
                self.yield_result(cn_img, do_not_show_finished_images=True)

        for cn_task in [_cn_task for _cn_task in task.controlnet_tasks if _cn_task.name.lower() == 'cpds']:
            cn_img = resize_image(ensure_three_channels(cn_task.img), width=task.width, height=task.height)

            if not skip_cn:
                cn_img = preprocessors.cpds(cn_img)

            cn_img = ensure_three_channels(cn_img)
            cn_task.img = numpy_to_pytorch(cn_img)

            if debug_cn:
                self.update_progress('ControlNet: CPDS')
                self.yield_result(cn_img, do_not_show_finished_images=True)
        for cn_task_ip in [cn_task for cn_task in task.controlnet_tasks if cn_task.name.lower() == 'ip']:
            cn_img = ensure_three_channels(cn_task_ip.img)

            # https://github.com/tencent-ailab/IP-Adapter/blob/d580c50a291566bbf9fc7ac0f760506607297e6d/README.md?plain=1#L75
            cn_img = resize_image(cn_img, width=224, height=224, resize_mode=0)

            cn_task.ip_conds, cn_task.ip_unconds = self.ip_adapter.preprocess(cn_img, ip_adapter_path=self.ip_adapter_path)
            if debug_cn:
                self.update_progress('ControlNet: IP')
                self.yield_result(cn_img, do_not_show_finished_images=True)

        for cn_task in [cn_task for cn_task in task.controlnet_tasks if cn_task.name.lower() == 'ip_face']:
            cn_img = ensure_three_channels(cn_task.img)

            if not skip_cn:
                cn_img = face_crop.crop_image(cn_img)

            # https://github.com/tencent-ailab/IP-Adapter/blob/d580c50a291566bbf9fc7ac0f760506607297e6d/README.md?plain=1#L75
            cn_img = resize_image(cn_img, width=224, height=224, resize_mode=0)

            cn_task.ip_conds, cn_task.ip_unconds = self.ip_adapter.preprocess(cn_img, ip_adapter_path=self.ip_adapter_face_path)

            if debug_cn:
                self.yield_result(cn_img, do_not_show_finished_images=True)

        # Image prompt and image prompt face
        all_ip_tasks = [
            cn_task for cn_task in task.controlnet_tasks if cn_task.name.lower() == "ip"
        ] + [
            cn_task
            for cn_task in task.controlnet_tasks
            if cn_task.name.lower() == "ip_face"
        ]
        
        if len(all_ip_tasks) > 0:
            self.pipeline.final_unet = ip_adapter.patch_model(self.pipeline.final_unet, all_ip_tasks)
    
    # OK
    def patch_samplers(self):
        task: config.ImageGenerationObject = self.generation_task
        
        def _patch_discrete(unet, scheduler_name):
            return opModelSamplingDiscrete.patch(unet, scheduler_name, False)[0]

        def _patch_edm(unet, scheduler_name):
            return opModelSamplingContinuousEDM.patch(
                unet, scheduler_name, 120.0, 0.002)[0]
        
        if task.scheduler_name in ["lcm", "tcd"]:
            final_scheduler_name = "sgm_uniform"
            if self.pipeline.final_unet is not None:
                self.pipeline.final_unet = _patch_discrete(
                    self.pipeline.final_unet, task.scheduler_name
                )
            if self.pipeline.final_refiner_unet is not None:
                self.pipeline.final_refiner_unet = _patch_discrete(
                    self.pipeline.final_refiner_unet, task.scheduler_name
                )

        elif task.scheduler_name == "edm_playground_v2.5":
            final_scheduler_name = "karras"
            if self.pipeline.final_unet is not None:
                self.pipeline.final_unet = _patch_edm(
                    self.pipeline.final_unet, task.scheduler_name
                )

            if self.pipeline.final_refiner_unet is not None:
                self.pipeline.final_refiner_unet = _patch_edm(
                    self.pipeline.final_refiner_unet, task.scheduler_name
                )

        else:
            final_scheduler_name = task.scheduler_name


        return final_scheduler_name

# UTILS

def save_images(imgs: List[np.ndarray], output_format: str, output_folder_path: str = "outputs"):
    """Saves images to disk
    
    Args:
        imgs (List[np.ndarray]): List of images to save
        output_format (str): Output format for the images
        output_folder_path (str, optional): Output folder path. Defaults to "outputs".

    Returns:
        True (bool): True if the images were saved successfully

    
    """
    if "." in output_folder_path:
        raise ValueError("Invalid output folder path. Did you mean to provide a folder name instead of a file path?")
    
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    paths = []
    for img in imgs:
        save_path = os.path.join(output_folder_path, f"{get_filename_string()}.{output_format}")
        paths.append(save_path)
        PIL.Image.fromarray(img).save(save_path)
    
    return paths


def get_filename_string():
    """Returns a string with the current date and time."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
