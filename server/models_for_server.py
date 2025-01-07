import os
import sys

from h3_utils.config import BaseControlNetTaskForRequests, OverWriteControls
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic_core import from_json
from torch import Tensor


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random

from h3_utils.flags import DESCRIBE_TYPE_PHOTO, ENHANCEMENT_UOV_PROMPT_TYPE_ORIGINAL, KSAMPLER, KSAMPLER_NAMES, KSAMPLER_NAMES_LIT, OUTPUTFORMAT_LIT, REFINER_SWAP_METHODS, SDXL_ASPECT_RATIOS, SDXL_ASPECT_RATIOS_CLASS, UPSCALE_OR_VARIATION_MODES, Overrides, Steps

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PARENT_DIR)

import json
import tempfile
from typing import Any, Dict, List, Literal, Optional, Tuple, Iterable, TypeAlias, Union
from enum import Enum
from h3_utils.model_file_config import BaseControlNetTask
from pydantic import BaseModel, Field, field_validator
from numpy.typing import NDArray

from modules.model_file_utils.model_loader import load_file_from_url
from h3_utils.path_configs import FolderPathsConfig
from h3_utils.logging_util import LoggingUtil
from h3_utils.flags import EXAMPLE_ENHANCE_DETECTION_PROMPTS, INPAINT_MASK_CLOTH_CATEGORY, INPUT_IMAGE_MODES, KSAMPLER, OUTPAINT_SELECTIONS, REFINER_SWAP_METHODS, SDXL_ASPECT_RATIOS, UPSCALE_OR_VARIATION_MODES, LatentPreviewMethod, OutputFormat, Performance, ENHANCEMENT_UOV_AFTER, ENHANCEMENT_UOV_BEFORE, ENHANCEMENT_UOV_PROCESSING_ORDER

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


    
