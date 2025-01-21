import os, sys
rootdir = os.path.abspath(__file__).split("Hooocus")[0]+"Hooocus"
sys.path.append(rootdir)

from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

from h3_utils.logging_util import LoggingUtil
from h3_utils.flags import (
    LatentPreviewMethod,
)

log = LoggingUtil(__name__).get_logger()


HOOOCUS_VERSION = "0.5.2-alpha"
METADATA_SCHEME = "Hooocus"

class _LAUNCH_ARGS(BaseModel):
    # Modify the initial values here
    class Config:
        arbitrary_types_allowed = True

    # General args
    enable_auto_describe_image: bool = Field(
        False,
        description="Enables automatic description of uov and enhance image when prompt is empty.",
    )
    preview_option: LatentPreviewMethod = LatentPreviewMethod.Auto
    wildcards_max_bfs_depth: int = 64
    disable_image_log: bool = Field(
        False, description="Prevent writing images and logs to the outputs folder."
    )
    disable_analytics: bool = Field(False, description="Disables analytics for Gradio.")
    disable_metadata: bool = Field(
        False, description="Disables saving metadata to images."
    )
    disable_preset_download: bool = Field(
        False, description="Disables downloading models for presets."
    )
    disable_enhance_output_sorting: bool = Field(
        False, description="Disables enhance output sorting for final image gallery."
    )
    always_download_new_model: bool = Field(
        False, description="Always download newer models."
    )
    rebuild_hash_cache: bool = Field(
        False, description="Generates missing model and LoRA hashes."
    )
    temp_path_cleanup_on_launch: bool = Field(
        True, description="The temp path cleanup on launch to use."
    )
    should_check_for_updates: bool = False

    # Etc
    web_upload_size: float = 100.0
    hf_mirror: str = "https://huggingface.co"
    external_working_path: str = None
    temp_path: str = None
    cache_path: str = None
    in_browser: bool = False
    disable_in_browser: bool = False

    # Global imagegen
    min_seed: int = 0
    max_seed: int = 2**63 - 1
    disable_attention_upcast: bool = False
    gpu_device_id: Optional[int] = None
    output_path: str = None
    directml: bool = False
    disable_ipex_hijack: bool = False
    disable_xformers: bool = False
    pytorch_deterministic: bool = False

    # CMD args
    async_cuda_allocation: bool = False
    disable_async_cuda_allocation: bool = False

    # Model args
    all_in_fp32: bool = False
    all_in_fp16: bool = False

    # Unet args
    unet_in_bf16: bool = False
    unet_in_fp16: bool = False
    unet_in_fp8_e4m3fn: bool = False
    unet_in_fp8_e5m2: bool = False

    # VAE args
    vae_in_fp16: bool = False
    vae_in_fp32: bool = False
    vae_in_bf16: bool = False
    vae_in_cpu: bool = False

    # FPTEArgs
    clip_in_fp8_e4m3fn: bool = False
    clip_in_fp8_e5m2: bool = False
    clip_in_fp16: bool = False
    clip_in_fp32: bool = False

    # AttentionArgs
    attention_split: bool = False
    attention_quad: bool = False
    attention_pytorch: bool = False

    # VramArgs
    always_cpu: bool = False
    always_gpu: bool = True
    always_high_vram: bool = True
    always_normal_vram: bool = False
    always_low_vram: bool = False
    always_no_vram: bool = False
    always_offload_from_vram: bool = False


LAUNCH_ARGS = _LAUNCH_ARGS()
