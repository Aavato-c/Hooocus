import os, sys
ROOT_DIR = os.path.abspath(__file__).split("Hooocus")[0]+"Hooocus"
sys.path.append(ROOT_DIR)


from enum import Enum
import os
import tempfile
from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()



class FolderPathsConfig:
    batch_folder = "./batchgen"
    batch_log_txt = os.path.join(batch_folder, "batch_log.txt")
    batch_input_json_folder = os.path.join(batch_folder, "input_json")
    batch_outputs = os.path.join(batch_folder, "outputs")
    path_facexlib = "./models/facexlib/"
    path_checkpoints = "./models/checkpoints/"
    path_loras = "./models/loras/"
    path_embeddings = "./models/embeddings/"
    path_vae_approx = "./models/vae_approx/"
    path_vae = "./models/vae/"
    path_upscale_models = "./models/upscale_models/"
    path_inpaint = "./models/inpaint/"
    path_controlnet = "./models/controlnet/"
    path_clip_vision = "./models/clip_vision/"
    path_fooocus_expansion = "./models/prompt_expansion/fooocus_expansion"
    path_wildcards = "./modules/sdxl_styles/wildcards/"
    path_safety_checker = "./models/safety_checker/"
    path_sam = "./models/sam/"
    path_prompt_style_samples = "./modules/sdxl_styles/samples/"
    config_path = "h3_utils/config.json"
    hash_cache_path = f"{ROOT_DIR}/__cache__/hash_cache.json"
    auth_filename = "auth.json"
    
    default_temp_path = os.path.join(tempfile.gettempdir(), 'hooocus')
    path_outputs: str = "outputs" # Don't use a dot here

    ALL = [
        "outputs",
        os.path.join(tempfile.gettempdir(), 'hooocus'),
        "./batchgen",
        os.path.join(batch_folder, "input_json"),
        os.path.join(batch_folder, "outputs"),
        "./models/facexlib/",
        "./models/checkpoints/",
        "./models/loras/",
        "./models/embeddings/",
        "./models/vae_approx/",
        "./models/vae/",
        "./models/upscale_models/",
        "./models/inpaint/",
        "./models/controlnet/",
        "./models/clip_vision/",
        "./models/prompt_expansion/fooocus_expansion",
        "./modules/sdxl_styles/wildcards/",
        "./models/safety_checker/",
        "./models/sam/",
        "./modules/sdxl_styles/samples/",
        "h3_utils/config.json",
        f"{ROOT_DIR}/__cache__/hash_cache.json",
        "auth.json",
    ]


def create_folders_if_not_exists(folders: list):
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            log.info(f"Created path: {folder}")
    

class _EnumFolderPaths(Enum):
    path_facexlib = "./models/facexlib/"
    path_checkpoints = "./models/checkpoints/"
    path_loras = "./models/loras/"
    path_embeddings = "./models/embeddings/"
    path_vae_approx = "./models/vae_approx/"
    path_vae = "./models/vae/"
    path_upscale_models = "./models/upscale_models/"
    path_inpaint = "./models/inpaint/"
    path_controlnet = "./models/controlnet/"
    path_clip_vision = "./models/clip_vision/"
    path_fooocus_expansion = "./models/prompt_expansion/fooocus_expansion"
    path_wildcards = "./modules/sdxl_styles/wildcards/"
    path_safety_checker = "./models/safety_checker/"
    path_sam = "./models/sam/"
    path_prompt_style_samples = "./modules/sdxl_styles/samples/"
    
    default_temp_path = os.path.join(tempfile.gettempdir(), 'hooocus')
    path_outputs: str = "./outputs"



_folder_path_config = _EnumFolderPaths
for path in _folder_path_config:
    if not os.path.exists(path.value):
        os.makedirs(path.value)
        log.info(f"Created path: {path.value}")


create_folders_if_not_exists(FolderPathsConfig.ALL)