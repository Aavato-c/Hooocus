import os
import sys

# Calculate the root directory of the project by splitting the path at "h3_utils"
ROOT_DIR = os.path.abspath(__file__).split("h3_utils")[0]
sys.path.append(ROOT_DIR)

os.environ['ROOT_DIR'] = ROOT_DIR

import ssl
import platform

from modules.model_file_utils.hash_cache import init_cache, load_cache_from_file
from h3_utils.launch.launch_util import is_installed, run, python, run_pip, delete_folder_content
from modules.model_file_utils.model_loader import load_file_from_url
from h3_utils.config import LAUNCH_ARGS
from h3_utils.flags import LORA_FILENAMES, MODEL_FILENAMES
from h3_utils.path_configs import FolderPathsConfig
from h3_utils.logging_util import LoggingUtil

log = LoggingUtil(__name__).get_logger()
args = LAUNCH_ARGS

log.info(f"Python {sys.version}")
log.info(f"Hooocus version: {LAUNCH_ARGS.hooocus_version}")


vae_approx_filenames = [
    ('xlvaeapp.pth', 'https://huggingface.co/lllyasviel/misc/resolve/main/xlvaeapp.pth'),
    ('vaeapp_sd15.pth', 'https://huggingface.co/lllyasviel/misc/resolve/main/vaeapp_sd15.pt'),
    ('xl-to-v1_interposer-v4.0.safetensors',
     'https://huggingface.co/mashb1t/misc/resolve/main/xl-to-v1_interposer-v4.0.safetensors')
]
ssl._create_default_https_context = ssl._create_unverified_context


def prepare_environment():
    hash_cache = load_cache_from_file()
    torch_index_url = os.environ.get('TORCH_INDEX_URL', "https://download.pytorch.org/whl/cu121")
    torch_command = os.environ.get('TORCH_COMMAND',
                                   f"pip install torch==2.1.0 torchvision==0.16.0 --extra-index-url {torch_index_url}")
    requirements_file = os.environ.get('REQS_FILE', "requirements.txt")

    log.info(f"Python {sys.version}")
    log.info(f"Hooocus version: {LAUNCH_ARGS.hooocus_version}")

    torch_installed = is_installed("torch")
    torchvision_installed = is_installed("torchvision")
    if not torch_installed or not torchvision_installed:
        run(f'"{python}" -m {torch_command}', "Installing torch and torchvision", "Couldn't install torch", live=True)

    if LAUNCH_ARGS.try_install_xformers:
        xformers_installed = is_installed("xformers")
        if not xformers_installed:
            xformers_package = os.environ.get('XFORMERS_PACKAGE', 'xformers==0.0.23')
            if platform.system() == "Windows":
                if platform.python_version().startswith("3.10"):
                    run_pip(f"install -U -I --no-deps {xformers_package}", "xformers", live=True)
                else:
                    print("Installation of xformers is not supported in this version of Python.")
                    print(
                        "You can also check this and build manually: https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Xformers#building-xformers-on-windows-by-duckness")
                    if not is_installed("xformers"):
                        exit(0)
            elif platform.system() == "Linux":
                run_pip(f"install -U -I --no-deps {xformers_package}", "xformers")


    
   

    # Set environment variables for GPU device and Hugging Face mirror
    if args.gpu_device_id is not None:
        os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu_device_id)
        print("Set device to:", args.gpu_device_id)

    if args.hf_mirror is not None:
        os.environ['HF_MIRROR'] = str(args.hf_mirror)
        print("Set hf_mirror to:", args.hf_mirror)

    os.environ["U2NET_HOME"] = FolderPathsConfig.path_inpaint

    os.environ['GRADIO_TEMP_DIR'] = FolderPathsConfig.default_temp_path

    if args.temp_path_cleanup_on_launch:
        print(f'[Cleanup] Attempting to delete content of temp dir {FolderPathsConfig.default_temp_path}')
        result = delete_folder_content(FolderPathsConfig.default_temp_path, '[Cleanup] ')
        if result:
            print("[Cleanup] Cleanup successful")
        else:
            print(f"[Cleanup] Failed to delete content of temp dir.")

    if len(hash_cache) == 0 and (len(MODEL_FILENAMES) > 0 or len(LORA_FILENAMES) > 0):
        if args.rebuild_hash_cache:
            hash_cache = init_cache(MODEL_FILENAMES, FolderPathsConfig.path_checkpoints, LORA_FILENAMES, FolderPathsConfig.path_loras)
            print('[Cache] Rebuilt cache.')
        else:
            hash_cache = init_cache(MODEL_FILENAMES, FolderPathsConfig.path_checkpoints, LORA_FILENAMES, FolderPathsConfig.path_loras)
            if len(hash_cache) > 0:
                print(f'[Cache] Initialized with {len(hash_cache)} entries.')
            else:
                print('[Cache] Initialization failed.')
    return



