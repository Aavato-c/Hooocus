import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import dotenv
import numpy
from pydantic import BaseModel, Field

from h3_utils.filesystem_utils import (
    get_files_from_folder,
    get_model_filenames,
    get_presets,
)
from h3_utils.path_configs import FolderPathsConfig

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from enum import IntEnum, Enum
from typing import Literal
import tempfile
from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()
dotenv.load_dotenv(override=True)


# For YieldObject
yield_types = Literal[
    "preview", "result", "waiting", "uri", "finish", "starting", "meta"
]


class YIELD_TYPE_FLAGS:
    preview = "preview"
    result = "result"
    waiting = "waiting"
    uri = "uri"
    finish = "finish"
    starting = "starting"
    meta = "meta"


MIN_SEED = 0
MAX_SEED = 2**63 - 1


DESCRIBE_TYPE_PHOTO = "Photograph"
DESCRIBE_TYPE_ANIME = "Art/Anime"
DESCRIBE_TYPES = [DESCRIBE_TYPE_PHOTO, DESCRIBE_TYPE_ANIME]

literal_enhancement_proceccing_order = Literal[
    "Before First Enhancement", "After Last Enhancement"
]

ENHANCEMENT_UOV_BEFORE = "Before First Enhancement"
ENHANCEMENT_UOV_AFTER = "After Last Enhancement"
ENHANCEMENT_UOV_PROCESSING_ORDER = [ENHANCEMENT_UOV_BEFORE, ENHANCEMENT_UOV_AFTER]

ENHANCEMENT_UOV_PROMPT_TYPE_ORIGINAL = "Original Prompts"
ENHANCEMENT_UOV_PROMPT_TYPE_LAST_FILLED = "Last Filled Enhancement Prompts"
ENHANCEMENT_UOV_PROMPT_TYPES = [
    ENHANCEMENT_UOV_PROMPT_TYPE_ORIGINAL,
    ENHANCEMENT_UOV_PROMPT_TYPE_LAST_FILLED,
]

SDXL_ASPECT_RATIOS = Literal[
    "704*1408",
    "704*1344",
    "768*1344",
    "768*1280",
    "832*1216",
    "832*1152",
    "896*1152",
    "896*1088",
    "960*1088",
    "960*1024",
    "1024*1024",
    "1024*960",
    "1088*960",
    "1088*896",
    "1152*896",
    "1152*832",
    "1216*832",
    "1280*768",
    "1344*768",
    "1344*704",
    "1408*704",
    "1472*704",
    "1536*640",
    "1600*640",
    "1664*576",
    "1728*576",
]


class SDXL_ASPECT_RATIOS_CLASS:
    class PORTRAIT:
        R960_1088 = "960*1088"
        R960_1024 = "960*1024"
        R896_1152 = "896*1152"
        R896_1088 = "896*1088"
        R832_1216 = "832*1216"
        R832_1152 = "832*1152"
        R768_1344 = "768*1344"
        R768_1280 = "768*1280"
        R704_1408 = "704*1408"
        R704_1344 = "704*1344"

    class SQUARE:
        R1024_1024 = "1024*1024"

    class LANDSCAPE:
        R_1728_576 = "1728*576"
        R_1664_576 = "1664*576"
        R_1600_640 = "1600*640"
        R_1536_640 = "1536*640"
        R_1472_704 = "1472*704"
        R_1408_704 = "1408*704"
        R_1344_768 = "1344*768"
        R_1344_704 = "1344*704"
        R_1280_768 = "1280*768"
        R_1216_832 = "1216*832"
        R_1152_896 = "1152*896"
        R_1152_832 = "1152*832"
        R_1088_960 = "1088*960"
        R_1088_896 = "1088*896"
        R_1024_960 = "1024*960"


INPUT_IMAGE_MODES = Literal["uov", "inpaint", "ip", "desc", "enhance", "metadata"]


class INPUT_IMAGE_MODES_CLASS:
    uov = "uov"
    ip = "ip"
    inpaint = "inpaint"
    desc = "desc"
    enhance = "enhance"
    metadata = "metadata"


class Overrides(BaseModel):
    steps: int | None = None
    switch: float | None = None
    width: int | None = None
    height: int | None = None


OUTPAINT_SELECTIONS = Literal["Left", "Right", "Top", "Bottom"]

REFINER_SWAP_METHODS = Literal["joint", "separate", "vae"]

CONTROLNET_TASK_TYPES = Literal["ImagePrompt", "ip_face", "PyraCanny", "CPDS"]


class CONTROLNET_TASK_TYPES_CLASS:
    ImagePrompt = "ImagePrompt"
    IpFace = "ip_face"
    PyraCanny = "PyraCanny"
    CPDS = "CPDS"


EXAMPLE_ENHANCE_DETECTION_PROMPTS = (["face", "eye", "mouth", "hair", "hand", "body"],)

UPSCALE_OR_VARIATION_MODES = Literal[
    "Enabled",
    "Vary (Subtle)",
    "Vary (Strong)",
    "Upscale (1.5x)",
    "Upscale (2x)",
    "Upscale (Fast 2x)",
]

CIVITAI_NO_KARRAS = Literal[
    "euler", "euler_ancestral", "heun", "dpm_fast", "dpm_adaptive", "ddim", "uni_pc"
]

max_image_number: int = 32
max_lora_number: int = 5
loras_max_weight: float = 2.0
loras_min_weight: float = 2.0
sam_max_detections: int = 0  # The default sam max detections to use.

INPAINT_MASK_CLOTH_CATEGORY = Literal["full", "upper", "lower"]


class KSAMPLER(Enum):
    euler = "Euler"
    euler_ancestral = "Euler a"
    heun = "Heun"
    heunpp2 = ""
    dpm_2 = "DPM2"
    dpm_2_ancestral = "DPM2 a"
    lms = "LMS"
    dpm_fast = "DPM fast"
    dpm_adaptive = "DPM adaptive"
    dpmpp_2s_ancestral = "DPM++ 2S a"
    dpmpp_sde = "DPM++ SDE"
    dpmpp_sde_gpu = "DPM++ SDE"
    dpmpp_2m = "DPM++ 2M"
    dpmpp_2m_sde = "DPM++ 2M SDE"
    dpmpp_2m_sde_gpu = "DPM++ 2M SDE"
    dpmpp_3m_sde = ""
    dpmpp_3m_sde_gpu = ""
    ddpm = ""
    lcm = "LCM"
    tcd = "TCD"
    restart = "Restart"


KSAMPLER_NAMES_LIT = Literal[
    "euler",
    "euler_ancestral",
    "heun",
    "heunpp2",
    "dpm_2",
    "dpm_2_ancestral",
    "lms",
    "dpm_fast",
    "dpm_adaptive",
    "dpmpp_2s_ancestral",
    "dpmpp_sde",
    "dpmpp_sde_gpu",
    "dpmpp_2m",
    "dpmpp_2m_sde",
    "dpmpp_2m_sde_gpu",
    "dpmpp_3m_sde",
    "dpmpp_3m_sde_gpu",
    "ddpm",
    "lcm",
    "tcd",
    "ddim",
    "uni_pc",
    "uni_pc_bh2",
    "restart",
]


class EXTRA_KSAMPLER(Enum):
    ddim = "DDIM"
    uni_pc = "UniPC"
    uni_pc_bh2 = ""


# Both KSAMPLER and EXTRA_KSAMPLER
KSAMPLER_NAMES = [k.value for k in KSAMPLER] + [k.value for k in EXTRA_KSAMPLER]
SAMPLERS = KSAMPLER | EXTRA_KSAMPLER
DEFAULT_SAMPLER = KSAMPLER.dpmpp_2m_sde_gpu

SCHEDULER_NAMES = [
    "normal",
    "karras",
    "exponential",
    "sgm_uniform",
    "simple",
    "ddim_uniform",
    "lcm",
    "turbo",
    "align_your_steps",
    "tcd",
    "edm_playground_v2.5",
]


class SCHEDULER_NAMES_CLS:
    normal = "normal"
    karras = "karras"
    exponential = "exponential"
    sgm_uniform = "sgm_uniform"
    simple = "simple"
    ddim_uniform = "ddim_uniform"
    lcm = "lcm"
    turbo = "turbo"
    align_your_steps = "align_your_steps"
    tcd = "tcd"
    edm_playground_v2_5 = "edm_playground_v2.5"


SCHEDULER_NAMES_LITERAL = Literal[
    "normal",
    "karras",
    "exponential",
    "sgm_uniform",
    "simple",
    "ddim_uniform",
    "lcm",
    "turbo",
    "align_your_steps",
    "tcd",
    "edm_playground_v2.5",
]


class _AvailableConfigsBase(Enum):
    pass


class LatentPreviewMethod(_AvailableConfigsBase):
    NoPreviews = "none"
    Auto = "auto"
    Latent2RGB = "fast"
    TAESD = "taesd"


class OutputFormat:
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"

    all = [PNG, JPEG, WEBP]


OUTPUTFORMAT_LIT = Literal["png", "jpeg", "webp"]


class RETURN_FORMATS:
    json = "json"
    image = "image"
    src_for_img_as_html = "src_for_img_as_html"
    src_for_img_as_json = "src_for_img_as_json"

    LIT = Literal["json", "image", "src_for_img_as_html", "src_for_img_as_json"]


class PerformanceLoRA(_AvailableConfigsBase):
    QUALITY = None
    SPEED = None
    EXTREME_SPEED = "sdxl_lcm_lora.safetensors"
    LIGHTNING = "sdxl_lightning_4step_lora.safetensors"
    HYPER_SD = "sdxl_hyper_sd_4step_lora.safetensors"


performance_lora_keys = PerformanceLoRA.__members__.keys()


class Steps(IntEnum):
    QUALITY = 60
    SPEED = 30
    EXTREME_SPEED = 8
    LIGHTNING = 4
    HYPER_SD = 4

    @classmethod
    def keys(cls) -> list:
        return list(map(lambda c: c, Steps.__members__))


class StepsUOV(IntEnum):
    QUALITY = 36
    SPEED = 18
    EXTREME_SPEED = 8
    LIGHTNING = 4
    HYPER_SD = 4


class Performance(_AvailableConfigsBase):
    QUALITY = "Quality"
    SPEED = "Speed"
    EXTREME_SPEED = "Extreme Speed"
    LIGHTNING = "Lightning"
    HYPER_SD = "Hyper-SD"

    LIT = Literal["Quality", "Speed", "Extreme Speed", "Lightning", "Hyper-SD"]

    @classmethod
    def list(cls) -> list:
        return list(map(lambda c: (c.name, c.value), cls))

    @classmethod
    def values(cls) -> list:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def by_steps(cls, steps: int | str):
        return cls[Steps(int(steps)).name]

    @classmethod
    def has_restricted_features(cls, x) -> bool:
        if isinstance(x, Performance):
            x = x.value
        return x in [cls.EXTREME_SPEED.value, cls.LIGHTNING.value, cls.HYPER_SD.value]

    def steps(self) -> int | None:
        return Steps[self.name].value if self.name in Steps.__members__ else None

    def steps_uov(self) -> int | None:
        return StepsUOV[self.name].value if self.name in StepsUOV.__members__ else None

    def lora_filename(self) -> str | None:
        return (
            PerformanceLoRA[self.name].value
            if self.name in PerformanceLoRA.__members__
            else None
        )


performance_keys = Performance.__members__.keys()


INPAINT_ENGINE_VERSIONS = Literal["1.0", "2.5", "2.6"]
AVAILABLE_PRESETS = get_presets()
MODEL_FILENAMES = get_model_filenames(FolderPathsConfig.path_checkpoints)
LORA_FILENAMES = get_model_filenames(FolderPathsConfig.path_loras)
VAE_FILENAMES = get_model_filenames(FolderPathsConfig.path_vae)
WILDCARD_FILENAMES = get_files_from_folder(FolderPathsConfig.path_wildcards, [".txt"])
