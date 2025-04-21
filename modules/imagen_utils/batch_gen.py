# nohup sh /home/kake/Hooocus/modules/imagen_utils/rungen.sh >> /home/kake/Hooocus/batchgen/rungen.log 2>&1 &
import random
import json, os, sys



currdir = os.path.abspath(__file__)
sys.path.append(currdir.split("Hooocus")[0] + "Hooocus")

from modules.sdxl_styles.prompt_styles import MetaStyles, PromptStyles
from h3_utils import path_configs
from h3_utils.logging_util import LoggingUtil
from h3_utils.config import ImageGenerationObject, ImageGenerationObjectForRequests
from h3_utils.flags import SDXL_ASPECT_RATIOS_CLASS, Performance
from modules.imagen_utils.imagen_main import generate_from_batch

log = LoggingUtil("batch_gen").get_logger()

def add_imageorders_from_json(json_path: str, n: int = 3):
    """
    Reads a JSON file and adds image orders to the database.
    """

    batch_output_log_path = json_path.replace(".json", "batch_log.json")

    if not os.path.exists(path_configs.FolderPathsConfig.batch_log_txt):
        with open(path_configs.FolderPathsConfig.batch_log_txt, "w") as f:
            f.write("")
    
    

    with open(json_path, "r") as f:
        data = json.load(f)

    for item in data:
       
        
        data_id = item["id"]
        for i in range(n):
            
            with open(path_configs.FolderPathsConfig.batch_log_txt, "r") as f:
                global_log_data = f.readlines()
    
            if f"{data_id}_{i}\n" in global_log_data:
                log.warning(f"Item with id {data_id} already exists in the log. Skipping...")
                continue
            
            imagen_request_base = ImageGenerationObjectForRequests(
                sample_sharpness=10.5,
                cfg_scale=2.0,
                performance_selection=Performance.SPEED,
                )
            
            imagen_request_base.seed = random.randint(0, 2**63 - 1)
            imagen_request_base.uid = f"{data_id}_{i}"
            imagen_request_base.prompt = item["image_prompt"]
            imagen_request_base.aspect_ratio = SDXL_ASPECT_RATIOS_CLASS.LANDSCAPE.R_1280_768
            imagen_request_base.styles = [PromptStyles.Fooocus_Cinematic.name, MetaStyles.Fooocus_V2.name]
            log.info(f"Generating image {i} for id {imagen_request_base.uid} (Item: {item['id']})")
            


            try:
                output_path = generate_from_batch(imagen_request_base, imagen_request_base.uid, outputfolder=path_configs.FolderPathsConfig.batch_outputs)
                try:
                    item["image_paths"].append(output_path) #@IgnoreException
                except KeyError:
                    item["image_paths"] = [output_path]
            
            except Exception as e:
                print(f"Error generating image: {e}")
                continue
            
            with open(path_configs.FolderPathsConfig.batch_log_txt, "a") as f:
                f.write(f"{imagen_request_base.uid}\n")

            
            output_log_json_path = f"{path_configs.FolderPathsConfig.batch_outputs}/{imagen_request_base.uid}_log.json"
            with open(output_log_json_path, "w") as log_file:
                json.dump(item, log_file, indent=4, ensure_ascii=False)
            
            if os.path.exists(batch_output_log_path):
                with open(batch_output_log_path, "r") as log_file:
                    log_data = json.load(log_file)
                    if isinstance(log_data, list):
                        log_data.append(item)
                    else:
                        log_data = [log_data, item]
            
            else:
                log_data = [item]
            
            with open(batch_output_log_path, "w") as log_file:
                json.dump(log_data, log_file, indent=4, ensure_ascii=False)
            

        

        
if __name__ == "__main__":

    for file in os.listdir(path_configs.FolderPathsConfig.batch_input_json_folder):
        if file.endswith(".json"):
            json_path = os.path.join(path_configs.FolderPathsConfig.batch_input_json_folder, file)
            add_imageorders_from_json(json_path)

        