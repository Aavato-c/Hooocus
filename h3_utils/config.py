import os
import sys

from h3_utils.model_file_config import controlnet_task_by_name



sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from pydantic_core import from_json
from torch import Tensor

from modules.model_file_utils.model_loader import load_file_from_url
from h3_utils.path_configs import FolderPathsConfig


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random

import numpy

from h3_utils.flags import DESCRIBE_TYPE_PHOTO, ENHANCEMENT_UOV_PROMPT_TYPE_ORIGINAL, KSAMPLER, KSAMPLER_NAMES, KSAMPLER_NAMES_LIT, OUTPUTFORMAT_LIT, REFINER_SWAP_METHODS, SCHEDULER_NAMES_CLS, SCHEDULER_NAMES_LITERAL, SDXL_ASPECT_RATIOS, SDXL_ASPECT_RATIOS_CLASS, UPSCALE_OR_VARIATION_MODES, Overrides, Steps

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PARENT_DIR)

import json
import tempfile
from typing import Any, Dict, List, Literal, Optional, Tuple, Iterable, TypeAlias, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from numpy.typing import NDArray

from h3_utils.logging_util import LoggingUtil
from h3_utils.flags import EXAMPLE_ENHANCE_DETECTION_PROMPTS, INPAINT_MASK_CLOTH_CATEGORY, INPUT_IMAGE_MODES, KSAMPLER, OUTPAINT_SELECTIONS, REFINER_SWAP_METHODS, SDXL_ASPECT_RATIOS, UPSCALE_OR_VARIATION_MODES, OutputFormat, Performance, ENHANCEMENT_UOV_BEFORE
from h3_utils.launch_args import METADATA_SCHEME, LAUNCH_ARGS
import traceback

log = LoggingUtil(__name__).get_logger()
log.debug("Loading config.py")
log.debug(f"Traceback: {traceback.format_stack()}")

preset_chosen: str = "default" # Modify this to change the preset
current_preset = {}
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'outputs')
CustomNDArrayType: TypeAlias = Union[NDArray, List[NDArray]]

try:
    with open(f"{PARENT_DIR}/presets/default.json", "r") as f:
        DEFAULT_PRESET = json.load(f)
        log.debug("Default preset loaded.")
except FileNotFoundError:
    raise FileNotFoundError("Could not find default preset file. Exiting.")


try:
    with open(f"{PARENT_DIR}/presets/{preset_chosen.lower()}.json", "r") as f:
        log.debug(f"Loading preset file for {preset_chosen}.")
        current_preset = json.load(f)
except FileNotFoundError:
    log.error(f"Could not find preset file for {preset_chosen}. Using default preset.")
    current_preset = DEFAULT_PRESET


class FilePathConfig:
    config_path = 'h3_utils/config.json'
    hash_cache_path = f'{PARENT_DIR}/__cache__/hash_cache.json'
    auth_filename = 'auth.json'

class FreeUControls(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    freeu_b1: float = Field(1.01, le=2.0, ge=0.0)
    freeu_b2: float = Field(1.02, le=2.0, ge=0.0)
    freeu_s1: float = Field(0.99, le=2.0, ge=0.0)
    freeu_s2: float = Field(0.95, le=2.0, ge=0.0)

class OverWriteControls(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    overwrite_height: int = -1
    overwrite_step: int = -1
    overwrite_switch: int = -1
    overwrite_upscale_strength: float = -1
    overwrite_upscale: float = -1
    overwrite_vary_strength: float = -1
    overwrite_width: int = -1

class DeveloperOptions(BaseModel):

    class Config:
        arbitrary_types_allowed = True
     # ?
    metadata_created_by: str = Field("", description="The metadata created by to use.")
    metadata_scheme: str = Field(METADATA_SCHEME, description="The default metadata scheme to use.")
    debugging_cn_preprocessor: bool = False
    debugging_dino: bool = False
    debugging_enhance_masks_checkbox: bool = False
    debugging_inpaint_preprocessor: bool = False
    temp_path_cleanup_on_launch: bool = Field(True, description="The temp path cleanup on launch to use.")
    temp_path: str = Field(os.path.join(tempfile.gettempdir(), 'hooocus'), description="The default temp path to use.")
    disable_intermediate_results: bool = False
    disable_seed_increment: bool = False
    generate_grid: bool = False
    disable_preview: bool = False
    skipping_cn_preprocessor: bool = False
    should_use_advanced: bool = Field(False, description="Bool: should use advanced checkbox?")
    should_use_developer_debug_mode: bool = Field(False, description="Bool: default developer debug mode.")

class InptaintOptions(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    inpaint_worker_current_task: Optional[Any] = None
    outpaint_selections: Optional[OUTPAINT_SELECTIONS] = None
    invert_mask: bool = False
    inpaint_mask_model: str = Field('isnet-general-use', description="The default invert mask model to use.")
    inpaint_additional_prompt: Optional[str] = None
    inpaint_disable_initial_latent: bool = False
    inpaint_engine_version: str = Field("v2.6", description="The default inpaint engine version to use.")
    inpaint_erode_or_dilate: Optional[int] = Field(None, le=64, ge=-64)
    inpaint_mask_cloth_category: str = Field('full', description="The default inpaint mask cloth category to use.")
    inpaint_mask_sam_model: str = Field('vit_b', description="The default inpaint mask sam model to use.")
    inpaint_method: str = Field("Inpaint or Outpaint (default)", description="The default inpaint method to use.")
    inpaint_respective_field: float = 0.618 # min 0.0 max 1.0
    use_advanced_inpaint_masking: bool = Field(False, description="Bool: should use advanced inpaint masking?")
    inpaint_should_use_inpaint_image: bool = False
    inpaint_should_use_mask: bool = False
    inpaint_stop_ats: List[float] = Field([0.5, 0.5, 0.5, 0.5], description="The default inpaint stop ats to use.")
    inpaint_strength: float = 1.0 # min 0.0 max 1.0

class EnhanceMaskCtrls(BaseModel):
    """
    Enhacement mask controls for inpaint and outpaint
    
    """
    class Config:
        arbitrary_types_allowed = True

    enhance_tabs: int = Field(3, description="The default enhance tabs to use.")
    enhance_mask_dino_prompt_text: str = EXAMPLE_ENHANCE_DETECTION_PROMPTS[0]
    
    enhance_prompt: str = None # Enhacement positive prompt. Uses original prompt if None
    enhance_negative_prompt: str = None # Enhacement negative prompt. Uses original negative prompt if None
    
    enhance_inpaint_mask_model: str = Field('sam', description="The default enhance inpaint mask model to use.")
    enhance_mask_cloth_category: INPAINT_MASK_CLOTH_CATEGORY = 'full'
    
    enhance_mask_sam_model: str = Field('vit_b', description="The default inpaint mask sam model to use.")
    
    enhance_mask_text_threshold: float = Field(0.25, description="The default enhance mask text threshold to use.", ge=0.0, le=1.0)
    enhance_mask_box_threshold: float = Field(0.30, description="The default enhance mask box threshold to use.", ge=0.0, le=1.0)
    enhance_mask_sam_max_detections: int = Field(0, description="The default enhance mask sam max detections to use.", ge=0, le=10)
    
    enhance_inpaint_disable_initial_latent: bool = False
    enhance_inpaint_engine: str = Field("2.6", description="The default enhance inpaint engine version to use.")
        
    enhance_inpaint_strength: float = Field(1.0, description="The default enhance inpaint strength to use.", ge=0.0, le=1.0)
    enhance_inpaint_respective_field: float = Field(0.618, description="The default enhance inpaint respective field to use.", ge=0.0, le=1.0)
    enhance_inpaint_erode_or_dilate: int = Field(0, description="The default enhance inpaint erode or dilate to use.", ge=-64, le=64)
    enhance_mask_inver: bool = False

    enhance_uov_method: Optional[UPSCALE_OR_VARIATION_MODES] = Field(None, description="Enhacement uov method")
    enhance_uov_method: Optional[str] = Field(None, description="The default enhance uov method to use.")
    enhance_uov_processing_order: int = Field(ENHANCEMENT_UOV_BEFORE, description="The default enhance uov processing order to use.")
    enhance_uov_prompt_type: int = Field(ENHANCEMENT_UOV_PROMPT_TYPE_ORIGINAL, description="The default enhance uov prompt type to use.")

class LambdaStyle(BaseModel):
    name: str
    prompt: str
    negative_prompt: str



class BaseControlNetTaskForRequests(BaseModel):

    stop: float = Field(0.5, ge=0, le=1)
    img: Optional[Any] = None
    image_url: Optional[str] = None
    weight: float = Field(1.0, ge=0, le=1)
    name: str = Field(None, description="Name of the ControlNetTask.")
    
    # Not used in requests
    ip_conds: Optional[Any] = None
    ip_unconds: Optional[Any] = None
    all_models: Optional[List[dict | object]] = None
    paths_of_models: Optional[List[str]] = None


class _InitialImageGenerationParams(BaseModel):
    class Config:
        arbitrary_types_allowed = True


    uid: str = Field("", description="The default uid to use.")
    has_been_processed: bool = False

    negative_prompt: str = Field("", description="The default negative prompt to use.")
    prompt: Optional[str] = Field(None, description="The default prompt to use.")
    read_wildcards_in_order: bool = False

    width: Optional[int] = Field(None, description="The default width to use.")
    height: Optional[int] = Field(None, description="The default height to use.")

    sample_sharpness: float = Field(2.0, description="The default sample sharpness to use.", ge=0.0, le=30.0)
    seed: int = 0
    sampler_name: KSAMPLER_NAMES_LIT = KSAMPLER.dpmpp_2m_sde_gpu.name
    scheduler_name: SCHEDULER_NAMES_LITERAL = SCHEDULER_NAMES_CLS.karras

    base_model_name: str = Field("juggernautXL_v8Rundiffusion.safetensors", description="The default model to use.", alias="model")
    refiner_model: str | bool = Field(False, description="The default refiner model to use.", )
    refiner_switch: float = Field(0.5, description="Refiner switch", ge=0.0, le=1.0)
    refiner_swap_method: REFINER_SWAP_METHODS = "joint"
    loras: list = Field(
        [[True, "None", 1.0],
            [True, "None", 1.0],
            [True, "None", 1.0],
            [True, "None", 1.0],
            [True, "None", 1.0],],
        description="The default LoRAs to use.",)
    
    styles: List[str | LambdaStyle] = Field(["Fooocus V2", "Fooocus Sharp"], description="Style additions for prompts")
    additional_style_lamdas: List[LambdaStyle] = Field([], description="The default additional style lamdas to use.")
    seed: int = 0
    vae_name: str = Field("Default (model)", description="The default vae to use.")

    performance_selection: Performance = Performance.SPEED
    performance_loras: list = []

    # Format and save options
    output_format: OUTPUTFORMAT_LIT = Field(OutputFormat.WEBP, description="Output format")
    save_metadata_to_images: bool = Field(False, description="The default save metadata to images to use.")
    save_only_final_enhanced_image: bool = Field(False, description="The default save only final enhanced image to use.")
    aspect_ratio: SDXL_ASPECT_RATIOS = Field(SDXL_ASPECT_RATIOS_CLASS.PORTRAIT.R832_1152, description="The default aspect ratio to use.")
    image_number: int = Field(1, description="The default amount of images number to use.", ge=1)

    steps: int = Field(-1, description="The default steps to use.")
    original_steps: int = False

    adaptive_cfg: float = Field(7.0, description="The default cfg tsnr to use.", ge=1.0, le=30.0)
    cfg_scale: float = Field(4.0, description="Higher value means style is cleaner, vivider, and more artistic.", ge=1.0, le=30.0)
    cfg_tsnr: float = Field(7.0, description="The default cfg tsnr to use.")

    adm_scaler_end: float = Field(0.3, description="The default adm scaler end to use.", ge=0.0, le=1.0)
    adm_scaler_negative: float = Field(0.8, description="The default adm scaler negative to use.", ge=0.1, le=3.0)
    adm_scaler_positive: float = Field(1.5, description="The default adm scaler positive to use.", ge=0.1, le=3.0)

    canny_high_threshold: int = Field(128, description="The default canny high threshold to use.", ge=0, le=255)
    canny_low_threshold: int = Field(64, description="The default canny low threshold to use.", ge=0, le=255)

    checkpoint_downloads: dict[str, str] = Field(DEFAULT_PRESET["checkpoint_downloads"], description="The default checkpoint downloads to use.")
    vae_downloads: dict[str, str] = Field({}, description="The default vae downloads to use.")
    lora_downloads: dict[str, str] = Field({}, description="The default lora downloads to use.")
    embeddings_downloads: dict[str, str] = Field(DEFAULT_PRESET["embeddings_downloads"], description="The default embeddings downloads to use.")

    clip_skip: int = Field(2, description="The default clip skip to use.") # Where clip skip max?
    controlnet_softness: float = Field(0.25, description="The default controlnet softness to use.", ge=0.0, le=1.0)
    dino_erode_or_dilate: int = 0 # min -64 max 64

    enhance_task: Optional[EnhanceMaskCtrls] = None
    freeu_controls: Optional[FreeUControls] = None
    inpaint_options: Optional[InptaintOptions] = None
    controlnet_tasks: Optional[List[BaseControlNetTaskForRequests]] = []
    overwrite_controls: Optional[OverWriteControls] = None
    developer_options: Optional[DeveloperOptions] = DeveloperOptions()

    # should_describe_apply_prompts: bool = Field(True, description="The default describe apply prompts checkbox to use.")
    describe_content_type: Optional[List[str]] = Field([DESCRIBE_TYPE_PHOTO], description="The default describe content type to use.")

    use_image_prompt_advanced: bool = Field(False, description="Bool: should use image prompt advanced?")
    use_imageprompt: bool = False
    use_upscale_or_vary: bool = False
    mix_image_prompt_and_vary_upscale: bool = False
    mix_image_prompt_and_inpaint: bool = False

    image_input_mode: INPUT_IMAGE_MODES = Field("uov", description="The image input mode to use.") # utils.flags.input_image_tab_ids 

    input_image: Optional[Dict[Literal["image", "mask"], CustomNDArrayType]] = None
    input_image_url: Optional[str] = None
    uov_input_image: Optional[CustomNDArrayType] = None
    input_mask_image: Optional[Dict[Literal["image", "mask"], CustomNDArrayType]] = None
    prepared_input_mask_image: Optional[CustomNDArrayType] = None
    enhance_input_image: Optional[CustomNDArrayType] = None

    uov_method: Optional[UPSCALE_OR_VARIATION_MODES] = Field(None, description="The default uov method to use.")
    steps_uov: int = -1


class TaskletObject(BaseModel):
    """A tasklet object for the async worker.
    
    - It's a variation of a ImageGenerationObject 
    with additional fields for the pipeline.process_diffusion method.

    - So if you have an ImageGenerationObject with image_count=2,
    you will have 2 TaskletObjects with the same data but some
    variations for the pipeline.process_diffusion method.
    """
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


    uid: str
    task_seed: int 
    task_prompt: str
    task_negative_prompt: str
    positive_basic_workloads: Optional[List[str]] = []
    negative_basic_workloads: Optional[List[str]] = []
    expansion: str
    # [[torch.cat(cond_list, dim=1), {"pooled_output": pooled_acc}]]
    encoded_positive_cond: Optional[Tuple[Tensor, Dict[str, Tensor]]] = None
    encoded_negative_cond: Optional[Tuple[Tensor, Dict[str, Tensor]]] = None
    positive_top_k: int = 0
    negative_top_k: int = 0
    log_positive_prompt: str 
    log_negative_prompt: str
    styles: List[str]

class ApplyImageInputParams(BaseModel):
    base_model_additional_loras: List[str]
    clip_vision_path: str
    controlnet_canny_path: str
    controlnet_cpds_path: str
    inpaint_head_model_path: str
    inpaint_image: str
    inpaint_mask: str
    ip_adapter_face_path: str
    ip_adapter_path: str
    ip_negative_path: str
    skip_prompt_processing: bool
    use_synthetic_refiner: bool


yield_types = Literal['preview', 'result', 'waiting', 'uri', 'finish', 'starting']

class YieldObject(BaseModel):
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

    yield_type: yield_types
    progress: Optional[float] = None
    message: Optional[str] = None
    image: Optional[numpy.ndarray] = None
    uid: str

class ImageGenerationObject(_InitialImageGenerationParams):
    prepared_tasklets: Optional[TaskletObject] = None
    processing_time: Optional[float] = None
    
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True

    def init_style_lambdas(self):
        if len(self.additional_style_lamdas) > 0:
            self.styles.extend(self.additional_style_lamdas)

    def save_log_json(self):
        while os.path.exists(f"{PARENT_DIR}/logs/imagen_logs/{self.uid}.json"):
            self.uid = f"{self.uid}_1"
        
        try:
            with open(f"{PARENT_DIR}/logs/imagen_logs/{self.uid}.json", "w") as f:
                self.performance_selection = self.performance_selection.name
                json_model = self.model_dump()
                json.dump(json_model, f, indent=4, ensure_ascii=False)
        except Exception as e:
            if "serialization" in str(e):
                log.error("Could not serialize model.")

                for key, value in self.dict().items():
                    try:
                        json.dumps({key: value})
                    except Exception as e:
                        log.error(f"Could not serialize {key} with value {value}.")
                        # Delete the key
                        self.__delattr__(key)
                try:
                    self.save_log()
                except Exception as e:
                    log.error("Could not save log.")
            else:
                log.error(f"Could not save log: {e}")

    def save_log(self):
        try:
            self.performance_selection = self.performance_selection.name
            json_model = self.model_dump_json()
            if crud.update_imageorder_log(self.uid, json_model):
                log.info(f"Saved log for {self.uid}.")
            else:
                log.error(f"Could not save log for {self.uid}.")
                log.error(f"Model: {json_model}")
        except Exception as e:
            if "serialization" in str(e):
                log.error("Could not serialize model.")

                for key, value in self.dict().items():
                    try:
                        json.dumps({key: value})
                    except Exception as e:
                        log.error(f"Could not serialize {key} with value {value}.")
                        # Delete the key
                        self.__delattr__(key)
                try:
                    self.save_log()
                except Exception as e:
                    log.error("Could not save log.")
            else:
                log.error(f"Could not save log: {e}")


            

    def _prepare_downloads(self):
        self.checkpoint_downloads = self.checkpoint_downloads or DEFAULT_PRESET["checkpoint_downloads"]
        self.embeddings_downloads = self.embeddings_downloads or DEFAULT_PRESET["embeddings_downloads"]

        self.vae_downloads = {}

        for lora in self.loras:
            if lora[1] or lora[1] != "None":
                self.lora_downloads[lora[1]] = lora[1]

        if self.vae_name != "Default (model)" and self.vae_name != "":
            self.vae_downloads[self.vae_name] = self.vae_name




        
                




    
    def download_models(self):
        default_model = self.base_model_name
        from modules.util import get_file_from_folder_list

        vae_approx_filenames = [
                (
                    'xlvaeapp.pth',
                    'https://huggingface.co/lllyasviel/misc/resolve/main/xlvaeapp.pth'
                ),
                (
                    'vaeapp_sd15.pth',
                    'https://huggingface.co/lllyasviel/misc/resolve/main/vaeapp_sd15.pt'
                ),
                (
                    'xl-to-v1_interposer-v4.0.safetensors',
                    'https://huggingface.co/mashb1t/misc/resolve/main/xl-to-v1_interposer-v4.0.safetensors'
                )
        ]

        for file_name, url in vae_approx_filenames:
            load_file_from_url(url=url, model_dir=FolderPathsConfig.path_vae_approx, file_name=file_name)

        load_file_from_url(
            url='https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_expansion.bin',
            model_dir=FolderPathsConfig.path_fooocus_expansion,
            file_name='pytorch_model.bin'
        )

        load_file_from_url(
            url='https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_expansion.bin',
            model_dir=FolderPathsConfig.path_fooocus_expansion,
            file_name='pytorch_model.bin'
        )

        if LAUNCH_ARGS.disable_preset_download:
            log.info('Skipped model download.')
            return default_model, self.checkpoint_downloads


        """ if not LAUNCH_ARGS.always_download_new_model:
            if not os.path.isfile(get_file_from_folder_list(default_model, FolderPathsConfig.path_checkpoints)):
                for alternative_model_name in self.previous_default_models:
                    if os.path.isfile(get_file_from_folder_list(alternative_model_name, FolderPathsConfig.path_checkpoints)):
                        log.info(f'You do not have [{default_model}] but you have [{alternative_model_name}].')
                        log.info(f'Fooocus will use [{alternative_model_name}] to avoid downloading new models, '
                            f'but you are not using the latest models.')
                        log.info('Use --always-download-new-model to avoid fallback and always get new models.')
                        self.checkpoint_downloads = {}
                        default_model = alternative_model_name
                        break """


        #for file_name, url in checkpoint_downloads.items():
        for file_name, url in self.checkpoint_downloads.items():
            model_dir = os.path.dirname(get_file_from_folder_list(file_name, FolderPathsConfig.path_checkpoints))
            load_file_from_url(url=url, model_dir=model_dir, file_name=file_name)
        for file_name, url in self.embeddings_downloads.items():
            load_file_from_url(url=url, model_dir=FolderPathsConfig.path_embeddings, file_name=file_name)
        for file_name, url in self.lora_downloads.items():
            load_file_from_url(url="https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_offset_example-lora_1.0.safetensors", 
                               model_dir=FolderPathsConfig.path_loras, file_name='sd_xl_offset_example-lora_1.0.safetensors')
        for file_name, url in self.vae_downloads.items():
            load_file_from_url(url=url, model_dir=FolderPathsConfig.path_vae, file_name=file_name)

        return default_model, self.checkpoint_downloads



class ImageGenerationObjectForRequests(BaseModel):
    class Config:
        arbitrary_types_allowed = True


    uid: Optional[str] = ""
    has_been_processed: bool = False
    
    negative_prompt: str = Field("", description="The default negative prompt to use.")
    prompt: Optional[str] = Field(None, description="The default prompt to use.")
    read_wildcards_in_order: bool = False

    width: Optional[int] = Field(None, description="The default width to use.")
    height: Optional[int] = Field(None, description="The default height to use.")
    
    sample_sharpness: float = Field(2.0, description="The default sample sharpness to use.", ge=0.0, le=30.0)
    seed: int
    do_not_update_seed: bool = False
    sampler_name: KSAMPLER_NAMES_LIT = "dpmpp_2m_sde_gpu"
    scheduler_name: str = "karras"
    
    base_model_name: str = Field("juggernautXL_v8Rundiffusion.safetensors", description="The default model to use.", alias="model")
    refiner_model: str | bool = Field(False, description="The default refiner model to use.", )
    refiner_switch: float = Field(0.5, description="Refiner switch", ge=0.0, le=1.0)
    refiner_swap_method: REFINER_SWAP_METHODS = "joint"
    loras: list = Field([
        [
            True,
            "None",
            1.0
        ],
        [
            True,
            "None",
            1.0
        ],
        [
            True,
            "None",
            1.0
        ],
        [
            True,
            "None",
            1.0
        ],
        [
            True,
            "None",
            1.0
        ]
    ], description="The default LoRAs to use.")
    styles: List[str] = Field([
        "Fooocus V2",
        "Fooocus Enhance",
    ], description="The default styles to use.")
    
    vae_name: str = Field("Default (model)", description="The default vae to use.")
    
    performance_selection: Performance = Performance.SPEED
    
    # Format and save options
    output_format: OUTPUTFORMAT_LIT = Field(OutputFormat.WEBP, description="Output format")
    save_metadata_to_images: bool = Field(False, description="The default save metadata to images to use.")
    save_only_final_enhanced_image: bool = Field(False, description="The default save only final enhanced image to use.")
    aspect_ratio: SDXL_ASPECT_RATIOS = Field(SDXL_ASPECT_RATIOS_CLASS.PORTRAIT.R832_1152, description="The default aspect ratio to use.")
    
    # ERROR HERE
    adaptive_cfg: float = Field(7.0, description="The default cfg tsnr to use.", ge=1.0, le=30.0)
    cfg_scale: float = Field(4.0, description="Higher value means style is cleaner, vivider, and more artistic.", ge=1.0, le=30.0)
    cfg_tsnr: float = Field(7.0, description="The default cfg tsnr to use.")
    
    adm_scaler_end: float = Field(0.3, description="The default adm scaler end to use.", ge=0.0, le=1.0)
    adm_scaler_negative: float = Field(0.8, description="The default adm scaler negative to use.", ge=0.1, le=3.0)
    adm_scaler_positive: float = Field(1.5, description="The default adm scaler positive to use.", ge=0.1, le=3.0)
    

    canny_high_threshold: int = Field(128, description="The default canny high threshold to use.", ge=0, le=255)
    canny_low_threshold: int = Field(64, description="The default canny low threshold to use.", ge=0, le=255)
    
    controlnet_softness: float = Field(0.25, description="The default controlnet softness to use.", ge=0.0, le=1.0)
    dino_erode_or_dilate: int = 0 # min -64 max 64

    controlnet_tasks: Optional[List[BaseControlNetTaskForRequests]] = None
    overwrite_controls: Optional[OverWriteControls] = None
    
    image_input_mode: INPUT_IMAGE_MODES = Field("uov", description="The image input mode to use.") # utils.flags.input_image_tab_ids 
    
    input_image: Optional[Dict[Literal["image", "mask"], Any]] = None
    input_image_url: Optional[str] = None
    uov_input_image: Optional[Any] = None
    input_mask_image: Optional[Dict[Literal["image", "mask"], Any]] = None
    prepared_input_mask_image: Optional[Any] = None
    enhance_input_image: Optional[bool] = None


    

HooocusConfig = ImageGenerationObject(**current_preset)
DefaultConfigImageGen = ImageGenerationObject(**DEFAULT_PRESET)


""" 
with open("hoocus_config.json", "w") as f:

    f.write(HooocusConfig.model_dump_json()) """
