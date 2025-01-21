from copy import deepcopy
import os
import sys
import numpy
import torch

from extras.facexlib.parsing.bisenet import BiSeNet
from extras.facexlib.parsing.parsenet import ParseNet


ROOT_DIR = os.path.abspath(__file__).split("h3_utils")[0]
sys.path.append(ROOT_DIR)

from extras.facexlib.detection.retinaface import RetinaFace
from h3_utils.logging_util import LoggingUtil
from ldm_patched.controlnet.cldm import ControlNet

from enum import Enum

from typing import Any, List, Optional

from pydantic import BaseModel, Field

from modules.model_file_utils.model_loader import load_file_from_url
from h3_utils.path_configs import FolderPathsConfig
from h3_utils.flags import CONTROLNET_TASK_TYPES_CLASS, PerformanceLoRA


log = LoggingUtil(__name__).get_logger()

class _BaseModelFile(BaseModel):
    """A base class for model files

    Attributes:
        model_path_basename (str): The name of the model file.
        model_path_folder (str): The folder path where the model will be stored.
        model_url (str): The URL to download the model file.
        nameof_model (str): The name of the model file.

    Methods:
        download_model() -> str: Downloads the model file and returns the full path.
    
    """
    filename_of_model: str = None
    folder_path_of_model: str = None
    url_of_model: Optional[str] = None
    
    def full_path(self):
        return os.path.join(self.folder_path_of_model, self.filename_of_model)

    def download_model(self):
        log.info(f"Downloading {self.filename_of_model} from {self.url_of_model}")        
        if not self.folder_path_of_model:
            raise ValueError("model_path_folder is not set.")

        load_file_from_url(
            url=self.url_of_model,
            model_dir=self.folder_path_of_model,
            file_name=self.filename_of_model
        )
        return os.path.join(self.folder_path_of_model, self.filename_of_model)



class _BaseControlNetModelFile(_BaseModelFile):
    folder_path_of_model: str = FolderPathsConfig.path_controlnet

ImagePromptClipVIsion = _BaseControlNetModelFile(
    filename_of_model = "clip_vision_vit_h",
    url_of_model = "https://huggingface.co/lllyasviel/misc/resolve/main/clip_vision_vit_h.safetensors",
    basename_of_model = "clip_vision_vit_h.safetensors",
)

ImagePromptAdapterPlus = _BaseControlNetModelFile(
    filename_of_model = "ip-adapter-plus",
    url_of_model = "https://huggingface.co/lllyasviel/misc/resolve/main/ip-adapter-plus_sdxl_vit-h.bin",
    basename_of_model = "'ip-adapter-plus_sdxl_vit-h.bin"
)

ImagePromptAdapterNegative = _BaseControlNetModelFile(
    filename_of_model = "fooocus_ip_negative",
    url_of_model = "https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_ip_negative.safetensors",
    basename_of_model = "fooocus_ip_negative.safetensors"
)

ImagePromptAdapterFace = _BaseControlNetModelFile(
    filename_of_model = "ip-adapter-plus-face",
    url_of_model = "https://huggingface.co/lllyasviel/misc/resolve/main/ip-adapter-plus-face_sdxl_vit-h.bin",
    basename_of_model = "ip-adapter-plus-face_sdxl_vit-h.bin"
)

PyraCanny = _BaseControlNetModelFile(
    filename_of_model = 'canny',
    url_of_model = 'https://huggingface.co/lllyasviel/misc/resolve/main/control-lora-canny-rank128.safetensors',
    basename_of_model = 'control-lora-canny-rank128.safetensors',
)

CPDS = _BaseControlNetModelFile(
    filename_of_model = 'cpds',
    url_of_model = 'https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_xl_cpds_128.safetensors',
    basename_of_model = 'fooocus_xl_cpds_128.safetensors',
)

class InpaintModelFiles:
    class _InpaintModelFile(_BaseModelFile):
        folder_path_of_model: str = FolderPathsConfig.path_inpaint

    def download_based_on_version(self, version):
        if version == "1.0":
            return self.InpaintPatchV1.download_model()
        elif version == "2.5":
            return self.InpaintPatchV25.download_model()
        elif version == "2.6":
            return self.InpaintPatchV26.download_model()
        else:
            raise ValueError("Invalid version number.")


    InpaintHead = _InpaintModelFile(
        filename_of_model = 'fooocus_inpaint_head.pth',
        url_of_model = 'https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/fooocus_inpaint_head.pth',
    )

    InpaintPatchV1 = _InpaintModelFile(
        filename_of_model = 'inpaint.fooocus.patch',
        url_of_model = 'https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/inpaint.fooocus.patch',
    )

    InpaintPatchV25 = _InpaintModelFile(
        filename_of_model = 'inpaint_v25.fooocus.patch',
        url_of_model = 'https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/inpaint_v25.fooocus.patch',
    )

    InpaintPatchV26 = _InpaintModelFile(
        filename_of_model = 'inpaint_v26.fooocus.patch',
        url_of_model = 'https://huggingface.co/lllyasviel/fooocus_inpaint/resolve/main/inpaint_v26.fooocus.patch',
    )

class _SAMFile(_BaseModelFile):
    folder_path_of_model: str = FolderPathsConfig.path_sam

class SAM_Files(Enum):
    """
    Segment Anything Model Files

    """

    VIT_B = _SAMFile(
        filename_of_model = 'sam_vit_b_01ec64.pth',
        url_of_model = 'https://huggingface.co/mashb1t/misc/resolve/main/sam_vit_b_01ec64.pth',
        basename_of_model = 'sam_vit_b_01ec64.pth'
    )

    VIT_L = _SAMFile(
        filename_of_model = 'sam_vit_l_0b3195.pth',
        url_of_model = 'https://huggingface.co/mashb1t/misc/resolve/main/sam_vit_l_0b3195.pth',
        basename_of_model = 'sam_vit_l_0b3195.pth'
    )

    VIT_H = _SAMFile(
        filename_of_model = 'sam_vit_h_4b8939.pth',
        url_of_model = 'https://huggingface.co/mashb1t/misc/resolve/main/sam_vit_h_4b8939.pth',
        basename_of_model = 'sam_vit_h_4b8939.pth'
    )



class VaeApproxFiles:
    VaeAppSDXL = _BaseModelFile(
        folder_path_of_model = FolderPathsConfig.path_vae,
        filename_of_model = 'xlvaeapp.pth',
        url_of_model = 'https://huggingface.co/lllyasviel/misc/resolve/main/xlvaeapp.pth',
        basename_of_model = 'xlvaeapp.pth'
    )

    VaeAppSD15 = _BaseModelFile(
        folder_path_of_model= FolderPathsConfig.path_vae,
        filename_of_model = 'vaeapp_sd15.pth',
        url_of_model = 'https://huggingface.co/lllyasviel/misc/resolve/main/vaeapp_sd15.pt',
        basename_of_model = 'vaeapp_sd15.pth'
    )

    XlToV1Interposer = _BaseModelFile(
        folder_path_of_model = FolderPathsConfig.path_vae,
        filename_of_model = 'xl-to-v1_interposer-v4.0.safetensors',
        url_of_model = 'https://huggingface.co/mashb1t/misc/resolve/main/xl-to-v1_interposer-v4.0.safetensors',
        basename_of_model = 'xl-to-v1_interposer-v4.0.safetensors'
    )


class FaceXLibModelFiles:
    def __init__(self):
        pass
    
    RetinaFaceResNet50 = _BaseModelFile(
        filename_of_model = 'detection_Resnet50_Final.pth',
        folder_path_of_model= FolderPathsConfig.path_facexlib,
        url_of_model = 'https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_Resnet50_Final.pth',
    )

    RetinaFaceMobile025 = _BaseModelFile(
        filename_of_model = 'detection_mobilenet0.25_Final.pth',
        folder_path_of_model= FolderPathsConfig.path_facexlib,
        url_of_model = 'https://github.com/xinntao/facexlib/releases/download/v0.1.0/detection_mobilenet0.25_Final.pth',
    )

    @classmethod
    def init_face_detection_model(cls, model_name, half=False, device='cuda'):
        if model_name == 'retinaface_resnet50':
            model = RetinaFace(network_name='resnet50', half=half, device=device)
            model_path = load_file_from_url(
                url=cls.RetinaFaceResNet50.url_of_model,
                model_dir=cls.RetinaFaceResNet50.folder_path_of_model,
                file_name=cls.RetinaFaceResNet50.filename_of_model
            )

        elif model_name == 'retinaface_mobile0.25':
            model = RetinaFace(network_name='mobile0.25', half=half, device=device)
            model_path = load_file_from_url(
                url=cls.RetinaFaceMobile025.url_of_model,
                model_dir=cls.RetinaFaceMobile025.folder_path_of_model,
                file_name=cls.RetinaFaceMobile025.filename_of_model
            )
        else:
            raise NotImplementedError(f'{model_name} is not implemented.')
        # TODO: clean pretrained model
        load_net = torch.load(model_path, map_location=lambda storage, loc: storage, weights_only=True)

        for k, v in deepcopy(load_net).items():
            if k.startswith('module.'):
                load_net[k[7:]] = v
                load_net.pop(k)
        model.load_state_dict(load_net, strict=True)
        model.eval()
        model = model.to(device)
        return model
    
    

    ParsingModelBiseNet = _BaseModelFile(
        filename_of_model = 'parsing_bisenet.pth',
        folder_path_of_model= FolderPathsConfig.path_facexlib,
        url_of_model = 'https://github.com/xinntao/facexlib/releases/download/v0.2.0/parsing_bisenet.pth',
    )

    ParsingModelParseNet = _BaseModelFile(
        filename_of_model = 'parsing_parsenet.pth',
        folder_path_of_model= FolderPathsConfig.path_facexlib,
        url_of_model = 'https://github.com/xinntao/facexlib/releases/download/v0.2.2/parsing_parsenet.pth',
    )

    @classmethod
    def init_parsing_model(cls, model_name='bisenet', half=False, device='cuda'):
        if model_name == 'bisenet':
            model = BiSeNet(num_class=19)
            model_url = cls.ParsingModelBiseNet.url_of_model
        elif model_name == 'parsenet':
            model = ParseNet(in_size=512, out_size=512, parsing_ch=19)
            model_url = cls.ParsingModelParseNet.url_of_model
        else:
            raise NotImplementedError(f'{model_name} is not implemented.')
        
        model_path = load_file_from_url(
            url=model_url, model_dir=cls.ParsingModelBiseNet.folder_path_of_model, progress=True, file_name=None)
        load_net = torch.load(model_path, map_location=lambda storage, loc: storage, weights_only=True)
        model.load_state_dict(load_net, strict=True)
        model.eval()
        model = model.to(device)
        return model
    


    
class BaseControlNetTask(BaseModel):
    class Config:
        arbitrary_types_allowed = True
    
    ip_conds: Optional[List[Any]] = None
    ip_unconds: Optional[List[Any]] = None
    stop: float = Field(0.5, ge=0, le=1)
    img: Optional[numpy.ndarray] = None
    image_url: Optional[str] = None
    weight: float = Field(1.0, ge=0, le=1)
    all_models: Optional[List[_BaseControlNetModelFile]] = None
    name: str = Field(None, description="Name of the ControlNetTask.")
    paths_of_models: Optional[List[str]] = None

    def get_paths(self):
        if self.models is None:
            return []
        return [model.full_path() for model in self.models]
    



class ControlNetTasks:
    ImagePrompt: BaseControlNetTask = BaseControlNetTask(
        stop = 0.5,
        name = CONTROLNET_TASK_TYPES_CLASS.ImagePrompt,
        weight = 0.6,
        img = None,
        all_models = [
            ImagePromptClipVIsion, 
            ImagePromptAdapterPlus,
            ImagePromptAdapterNegative
        ]
    )
    
    FaceSwap: BaseControlNetTask = BaseControlNetTask(
        stop = 0.9,
        img = None,
        name = CONTROLNET_TASK_TYPES_CLASS.IpFace,
        weight = 0.75,
        all_models = [
            ImagePromptClipVIsion,
            ImagePromptAdapterFace,
            ImagePromptAdapterNegative
        ],
    )

    PyraCanny: BaseControlNetTask = BaseControlNetTask(
        stop = 0.5,
        img = None,
        name = CONTROLNET_TASK_TYPES_CLASS.PyraCanny,
        weight = 1.0,
        all_models = [
            PyraCanny
        ]

        )

    CPDS: BaseControlNetTask = BaseControlNetTask(
        stop = 0.5,
        img = None,
        name = CONTROLNET_TASK_TYPES_CLASS.CPDS,
        weight = 1.0,
        all_models = [
            CPDS
        ]
    )


def controlnet_task_by_name(name: str, update_with: dict):
    match name:
        case CONTROLNET_TASK_TYPES_CLASS.IpFace:
            name = "FaceSwap"
        case _:
            raise ValueError("Invalid task name.")
        
    task_base = getattr(ControlNetTasks, name)
    task_base = task_base.copy(update=update_with)
    return task_base
    

UpscaleModel = _BaseModelFile(
    url_of_model="https://huggingface.co/lllyasviel/misc/resolve/main/fooocus_upscaler_s409985e5.bin",
    filename_of_model="fooocus_upscaler",
    basename_of_model="fooocus_upscaler_s409985e5.bin",
    folder_path_of_model=FolderPathsConfig.path_upscale_models
)

SafetyCheckModel = _BaseModelFile(
    url_of_model="https://huggingface.co/mashb1t/misc/resolve/main/stable-diffusion-safety-checker.bin",
    filename_of_model="fooocus_safety_check",
    basename_of_model="stable-diffusion-safety-checker.bin",
    folder_path_of_model=FolderPathsConfig.path_safety_checker
)

SDXL_LightningLoRA = _BaseModelFile(
    url_of_model="https://huggingface.co/mashb1t/misc/resolve/main/sdxl_lightning_4step_lora.safetensors",
    filename_of_model=PerformanceLoRA.LIGHTNING.value,
    basename_of_model=PerformanceLoRA.LIGHTNING.value,
    folder_path_of_model=FolderPathsConfig.path_loras
)

SDXL_HyperSDLoRA = _BaseModelFile(
    url_of_model="https://huggingface.co/mashb1t/misc/resolve/main/sdxl_hyper_sd_4step_lora.safetensors",
    filename_of_model=PerformanceLoRA.HYPER_SD.value,
    basename_of_model=PerformanceLoRA.HYPER_SD.value,
    folder_path_of_model=FolderPathsConfig.path_loras
)

SDXL_LCM_LoRA = _BaseModelFile(
    url_of_model="https://huggingface.co/lllyasviel/misc/resolve/main/sdxl_lcm_lora.safetensors",
    filename_of_model=PerformanceLoRA.EXTREME_SPEED.value,
    basename_of_model=PerformanceLoRA.EXTREME_SPEED.value,
    folder_path_of_model=FolderPathsConfig.path_loras
)


class CheckPoints:
    class _CheckPointFile(_BaseModelFile):
        folder_path_of_model: str = FolderPathsConfig.path_checkpoints

    JuggernautXL_v8 = _CheckPointFile(
        filename_of_model = 'juggernautXL_v8Rundiffusion.safetensors',
        url_of_model = 'https://huggingface.co/lllyasviel/fav_models/resolve/main/fav/juggernautXL_v8Rundiffusion.safetensors',
        basename_of_model = 'juggernautXL_v8Rundiffusion.safetensors'
    )


class AllModelFiles:

    BaseModel = _BaseModelFile()
    UpscaleModel = UpscaleModel
    SafetyCheckModel = SafetyCheckModel
    SDXL_LightningLoRA = SDXL_LightningLoRA
    SDXL_HyperSDLoRA = SDXL_HyperSDLoRA
    SDXL_LCM_LoRA = SDXL_LCM_LoRA
    ControlNetModels = [ControlNetTasks.ImagePrompt.all_models, ControlNetTasks.FaceSwap.all_models, ControlNetTasks.PyraCanny.all_models, ControlNetTasks.CPDS.all_models]
    InpaintModels = InpaintModelFiles()
    SAM_Files = SAM_Files
    CheckPoints = CheckPoints.JuggernautXL_v8
    

