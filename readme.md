# Hooocus (H3)
<div align=center>
<img src="https://github.com/Aavato-c/Hooocus/blob/main/media/logo2.png">
</div>

### A *H*eadless variant of Fooocus

`v. 0.5.1`

> **This project is very much in a development phase. If you're just looking for a way to create images, use [the original Fooocus](https://github.com/lllyasviel/Fooocus).**

Hooocus (H3) is a headless variant of [Fooocus](https://github.com/lllyasviel/Fooocus), a wonderful creation started by [lllyasviel](https://github.com/lllyasviel)

Fooocus has included and automated [lots of inner optimizations and quality improvements](#tech_list). Where the Gradio UI may provide ease of use, the aim of this fork is to provide ease of automation. Ideally, one should be able to use the Fooocus log parameters as starting points for creating images with Hooocus. It started out of my own needs.

Goals:

- A simple HTTP-api for generating images
- A lower level API improving on the existing one with e.g. adding pydantic validations
- Removing gradio as a dependancy at some point

Priorities:

- Concentrate global state managment more neatly (now having flags, argvs, configs,     consts, globals, config-files etc)
- Build a basic gradio-free workflow example

Status:
Look into main.py for a usage example. It all boils down to using the `ImageGenerationObject` to create a "task" for the `ImageProcessor`. The ImageProcessor will then handle the generation of the image from ImageProcessor.generation_tasks -list.

## Usage (MacOs / Ubuntu)

``python3 -m venv venv``
``source venv/bin/activate``
``python3 -m pip install -r requirements_versions.txt``
--> A work in progress....

## Some of the "Hidden" tricks that were present in Fooocus that are also included in H3

<a name="tech_list"></a>

<details>
<summary>Click to see a list of tricks. Those are based on SDXL and are not very up-to-date with latest models.</summary>

1. GPT2-based [prompt expansion as a dynamic style "Fooocus V2".](https://github.com/lllyasviel/Fooocus/discussions/117#raw) (similar to Midjourney's hidden pre-processing and "raw" mode, or the LeonardoAI's Prompt Magic).
2. Native refiner swap inside one single k-sampler. The advantage is that the refiner model can now reuse the base model's momentum (or ODE's history parameters) collected from k-sampling to achieve more coherent sampling. In Automatic1111's high-res fix and ComfyUI's node system, the base model and refiner use two independent k-samplers, which means the momentum is largely wasted, and the sampling continuity is broken. Fooocus uses its own advanced k-diffusion sampling that ensures seamless, native, and continuous swap in a refiner setup. (Update Aug 13: Actually, I discussed this with Automatic1111 several days ago, and it seems that the “native refiner swap inside one single k-sampler” is [merged](https://github.com/AUTOMATIC1111/stable-diffusion-webui/pull/12371) into the dev branch of webui. Great!)
3. Negative ADM guidance. Because the highest resolution level of XL Base does not have cross attentions, the positive and negative signals for XL's highest resolution level cannot receive enough contrasts during the CFG sampling, causing the results to look a bit plastic or overly smooth in certain cases. Fortunately, since the XL's highest resolution level is still conditioned on image aspect ratios (ADM), we can modify the adm on the positive/negative side to compensate for the lack of CFG contrast in the highest resolution level. (Update Aug 16, the IOS App [Draw Things](https://apps.apple.com/us/app/draw-things-ai-generation/id6444050820) will support Negative ADM Guidance. Great!)
4. We implemented a carefully tuned variation of Section 5.1 of ["Improving Sample Quality of Diffusion Models Using Self-Attention Guidance"](https://arxiv.org/pdf/2210.00939.pdf). The weight is set to very low, but this is Fooocus's final guarantee to make sure that the XL will never yield an overly smooth or plastic appearance (examples [here](https://github.com/lllyasviel/Fooocus/discussions/117#sharpness)). This can almost eliminate all cases for which XL still occasionally produces overly smooth results, even with negative ADM guidance. (Update 2023 Aug 18, the Gaussian kernel of SAG is changed to an anisotropic kernel for better structure preservation and fewer artifacts.)
5. We modified the style templates a bit and added the "cinematic-default".
6. We tested the "sd_xl_offset_example-lora_1.0.safetensors" and it seems that when the lora weight is below 0.5, the results are always better than XL without lora.
7. The parameters of samplers are carefully tuned.
8. Because XL uses positional encoding for generation resolution, images generated by several fixed resolutions look a bit better than those from arbitrary resolutions (because the positional encoding is not very good at handling int numbers that are unseen during training). This suggests that the resolutions in UI may be hard coded for best results.
9. Separated prompts for two different text encoders seem unnecessary. Separated prompts for the base model and refiner may work, but the effects are random, and we refrain from implementing this.
10. The DPM family seems well-suited for XL since XL sometimes generates overly smooth texture, but the DPM family sometimes generates overly dense detail in texture. Their joint effect looks neutral and appealing to human perception.
11. A carefully designed system for balancing multiple styles as well as prompt expansion.
12. Using automatic1111's method to normalize prompt emphasizing. This significantly improves results when users directly copy prompts from civitai.
13. The joint swap system of the refiner now also supports img2img and upscale in a seamless way.
14. CFG Scale and TSNR correction (tuned for SDXL) when CFG is bigger than 10.

</details>

## Customization

- TBA
  ``

## Current todo

- [ ] Convert presets to new format including usage of bools isntead of -1
- [ ] Isolate model managment and assaign cuda devices based on available devices
- [ ] Implement api for generating images
- [ ] Implement a basic example of using the api
- [ ] Add documentation
- [ ] Remove reduntant subdicts from LaunchArguments
- [ ] Remove all global vars
- [ ] Update MERGED_ARGS to be used everywhere, get rid of old args
- [ ] Get a thread for viewing images. Some kind of a streaming POST-endpoint for viewing images would be nice, I'll build it later.
- [ ] Flux support
- [ ] Isolate model management
- [ ] Isolate patch insertion
- [ ] Multi-gpu support using accelerate
- [ ] Automatic configuration on the first run
- [ ] Config rewrtie (isolate launch args to their own file)
- [ ] Api with a streaming response and in memory image stream 
- [ ] Auth for the api
- [ ] Progress bar management, move to tqdm
- [ ] Remove hanging code
- [ ] Improve memory cleanup
- [ ] Figure out global interrupt mutex. Redundant for now as the app is single threaded


# Long term nice to haves
- [ ] Dockerize


### API roadmap
