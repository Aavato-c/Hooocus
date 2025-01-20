from enum import Enum
import os, sys

curr_dirr = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, curr_dirr.split("h3_utils")[0])


from typing import Literal, Optional
from click import style
from pydantic import BaseModel

from h3_utils.path_configs import FolderPathsConfig


sample_img_path = FolderPathsConfig.path_prompt_style_samples


VALID_STYLE_NAMES = Literal[
    "Fooocus_V2",
    "Fooocus_Cinematic",
    "Fooocus_Enhance",
    "Fooocus_Masterpiece",
    "Fooocus_Negative",
    "Fooocus_Photograph",
    "Fooocus_Pony",
    "Fooocus_Semi_Realistic",
    "Fooocus_Sharp",
    "Abstract_Expressionism",
    "Academia",
    "Action_Figure",
    "Adorable_Kawaii",
    "Adorable_3D_Character",
    "Art_Deco",
    "Art_Nouveau",
    "Astral_Aura",
    "Avant_garde",
    "Baroque",
    "Bauhaus_Style_Poster",
    "Blueprint_Schematic_Drawing",
    "Caricature",
    "Cel_Shaded_Art",
    "Character_Design_Sheet",
    "Cinematic_Diva",
    "Classicism_Art",
    "Color_Field_Painting",
    "Colored_Pencil_Art",
    "Conceptual_Art",
    "Constructivism",
    "Cubism",
    "DMT_Art_Style",
    "Dadaism",
    "Dark_Fantasy",
    "Dark_Moody_Atmosphere",
    "Doodle_Art",
    "Double_Exposure",
    "Dripping_Paint_Splatter_Art",
    "Expressionism",
    "Faded_Polaroid_Photo",
    "Fauvism",
    "Flat_2D_Art",
    "Fortnite_Art_Style",
    "Futurism",
    "Glitchcore",
    "Glo_fi",
    "Googie_Art_Style",
    "Graffiti_Art",
    "Harlem_Renaissance_Art",
    "High_Fashion",
    "Idyllic",
    "Impressionism",
    "Infographic_Drawing",
    "Ink_Dripping_Drawing",
    "Japanese_Ink_Drawing",
    "Knolling_Photography",
    "Light_Cheery_Atmosphere",
    "Logo_Design",
    "Luxurious_Elegance",
    "Macro_Photography",
    "Mandola_Art",
    "Marker_Drawing",
    "Medievalism",
    "Minimalism",
    "Neo_Baroque",
    "Neo_Byzantine",
    "Neo_Futurism",
    "Neo_Impressionism",
    "Neo_Rococo",
    "Neoclassicism",
    "Op_Art",
    "Ornate_and_Intricate",
    "Pencil_Sketch_Drawing",
    "Pop_Art_2",
    "Rococo",
    "Silhouette_Art",
    "Simple_Vector_Art",
    "Sketchup",
    "Steampunk_2",
    "Sticker_Designs",
    "Suprematism",
    "Surrealism",
    "Terragen",
    "Tranquil_Relaxing_Atmosphere",
    "Vibrant_Rim_Light",
    "Volumetric_Lighting",
    "Watercolor_2",
    "Whimsical_and_Playful",
    "MK_Albumen_Print",
    "MK_Alcohol_Ink_Art",
    "MK_Andy_Warhol",
    "MK_Anthotype_Print",
    "MK_Aquatint_Print",
    "MK_Basquiat",
    "MK_Blacklight_Paint",
    "MK_Bromoil_Print",
    "MK_Calotype_Print",
    "MK_Carnival_Glass",
    "MK_Chromolithography",
    "MK_Cibulak_Porcelain",
    "MK_Color_Sketchnote",
    "MK_Coloring_Book",
    "MK_Cross_Processing_Print",
    "MK_Cross_Stitching",
    "MK_Cyanotype_Print",
    "MK_Dufaycolor_Photograph",
    "MK_Embroidery",
    "MK_Encaustic_Paint",
    "MK_Gond_Painting",
    "MK_Gyotaku",
    "MK_Halftone_print",
    "MK_Herbarium",
    "MK_Inuit_Carving",
    "MK_Lite_Brite_Art",
    "MK_Luminogram",
    "MK_Mokume_gane",
    "MK_One_Line_Art",
    "MK_Palekh",
    "MK_Pollock",
    "MK_Punk_Collage",
    "MK_Scrimshaw",
    "MK_Shibori",
    "MK_Singer_Sargent",
    "MK_Suminagashi",
    "MK_Ukiyo_e",
    "MK_Van_Gogh",
    "MK_Vitreous_Enamel",
    "MK_adnate_style",
    "MK_afrofuturism",
    "MK_atompunk",
    "MK_bauhaus_style",
    "MK_chicano_art",
    "MK_constructivism",
    "MK_dayak_art",
    "MK_de_stijl",
    "MK_fayum_portrait",
    "MK_illuminated_manuscript",
    "MK_kalighat_painting",
    "MK_madhubani_painting",
    "MK_mosaic",
    "MK_patachitra_painting",
    "MK_pichwai_painting",
    "MK_pictorialism",
    "MK_ron_english_style",
    "MK_samoan_art_inspired",
    "MK_shepard_fairey_style",
    "MK_tlingit_art",
    "MK_vintage_airline_poster",
    "MK_vintage_travel_poster",
    "Pebble_Art",
    "mre_ancient_illustration",
    "mre_anime",
    "mre_artistic_vision",
    "mre_bad_dream",
    "mre_brave_art",
    "mre_cinematic_dynamic",
    "mre_comic",
    "mre_dark_cyberpunk",
    "mre_dark_dream",
    "mre_dynamic_illustration",
    "mre_elemental_art",
    "mre_gloomy_art",
    "mre_heroic_fantasy",
    "mre_lyrical_geometry",
    "mre_manga",
    "mre_space_art",
    "mre_spontaneous_picture",
    "mre_sumi_e_detailed",
    "mre_sumi_e_symbolic",
    "mre_surreal_painting",
    "mre_undead_art",
    "mre_underground",
    "sai_3d_model",
    "sai_analog_film",
    "sai_anime",
    "sai_cinematic",
    "sai_comic_book",
    "sai_craft_clay",
    "sai_digital_art",
    "sai_enhance",
    "sai_fantasy_art",
    "sai_isometric",
    "sai_line_art",
    "sai_lowpoly",
    "sai_neonpunk",
    "sai_origami",
    "sai_photographic",
    "sai_pixel_art",
    "sai_texture",
    "ads_advertising",
    "ads_automotive",
    "ads_corporate",
    "ads_fashion_editorial",
    "ads_food_photography",
    "ads_gourmet_food_photography",
    "ads_luxury",
    "ads_real_estate",
    "ads_retail",
    "artstyle_abstract",
    "artstyle_abstract_expressionism",
    "artstyle_art_deco",
    "artstyle_art_nouveau",
    "artstyle_constructivist",
    "artstyle_cubist",
    "artstyle_expressionist",
    "artstyle_graffiti",
    "artstyle_hyperrealism",
    "artstyle_impressionist",
    "artstyle_pointillism",
    "artstyle_pop_art",
    "artstyle_psychedelic",
    "artstyle_renaissance",
    "artstyle_steampunk",
    "artstyle_surrealist",
    "artstyle_typography",
    "artstyle_watercolor",
    "futuristic_biomechanical",
    "futuristic_biomechanical_cyberpunk",
    "futuristic_cybernetic",
    "futuristic_cybernetic_robot",
    "futuristic_cyberpunk_cityscape",
    "futuristic_futuristic",
    "futuristic_retro_cyberpunk",
    "futuristic_retro_futurism",
    "futuristic_sci_fi",
    "futuristic_vaporwave",
    "game_bubble_bobble",
    "game_cyberpunk_game",
    "game_fighting_game",
    "game_gta",
    "game_mario",
    "game_minecraft",
    "game_pokemon",
    "game_retro_arcade",
    "game_retro_game",
    "game_rpg_fantasy_game",
    "game_strategy_game",
    "game_streetfighter",
    "game_zelda",
    "misc_architectural",
    "misc_disco",
    "misc_dreamscape",
    "misc_dystopian",
    "misc_fairy_tale",
    "misc_gothic",
    "misc_grunge",
    "misc_horror",
    "misc_kawaii",
    "misc_lovecraftian",
    "misc_macabre",
    "misc_manga",
    "misc_metropolis",
    "misc_minimalist",
    "misc_monochrome",
    "misc_nautical",
    "misc_space",
    "misc_stained_glass",
    "misc_techwear_fashion",
    "misc_tribal",
    "misc_zentangle",
    "papercraft_collage",
    "papercraft_flat_papercut",
    "papercraft_kirigami",
    "papercraft_paper_mache",
    "papercraft_paper_quilling",
    "papercraft_papercut_collage",
    "papercraft_papercut_shadow_box",
    "papercraft_stacked_papercut",
    "papercraft_thick_layered_papercut",
    "photo_alien",
    "photo_film_noir",
    "photo_glamour",
    "photo_hdr",
    "photo_iphone_photographic",
    "photo_long_exposure",
    "photo_neon_noir",
    "photo_silhouette",
    "photo_tilt_shift",
]


class PromptStyle(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    sample_image_path: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sample_image_path = (
            f"{sample_img_path}{self.name.lower()}.jpg" if self.name else None
        )


class Fooocus(Enum):

    ALL_NAMES = [
        "Fooocus_Cinematic",
        "Fooocus_V2",
        "Fooocus_Enhance",
        "Fooocus_Masterpiece",
        "Fooocus_Negative",
        "Fooocus_Photograph",
        "Fooocus_Pony",
        "Fooocus_Semi_Realistic",
        "Fooocus_Sharp",
    ]

    """@classmethod
    def all_style_names(cls):
        all_names = []
        for style in dir(cls):
            if isinstance(getattr(cls, style), PromptStyle):
                all_names.append(getattr(cls, style).name)
        return all_names
     """
    
    Fooocus_V2 = PromptStyle(
        name="Fooocus_V2"
    )

    Fooocus_Enhance = PromptStyle(
        name="Fooocus_Enhance",
        negative_prompt="(worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed, grayscale, bw, bad photo, bad photography, bad art:1.4), (watermark, signature, text font, username, error, logo, words, letters, digits, autograph, trademark, name:1.2), (blur, blurry, grainy), morbid, ugly, asymmetrical, mutated malformed, mutilated, poorly lit, bad shadow, draft, cropped, out of frame, cut off, censored, jpeg artifacts, out of focus, glitch, duplicate, (airbrushed, cartoon, anime, semi-realistic, cgi, render, blender, digital art, manga, amateur:1.3), (3D ,3D Game, 3D Game Scene, 3D Character:1.1), (bad hands, bad anatomy, bad body, bad face, bad teeth, bad arms, bad legs, deformities:1.3)",
    )

    Fooocus_Semi_Realistic = PromptStyle(
        name="Fooocus_Semi_Realistic",
        negative_prompt="(worst quality, low quality, normal quality, lowres, low details, oversaturated, undersaturated, overexposed, underexposed, bad photo, bad photography, bad art:1.4), (watermark, signature, text font, username, error, logo, words, letters, digits, autograph, trademark, name:1.2), (blur, blurry, grainy), morbid, ugly, asymmetrical, mutated malformed, mutilated, poorly lit, bad shadow, draft, cropped, out of frame, cut off, censored, jpeg artifacts, out of focus, glitch, duplicate, (bad hands, bad anatomy, bad body, bad face, bad teeth, bad arms, bad legs, deformities:1.3)",
    )

    Fooocus_Sharp = PromptStyle(
        name="Fooocus_Sharp",
        prompt="cinematic still {prompt} . emotional, harmonious, vignette, 4k epic detailed, shot on kodak, 35mm photo, sharp focus, high budget, cinemascope, moody, epic, gorgeous, film grain, grainy",
        negative_prompt="anime, cartoon, graphic, (blur, blurry, bokeh), text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
    )

    Fooocus_Masterpiece = PromptStyle(
        name="Fooocus_Masterpiece",
        prompt="(masterpiece), (best quality), (ultra-detailed), {prompt}, illustration, disheveled hair, detailed eyes, perfect composition, moist skin, intricate details, earrings",
        negative_prompt="longbody, lowres, bad anatomy, bad hands, missing fingers, pubic hair,extra digit, fewer digits, cropped, worst quality, low quality",
    )

    Fooocus_Photograph = PromptStyle(
        name="Fooocus_Photograph",
        prompt="photograph {prompt}, 50mm . cinematic 4k epic detailed 4k epic detailed photograph shot on kodak detailed cinematic hbo dark moody, 35mm photo, grainy, vignette, vintage, Kodachrome, Lomography, stained, highly detailed, found footage",
        negative_prompt="Brad Pitt, bokeh, depth of field, blurry, cropped, regular face, saturated, contrast, deformed iris, deformed pupils, semi-realistic, cgi, 3d, render, sketch, cartoon, drawing, anime, text, cropped, out of frame, worst quality, low quality, jpeg artifacts, ugly, duplicate, morbid, mutilated, extra fingers, mutated hands, poorly drawn hands, poorly drawn face, mutation, deformed, dehydrated, bad anatomy, bad proportions, extra limbs, cloned face, disfigured, gross proportions, malformed limbs, missing arms, missing legs, extra arms, extra legs, fused fingers, too many fingers, long neck",
    )

    Fooocus_Negative = PromptStyle(
        name="Fooocus_Negative",
        negative_prompt="deformed, bad anatomy, disfigured, poorly drawn face, mutated, extra limb, ugly, poorly drawn hands, missing limb, floating limbs, disconnected limbs, disconnected head, malformed hands, long neck, mutated hands and fingers, bad hands, missing fingers, cropped, worst quality, low quality, mutation, poorly drawn, huge calf, bad hands, fused hand, missing hand, disappearing arms, disappearing thigh, disappearing calf, disappearing legs, missing fingers, fused fingers, abnormal eye proportion, Abnormal hands, abnormal legs, abnormal feet, abnormal fingers, drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly, anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch",
    )

    Fooocus_Cinematic = PromptStyle(
        name="Fooocus_Cinematic",
        prompt="cinematic still {prompt} . emotional, harmonious, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy",
        negative_prompt="anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
    )

    Fooocus_Pony = PromptStyle(
        name="Fooocus_Pony",
        prompt="score_9, score_8_up, score_7_up, {prompt}",
        negative_prompt="score_6, score_5, score_4",
    )

class Diva(Enum):
    
    ALL_NAMES = [
        "Abstract_Expressionism",
        "Academia",
        "Action_Figure",
        "Adorable_Kawaii",
        "Adorable_3D_Character",
        "Art_Deco",
        "Art_Nouveau",
        "Astral_Aura",
        "Avant_garde",
        "Baroque",
        "Bauhaus_Style_Poster",
        "Blueprint_Schematic_Drawing",
        "Caricature",
        "Cel_Shaded_Art",
        "Character_Design_Sheet",
        "Cinematic_Diva",
        "Classicism_Art",
        "Color_Field_Painting",
        "Colored_Pencil_Art",
        "Conceptual_Art",
        "Constructivism",
        "Cubism",
        "DMT_Art_Style",
        "Dadaism",
        "Dark_Fantasy",
        "Dark_Moody_Atmosphere",
        "Doodle_Art",
        "Double_Exposure",
        "Dripping_Paint_Splatter_Art",
        "Expressionism",
        "Faded_Polaroid_Photo",
        "Fauvism",
        "Flat_2D_Art",
        "Fortnite_Art_Style",
        "Futurism",
        "Glitchcore",
        "Glo_fi",
        "Googie_Art_Style",
        "Graffiti_Art",
        "Harlem_Renaissance_Art",
        "High_Fashion",
        "Idyllic",
        "Impressionism",
        "Infographic_Drawing",
        "Ink_Dripping_Drawing",
        "Japanese_Ink_Drawing",
        "Knolling_Photography",
        "Light_Cheery_Atmosphere",
        "Logo_Design",
        "Luxurious_Elegance",
        "Macro_Photography",
        "Mandola_Art",
        "Marker_Drawing",
        "Medievalism",
        "Minimalism",
        "Neo_Baroque",
        "Neo_Byzantine",
        "Neo_Futurism",
        "Neo_Impressionism",
        "Neo_Rococo",
        "Neoclassicism",
        "Op_Art",
        "Ornate_and_Intricate",
        "Pencil_Sketch_Drawing",
        "Pop_Art_2",
        "Rococo",
        "Silhouette_Art",
        "Simple_Vector_Art",
        "Sketchup",
        "Steampunk_2",
        "Sticker_Designs",
        "Suprematism",
        "Surrealism",
        "Terragen",
        "Tranquil_Relaxing_Atmosphere",
        "Vibrant_Rim_Light",
        "Volumetric_Lighting",
        "Watercolor_2",
        "Whimsical_and_Playful",
    ]

    Cinematic_Diva = PromptStyle(
        name="Cinematic_Diva",
        prompt="UHD, 8K, ultra detailed, a cinematic photograph of {prompt}, beautiful lighting, great composition",
        negative_prompt="ugly, deformed, noisy, blurry, NSFW",
    )

    Abstract_Expressionism = PromptStyle(
        name="Abstract_Expressionism",
        prompt="Abstract Expressionism Art, {prompt}, High contrast, minimalistic, colorful, stark, dramatic, expressionism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic",
    )

    Academia = PromptStyle(
        name="Academia",
        prompt="Academia, {prompt}, preppy Ivy League style, stark, dramatic, chic boarding school, academia",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, grunge, sloppy, unkempt",
    )

    Action_Figure = PromptStyle(
        name="Action_Figure",
        prompt="Action Figure, {prompt}, plastic collectable action figure, collectable toy action figure",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Adorable_3D_Character = PromptStyle(
        name="Adorable_3D_Character",
        prompt="Adorable 3D Character, {prompt}, 3D render, adorable character, 3D art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, grunge, sloppy, unkempt, photograph, photo, realistic",
    )

    Adorable_Kawaii = PromptStyle(
        name="Adorable_Kawaii",
        prompt="Adorable Kawaii, {prompt}, pretty, cute, adorable, kawaii",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, gothic, dark, moody, monochromatic",
    )

    Art_Deco = PromptStyle(
        name="Art_Deco",
        prompt="Art Deco, {prompt}, sleek, geometric forms, art deco style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Art_Nouveau = PromptStyle(
        name="Art_Nouveau",
        prompt="Art Nouveau, beautiful art, {prompt}, sleek, organic forms, long, sinuous, art nouveau style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, industrial, mechanical",
    )

    Astral_Aura = PromptStyle(
        name="Astral_Aura",
        prompt="Astral Aura, {prompt}, astral, colorful aura, vibrant energy",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Avant_garde = PromptStyle(
        name="Avant_garde",
        prompt="Avant-garde, {prompt}, unusual, experimental, avant-garde art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Baroque = PromptStyle(
        name="Baroque",
        prompt="Baroque, {prompt}, dramatic, exuberant, grandeur, baroque art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Bauhaus_Style_Poster = PromptStyle(
        name="Bauhaus_Style_Poster",
        prompt="Bauhaus-Style Poster, {prompt}, simple geometric shapes, clean lines, primary colors, Bauhaus-Style Poster",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Blueprint_Schematic_Drawing = PromptStyle(
        name="Blueprint_Schematic_Drawing",
        prompt="Blueprint Schematic Drawing, {prompt}, technical drawing, blueprint, schematic",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Caricature = PromptStyle(
        name="Caricature",
        prompt="Caricature, {prompt}, exaggerated, comical, caricature",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realistic",
    )

    Cel_Shaded_Art = PromptStyle(
        name="Cel_Shaded_Art",
        prompt="Cel Shaded Art, {prompt}, 2D, flat color, toon shading, cel shaded style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Character_Design_Sheet = PromptStyle(
        name="Character_Design_Sheet",
        prompt="Character Design Sheet, {prompt}, character reference sheet, character turn around",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Classicism_Art = PromptStyle(
        name="Classicism_Art",
        prompt="Classicism Art, {prompt}, inspired by Roman and Greek culture, clarity, harmonious, classicism art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Color_Field_Painting = PromptStyle(
        name="Color_Field_Painting",
        prompt="Color Field Painting, {prompt}, abstract, simple, geometic, color field painting style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Colored_Pencil_Art = PromptStyle(
        name="Colored_Pencil_Art",
        prompt="Colored Pencil Art, {prompt}, colored pencil strokes, light color, visible paper texture, colored pencil art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Conceptual_Art = PromptStyle(
        name="Conceptual_Art",
        prompt="Conceptual Art, {prompt}, concept art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Constructivism = PromptStyle(
        name="Constructivism",
        prompt="Constructivism Art, {prompt}, minimalistic, geometric forms, constructivism art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Cubism = PromptStyle(
        name="Cubism",
        prompt="Cubism Art, {prompt}, flat geometric forms, cubism art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Dadaism = PromptStyle(
        name="Dadaism",
        prompt="Dadaism Art, {prompt}, satirical, nonsensical, dadaism art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Dark_Fantasy = PromptStyle(
        name="Dark_Fantasy",
        prompt="Dark Fantasy Art, {prompt}, dark, moody, dark fantasy style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, bright, sunny",
    )

    Dark_Moody_Atmosphere = PromptStyle(
        name="Dark_Moody_Atmosphere",
        prompt="Dark Moody Atmosphere, {prompt}, dramatic, mysterious, dark moody atmosphere",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, vibrant, colorful, bright",
    )

    DMT_Art_Style = PromptStyle(
        name="DMT_Art_Style",
        prompt="DMT Art Style, {prompt}, bright colors, surreal visuals, swirling patterns, DMT art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Doodle_Art = PromptStyle(
        name="Doodle_Art",
        prompt="Doodle Art Style, {prompt}, drawing, freeform, swirling patterns, doodle art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Double_Exposure = PromptStyle(
        name="Double_Exposure",
        prompt="Double Exposure Style, {prompt}, double image ghost effect, image combination, double exposure style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Dripping_Paint_Splatter_Art = PromptStyle(
        name="Dripping_Paint_Splatter_Art",
        prompt="Dripping Paint Splatter Art, {prompt}, dramatic, paint drips, splatters, dripping paint",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Expressionism = PromptStyle(
        name="Expressionism",
        prompt="Expressionism Art Style, {prompt}, movement, contrast, emotional, exaggerated forms, expressionism art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Faded_Polaroid_Photo = PromptStyle(
        name="Faded_Polaroid_Photo",
        prompt="Faded Polaroid Photo, {prompt}, analog, old faded photo, old polaroid",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, vibrant, colorful",
    )

    Fauvism = PromptStyle(
        name="Fauvism",
        prompt="Fauvism Art, {prompt}, painterly, bold colors, textured brushwork, fauvism art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Flat_2D_Art = PromptStyle(
        name="Flat_2D_Art",
        prompt="Flat 2D Art, {prompt}, simple flat color, 2-dimensional, Flat 2D Art Style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, 3D, photo, realistic",
    )

    Fortnite_Art_Style = PromptStyle(
        name="Fortnite_Art_Style",
        prompt="Fortnite Art Style, {prompt}, 3D cartoon, colorful, Fortnite Art Style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, photo, realistic",
    )

    Futurism = PromptStyle(
        name="Futurism",
        prompt="Futurism Art Style, {prompt}, dynamic, dramatic, Futurism Art Style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Glitchcore = PromptStyle(
        name="Glitchcore",
        prompt="Glitchcore Art Style, {prompt}, dynamic, dramatic, distorted, vibrant colors, glitchcore art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Glo_fi = PromptStyle(
        name="Glo_fi",
        prompt="Glo-fi Art Style, {prompt}, dynamic, dramatic, vibrant colors, glo-fi art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Googie_Art_Style = PromptStyle(
        name="Googie_Art_Style",
        prompt="Googie Art Style, {prompt}, dynamic, dramatic, 1950's futurism, bold boomerang angles, Googie art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Graffiti_Art = PromptStyle(
        name="Graffiti_Art",
        prompt="Graffiti Art Style, {prompt}, dynamic, dramatic, vibrant colors, graffiti art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Harlem_Renaissance_Art = PromptStyle(
        name="Harlem_Renaissance_Art",
        prompt="Harlem Renaissance Art Style, {prompt}, dynamic, dramatic, 1920s African American culture, Harlem Renaissance art style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    High_Fashion = PromptStyle(
        name="High_Fashion",
        prompt="High Fashion, {prompt}, dynamic, dramatic, haute couture, elegant, ornate clothing, High Fashion",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Idyllic = PromptStyle(
        name="Idyllic",
        prompt="Idyllic, {prompt}, peaceful, happy, pleasant, happy, harmonious, picturesque, charming",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Impressionism = PromptStyle(
        name="Impressionism",
        prompt="Impressionism, {prompt}, painterly, small brushstrokes, visible brushstrokes, impressionistic style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Infographic_Drawing = PromptStyle(
        name="Infographic_Drawing",
        prompt="Infographic Drawing, {prompt}, diagram, infographic",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Ink_Dripping_Drawing = PromptStyle(
        name="Ink_Dripping_Drawing",
        prompt="Ink Dripping Drawing, {prompt}, ink drawing, dripping ink",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, colorful, vibrant",
    )

    Japanese_Ink_Drawing = PromptStyle(
        name="Japanese_Ink_Drawing",
        prompt="Japanese Ink Drawing, {prompt}, ink drawing, inkwash, Japanese Ink Drawing",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, colorful, vibrant",
    )

    Knolling_Photography = PromptStyle(
        name="Knolling_Photography",
        prompt="Knolling Photography, {prompt}, flat lay photography, object arrangment, knolling photography",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Light_Cheery_Atmosphere = PromptStyle(
        name="Light_Cheery_Atmosphere",
        prompt="Light Cheery Atmosphere, {prompt}, happy, joyful, cheerful, carefree, gleeful, lighthearted, pleasant atmosphere",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, monochromatic, dark, moody",
    )

    Logo_Design = PromptStyle(
        name="Logo_Design",
        prompt="Logo Design, {prompt}, dynamic graphic art, vector art, minimalist, professional logo design",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Luxurious_Elegance = PromptStyle(
        name="Luxurious_Elegance",
        prompt="Luxurious Elegance, {prompt}, extravagant, ornate, designer, opulent, picturesque, lavish",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Macro_Photography = PromptStyle(
        name="Macro_Photography",
        prompt="Macro Photography, {prompt}, close-up, macro 100mm, macro photography",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Mandola_Art = PromptStyle(
        name="Mandola_Art",
        prompt="Mandola art style, {prompt}, complex, circular design, mandola",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Marker_Drawing = PromptStyle(
        name="Marker_Drawing",
        prompt="Marker Drawing, {prompt}, bold marker lines, visibile paper texture, marker drawing",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, photograph, realistic",
    )

    Medievalism = PromptStyle(
        name="Medievalism",
        prompt="Medievalism, {prompt}, inspired by The Middle Ages, medieval art, elaborate patterns and decoration, Medievalism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Minimalism = PromptStyle(
        name="Minimalism",
        prompt="Minimalism, {prompt}, abstract, simple geometic shapes, hard edges, sleek contours, Minimalism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Neo_Baroque = PromptStyle(
        name="Neo_Baroque",
        prompt="Neo-Baroque, {prompt}, ornate and elaborate, dynaimc, Neo-Baroque",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Neo_Byzantine = PromptStyle(
        name="Neo_Byzantine",
        prompt="Neo-Byzantine, {prompt}, grand decorative religious style, Orthodox Christian inspired, Neo-Byzantine",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Neo_Futurism = PromptStyle(
        name="Neo_Futurism",
        prompt="Neo-Futurism, {prompt}, high-tech, curves, spirals, flowing lines, idealistic future, Neo-Futurism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Neo_Impressionism = PromptStyle(
        name="Neo_Impressionism",
        prompt="Neo-Impressionism, {prompt}, tiny dabs of color, Pointillism, painterly, Neo-Impressionism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, photograph, realistic",
    )

    Neo_Rococo = PromptStyle(
        name="Neo_Rococo",
        prompt="Neo-Rococo, {prompt}, curved forms, naturalistic ornamentation, elaborate, decorative, gaudy, Neo-Rococo",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Neoclassicism = PromptStyle(
        name="Neoclassicism",
        prompt="Neoclassicism, {prompt}, ancient Rome and Greece inspired, idealic, sober colors, Neoclassicism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Op_Art = PromptStyle(
        name="Op_Art",
        prompt="Op Art, {prompt}, optical illusion, abstract, geometric pattern, impression of movement, Op Art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Ornate_and_Intricate = PromptStyle(
        name="Ornate_and_Intricate",
        prompt="Ornate and Intricate, {prompt}, decorative, highly detailed, elaborate, ornate, intricate",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Pencil_Sketch_Drawing = PromptStyle(
        name="Pencil_Sketch_Drawing",
        prompt="Pencil Sketch Drawing, {prompt}, black and white drawing, graphite drawing",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Pop_Art_2 = PromptStyle(
        name="Pop_Art_2",
        prompt="Pop Art, {prompt}, vivid colors, flat color, 2D, strong lines, Pop Art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, photo, realistic",
    )

    Rococo = PromptStyle(
        name="Rococo",
        prompt="Rococo, {prompt}, flamboyant, pastel colors, curved lines, elaborate detail, Rococo",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Silhouette_Art = PromptStyle(
        name="Silhouette_Art",
        prompt="Silhouette Art, {prompt}, high contrast, well defined, Silhouette Art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Simple_Vector_Art = PromptStyle(
        name="Simple_Vector_Art",
        prompt="Simple Vector Art, {prompt}, 2D flat, simple shapes, minimalistic, professional graphic, flat color, high contrast, Simple Vector Art",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, 3D, photo, realistic",
    )

    Sketchup = PromptStyle(
        name="Sketchup",
        prompt="Sketchup, {prompt}, CAD, professional design, Sketchup",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, photo, photograph",
    )

    Steampunk_2 = PromptStyle(
        name="Steampunk_2",
        prompt="Steampunk, {prompt}, retrofuturistic science fantasy, steam-powered tech, vintage industry, gears, neo-victorian, steampunk",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Surrealism = PromptStyle(
        name="Surrealism",
        prompt="Surrealism, {prompt}, expressive, dramatic, organic lines and forms, dreamlike and mysterious, Surrealism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realistic",
    )

    Suprematism = PromptStyle(
        name="Suprematism",
        prompt="Suprematism, {prompt}, abstract, limited color palette, geometric forms, Suprematism",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realistic",
    )

    Terragen = PromptStyle(
        name="Terragen",
        prompt="Terragen, {prompt}, beautiful massive landscape, epic scenery, Terragen",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Tranquil_Relaxing_Atmosphere = PromptStyle(
        name="Tranquil_Relaxing_Atmosphere",
        prompt="Tranquil Relaxing Atmosphere, {prompt}, calming style, soothing colors, peaceful, idealic, Tranquil Relaxing Atmosphere",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, oversaturated",
    )

    Sticker_Designs = PromptStyle(
        name="Sticker_Designs",
        prompt="Vector Art Stickers, {prompt}, professional vector design, sticker designs, Sticker Sheet",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Vibrant_Rim_Light = PromptStyle(
        name="Vibrant_Rim_Light",
        prompt="Vibrant Rim Light, {prompt}, bright rim light, high contrast, bold edge light",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Volumetric_Lighting = PromptStyle(
        name="Volumetric_Lighting",
        prompt="Volumetric Lighting, {prompt}, light depth, dramatic atmospheric lighting, Volumetric Lighting",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast",
    )

    Watercolor_2 = PromptStyle(
        name="Watercolor_2",
        prompt="Watercolor style painting, {prompt}, visible paper texture, colorwash, watercolor",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, photo, realistic",
    )

    Whimsical_and_Playful = PromptStyle(
        name="Whimsical_and_Playful",
        prompt="Whimsical and Playful, {prompt}, imaginative, fantastical, bight colors, stylized, happy, Whimsical and Playful",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, drab, boring, moody",
    )


class Mark_K3nt3l(Enum):
    ALL_NAMES = [
        "MK_Albumen_Print",
        "MK_Alcohol_Ink_Art",
        "MK_Andy_Warhol",
        "MK_Anthotype_Print",
        "MK_Aquatint_Print",
        "MK_Basquiat",
        "MK_Blacklight_Paint",
        "MK_Bromoil_Print",
        "MK_Calotype_Print",
        "MK_Carnival_Glass",
        "MK_Chromolithography",
        "MK_Cibulak_Porcelain",
        "MK_Color_Sketchnote",
        "MK_Coloring_Book",
        "MK_Cross_Processing_Print",
        "MK_Cross_Stitching",
        "MK_Cyanotype_Print",
        "MK_Dufaycolor_Photograph",
        "MK_Embroidery",
        "MK_Encaustic_Paint",
        "MK_Gond_Painting",
        "MK_Gyotaku",
        "MK_Halftone_print",
        "MK_Herbarium",
        "MK_Inuit_Carving",
        "MK_Lite_Brite_Art",
        "MK_Luminogram",
        "MK_Mokume_gane",
        "MK_One_Line_Art",
        "MK_Palekh",
        "MK_Pollock",
        "MK_Punk_Collage",
        "MK_Scrimshaw",
        "MK_Shibori",
        "MK_Singer_Sargent",
        "MK_Suminagashi",
        "MK_Ukiyo_e",
        "MK_Van_Gogh",
        "MK_Vitreous_Enamel",
        "MK_adnate_style",
        "MK_afrofuturism",
        "MK_atompunk",
        "MK_bauhaus_style",
        "MK_chicano_art",
        "MK_constructivism",
        "MK_dayak_art",
        "MK_de_stijl",
        "MK_fayum_portrait",
        "MK_illuminated_manuscript",
        "MK_kalighat_painting",
        "MK_madhubani_painting",
        "MK_mosaic",
        "MK_patachitra_painting",
        "MK_pichwai_painting",
        "MK_pictorialism",
        "MK_ron_english_style",
        "MK_samoan_art_inspired",
        "MK_shepard_fairey_style",
        "MK_tlingit_art",
        "MK_vintage_airline_poster",
        "MK_vintage_travel_poster",
        "Pebble_Art",
    ]

    MK_Chromolithography = PromptStyle(
        name="MK_Chromolithography",
        prompt="Chromolithograph {prompt}. Vibrant colors, intricate details, rich color saturation, meticulous registration, multi-layered printing, decorative elements, historical charm, artistic reproductions, commercial posters, nostalgic, ornate compositions.",
        negative_prompt="monochromatic, simple designs, limited color palette, imprecise registration, minimalistic, modern aesthetic, digital appearance.",
    )

    MK_Cross_Processing_Print = PromptStyle(
        name="MK_Cross_Processing_Print",
        prompt="Cross processing print {prompt}. Experimental color shifts, unconventional tonalities, vibrant and surreal hues, heightened contrasts, unpredictable results, artistic unpredictability, retro and vintage feel, dynamic color interplay, abstract and dreamlike.",
        negative_prompt="predictable color tones, traditional processing, realistic color representation, subdued contrasts, standard photographic aesthetics.",
    )

    MK_Dufaycolor_Photograph = PromptStyle(
        name="MK_Dufaycolor_Photograph",
        prompt="Dufaycolor photograph {prompt}. Vintage color palette, distinctive color rendering, soft and dreamy atmosphere, historical charm, unique color process, grainy texture, evocative mood, nostalgic aesthetic, hand-tinted appearance, artistic patina.",
        negative_prompt="modern color reproduction, hyperrealistic tones, sharp and clear details, digital precision, contemporary aesthetic.",
    )

    MK_Herbarium = PromptStyle(
        name="MK_Herbarium",
        prompt="Herbarium drawing{prompt}. Botanical accuracy, old botanical book illustration, detailed illustrations, pressed plants, delicate and precise linework, scientific documentation, meticulous presentation, educational purpose, organic compositions, timeless aesthetic, naturalistic beauty.",
        negative_prompt="abstract representation, vibrant colors, artistic interpretation, chaotic compositions, fantastical elements, digital appearance.",
    )

    MK_Punk_Collage = PromptStyle(
        name="MK_Punk_Collage",
        prompt="punk collage style {prompt} . mixed media, papercut,textured paper, overlapping, ripped posters, safety pins, chaotic layers, graffiti-style elements, anarchy symbols, vintage photos, cut-and-paste aesthetic, bold typography, distorted images, political messages, urban decay, distressed textures, newspaper clippings, spray paint, rebellious icons, DIY spirit, vivid colors, punk band logos, edgy and raw compositions, ",
        negative_prompt="conventional,blurry, noisy, low contrast",
    )

    MK_mosaic = PromptStyle(
        name="MK_mosaic",
        prompt="mosaic style {prompt} . fragmented, assembled, colorful, highly detailed",
        negative_prompt="whole, unbroken, monochrome",
    )

    MK_Van_Gogh = PromptStyle(
        name="MK_Van_Gogh",
        prompt="Oil painting by Van Gogh {prompt} . Expressive, impasto, swirling brushwork, vibrant, brush strokes, Brushstroke-heavy, Textured, Impasto, Colorful, Dynamic, Bold, Distinctive, Vibrant, Whirling, Expressive, Dramatic, Swirling, Layered, Intense, Contrastive, Atmospheric, Luminous, Textural, Evocative, SpiraledVan Gogh style",
        negative_prompt="realistic, photorealistic, calm, straight lines, signature, frame, text, watermark",
    )

    MK_Coloring_Book = PromptStyle(
        name="MK_Coloring_Book",
        prompt="centered black and white high contrast line drawing, coloring book style,{prompt} . monochrome, blank white background",
        negative_prompt="greyscale, gradients,shadows,shadow, colored, Red, Blue, Yellow, Green, Orange, Purple, Pink, Brown, Gray, Beige, Turquoise, Lavender, Cyan, Magenta, Olive, Indigo, black background",
    )

    MK_Singer_Sargent = PromptStyle(
        name="MK_Singer_Sargent",
        prompt="Oil painting by John Singer Sargent {prompt}. Elegant, refined, masterful technique,realistic portrayal, subtle play of light, captivating expression, rich details, harmonious colors, skillful composition, brush strokes, chiaroscuro.",
        negative_prompt="realistic, photorealistic, abstract, overly stylized, excessive contrasts, distorted,bright colors,disorder.",
    )

    MK_Pollock = PromptStyle(
        name="MK_Pollock",
        prompt="Oil painting by Jackson Pollock {prompt}. Abstract expressionism, drip painting, chaotic composition, energetic, spontaneous, unconventional technique, dynamic, bold, distinctive, vibrant, intense, expressive, energetic, layered, non-representational, gestural.",
        negative_prompt="(realistic:1.5), (photorealistic:1.5), representational, calm, ordered composition, precise lines, detailed forms, subdued colors, quiet, static, traditional, figurative.",
    )

    MK_Basquiat = PromptStyle(
        name="MK_Basquiat",
        prompt="Artwork by Jean-Michel Basquiat {prompt}. Neo-expressionism, street art influence, graffiti-inspired, raw, energetic, bold colors, dynamic composition, chaotic, layered, textural, expressive, spontaneous, distinctive, symbolic,energetic brushstrokes.",
        negative_prompt="(realistic:1.5), (photorealistic:1.5), calm, precise lines, conventional composition, subdued",
    )

    MK_Andy_Warhol = PromptStyle(
        name="MK_Andy_Warhol",
        prompt="Artwork in the style of Andy Warhol {prompt}. Pop art, vibrant colors, bold compositions, repetition of iconic imagery, celebrity culture, commercial aesthetics, mass production influence, stylized simplicity, cultural commentary, graphical elements, distinctive portraits.",
        negative_prompt="subdued colors, realistic, lack of repetition, minimalistic.",
    )

    MK_Halftone_print = PromptStyle(
        name="MK_Halftone_print",
        prompt="Halftone print of {prompt}. Dot matrix pattern, grayscale tones, vintage aesthetic, newspaper print vibe, stylized dots, visual texture, black and white contrasts, retro appearance, artistic pointillism,pop culture, (Roy Lichtenstein style:1.5).",
        negative_prompt="smooth gradients, continuous tones, vibrant colors.",
    )

    MK_Gond_Painting = PromptStyle(
        name="MK_Gond_Painting",
        prompt="Gond painting {prompt}. Intricate patterns, vibrant colors, detailed motifs, nature-inspired themes, tribal folklore, fine lines, intricate detailing, storytelling compositions, mystical and folkloric, cultural richness.",
        negative_prompt="monochromatic, abstract shapes, minimalistic.",
    )

    MK_Albumen_Print = PromptStyle(
        name="MK_Albumen_Print",
        prompt="Albumen print {prompt}. Sepia tones, fine details, subtle tonal gradations, delicate highlights, vintage aesthetic, soft and muted atmosphere, historical charm, rich textures, meticulous craftsmanship, classic photographic technique, vignetting.",
        negative_prompt="vibrant colors, high contrast, modern, digital appearance, sharp details, contemporary style.",
    )

    MK_Aquatint_Print = PromptStyle(
        name="MK_Aquatint_Print",
        prompt="Aquatint print {prompt}. Soft tonal gradations, atmospheric effects, velvety textures, rich contrasts, fine details, etching process, delicate lines, nuanced shading, expressive and moody atmosphere, artistic depth.",
        negative_prompt="sharp contrasts, bold lines, minimalistic.",
    )

    MK_Anthotype_Print = PromptStyle(
        name="MK_Anthotype_Print",
        prompt="Anthotype print {prompt}. Monochrome dye, soft and muted colors, organic textures, ephemeral and delicate appearance, low details, watercolor canvas, low contrast, overexposed, silhouette, textured paper.",
        negative_prompt="vibrant synthetic dyes, bold and saturated colors.",
    )

    MK_Inuit_Carving = PromptStyle(
        name="MK_Inuit_Carving",
        prompt="A sculpture made of ivory, {prompt} made of . Sculptures, Inuit art style, intricate carvings, natural materials, storytelling motifs, arctic wildlife themes, symbolic representations, cultural traditions, earthy tones, harmonious compositions, spiritual and mythological elements.",
        negative_prompt="abstract, vibrant colors.",
    )

    MK_Bromoil_Print = PromptStyle(
        name="MK_Bromoil_Print",
        prompt="Bromoil print {prompt}. Painterly effects, sepia tones, textured surfaces, rich contrasts, expressive brushwork, tonal variations, vintage aesthetic, atmospheric mood, handmade quality, artistic experimentation, darkroom craftsmanship, vignetting.",
        negative_prompt="smooth surfaces, minimal brushwork, contemporary digital appearance.",
    )

    MK_Calotype_Print = PromptStyle(
        name="MK_Calotype_Print",
        prompt="Calotype print {prompt}. Soft focus, subtle tonal range, paper negative process, fine details, vintage aesthetic, artistic experimentation, atmospheric mood, early photographic charm, handmade quality, vignetting.",
        negative_prompt="sharp focus, bold contrasts, modern aesthetic, digital photography.",
    )

    MK_Color_Sketchnote = PromptStyle(
        name="MK_Color_Sketchnote",
        prompt="Color sketchnote {prompt}. Hand-drawn elements, vibrant colors, visual hierarchy, playful illustrations, varied typography, graphic icons, organic and dynamic layout, personalized touches, creative expression, engaging storytelling.",
        negative_prompt="monochromatic, geometric layout.",
    )

    MK_Cibulak_Porcelain = PromptStyle(
        name="MK_Cibulak_Porcelain",
        prompt="A sculpture made of blue pattern porcelain of {prompt}. Classic design, blue and white color scheme, intricate detailing, floral motifs, onion-shaped elements, historical charm, rococo, white ware, cobalt blue, underglaze pattern, fine craftsmanship, traditional elegance, delicate patterns, vintage aesthetic, Meissen, Blue Onion pattern, Cibulak.",
        negative_prompt="tea, teapot, cup, teacup,bright colors, bold and modern design, absence of intricate detailing, lack of floral motifs, non-traditional shapes.",
    )

    MK_Alcohol_Ink_Art = PromptStyle(
        name="MK_Alcohol_Ink_Art",
        prompt="Alcohol ink art {prompt}. Fluid and vibrant colors, unpredictable patterns, organic textures, translucent layers, abstract compositions, ethereal and dreamy effects, free-flowing movement, expressive brushstrokes, contemporary aesthetic, wet textured paper.",
        negative_prompt="monochromatic, controlled patterns.",
    )

    MK_One_Line_Art = PromptStyle(
        name="MK_One_Line_Art",
        prompt="One line art {prompt}. Continuous and unbroken black line, minimalistic, simplicity, economical use of space, flowing and dynamic, symbolic representations, contemporary aesthetic, evocative and abstract, white background.",
        negative_prompt="disjointed lines, complexity, complex detailing.",
    )

    MK_Blacklight_Paint = PromptStyle(
        name="MK_Blacklight_Paint",
        prompt="Blacklight paint {prompt}. Fluorescent pigments, vibrant and surreal colors, ethereal glow, otherworldly effects, dynamic and psychedelic compositions, neon aesthetics, transformative in ultraviolet light, contemporary and experimental.",
        negative_prompt="muted colors, traditional and realistic compositions.",
    )

    MK_Carnival_Glass = PromptStyle(
        name="MK_Carnival_Glass",
        prompt="A sculpture made of Carnival glass, {prompt}. Iridescent surfaces, vibrant colors, intricate patterns, opalescent hues, reflective and prismatic effects, Art Nouveau and Art Deco influences, vintage charm, intricate detailing, lustrous and luminous appearance, Carnival Glass style.",
        negative_prompt="non-iridescent surfaces, muted colors, absence of intricate patterns, lack of opalescent hues, modern and minimalist aesthetic.",
    )

    MK_Cyanotype_Print = PromptStyle(
        name="MK_Cyanotype_Print",
        prompt="Cyanotype print {prompt}. Prussian blue tones, distinctive coloration, high contrast, blueprint aesthetics, atmospheric mood, sun-exposed paper, silhouette effects, delicate details, historical charm, handmade and experimental quality.",
        negative_prompt="vibrant colors, low contrast, modern and polished appearance.",
    )

    MK_Cross_Stitching = PromptStyle(
        name="MK_Cross_Stitching",
        prompt="Cross-stitching {prompt}. Intricate patterns, embroidery thread, sewing, fine details, precise stitches, textile artistry, symmetrical designs, varied color palette, traditional and contemporary motifs, handmade and crafted,canvas, nostalgic charm.",
        negative_prompt="paper, paint, ink, photography.",
    )

    MK_Encaustic_Paint = PromptStyle(
        name="MK_Encaustic_Paint",
        prompt="Encaustic paint {prompt}. Textured surfaces, translucent layers, luminous quality, wax medium, rich color saturation, fluid and organic shapes, contemporary and historical influences, mixed media elements, atmospheric depth.",
        negative_prompt="flat surfaces, opaque layers, lack of wax medium, muted color palette, absence of textured surfaces, non-mixed media.",
    )

    MK_Embroidery = PromptStyle(
        name="MK_Embroidery",
        prompt="Embroidery {prompt}. Intricate stitching, embroidery thread, fine details, varied thread textures, textile artistry, embellished surfaces, diverse color palette, traditional and contemporary motifs, handmade and crafted, tactile and ornate.",
        negative_prompt="minimalist, monochromatic.",
    )

    MK_Gyotaku = PromptStyle(
        name="MK_Gyotaku",
        prompt="Gyotaku {prompt}. Fish impressions, realistic details, ink rubbings, textured surfaces, traditional Japanese art form, nature-inspired compositions, artistic representation of marine life, black and white contrasts, cultural significance.",
        negative_prompt="photography.",
    )

    MK_Luminogram = PromptStyle(
        name="MK_Luminogram",
        prompt="Luminogram {prompt}. Photogram technique, ethereal and abstract effects, light and shadow interplay, luminous quality, experimental process, direct light exposure, unique and unpredictable results, artistic experimentation.",
    )

    MK_Lite_Brite_Art = PromptStyle(
        name="MK_Lite_Brite_Art",
        prompt="Lite Brite art {prompt}. Luminous and colorful designs, pixelated compositions, retro aesthetic, glowing effects, creative patterns, interactive and playful, nostalgic charm, vibrant and dynamic arrangements.",
        negative_prompt="monochromatic.",
    )

    MK_Mokume_gane = PromptStyle(
        name="MK_Mokume_gane",
        prompt="Mokume-gane {prompt}. Wood-grain patterns, mixed metal layers, intricate and organic designs, traditional Japanese metalwork, harmonious color combinations, artisanal craftsmanship, unique and layered textures, cultural and historical significance.",
        negative_prompt="uniform metal surfaces.",
    )

    Pebble_Art = PromptStyle(
        name="Pebble_Art",
        prompt="a sculpture made of peebles, {prompt}. Pebble art style,natural materials, textured surfaces, balanced compositions, organic forms, harmonious arrangements, tactile and 3D effects, beach-inspired aesthetic, creative storytelling, artisanal craftsmanship.",
        negative_prompt="non-natural materials, lack of textured surfaces, imbalanced compositions, absence of organic forms, non-tactile appearance.",
    )

    MK_Palekh = PromptStyle(
        name="MK_Palekh",
        prompt="Palekh art {prompt}. Miniature paintings, intricate details, vivid colors, folkloric themes, lacquer finish, storytelling compositions, symbolic elements, Russian folklore influence, cultural and historical significance.",
        negative_prompt="large-scale paintings.",
    )

    MK_Suminagashi = PromptStyle(
        name="MK_Suminagashi",
        prompt="Suminagashi {prompt}. Floating ink patterns, marbled effects, delicate and ethereal designs, water-based ink, fluid and unpredictable compositions, meditative process, monochromatic or subtle color palette, Japanese artistic tradition.",
        negative_prompt="vibrant and bold color palette.",
    )

    MK_Scrimshaw = PromptStyle(
        name="MK_Scrimshaw",
        prompt="A Scrimshaw engraving of {prompt}. Intricate engravings on a spermwhale's teeth, marine motifs, detailed scenes, nautical themes, black and white contrasts, historical craftsmanship, artisanal carving, storytelling compositions, maritime heritage.",
        negative_prompt="colorful, modern.",
    )

    MK_Shibori = PromptStyle(
        name="MK_Shibori",
        prompt="Shibori {prompt}. Textured fabric, intricate patterns, resist-dyeing technique, indigo or vibrant colors, organic and flowing designs, Japanese textile art, cultural tradition, tactile and visual interest.",
        negative_prompt="monochromatic.",
    )

    MK_Vitreous_Enamel = PromptStyle(
        name="MK_Vitreous_Enamel",
        prompt="A sculpture made of Vitreous enamel {prompt}. Smooth and glossy surfaces, vibrant colors, glass-like finish, durable and resilient, intricate detailing, traditional and contemporary applications, artistic craftsmanship, jewelry and decorative objects, , Vitreous enamel, colored glass.",
        negative_prompt="rough surfaces, muted colors.",
    )

    MK_Ukiyo_e = PromptStyle(
        name="MK_Ukiyo_e",
        prompt="Ukiyo-e {prompt}. Woodblock prints, vibrant colors, intricate details, depictions of landscapes, kabuki actors, beautiful women, cultural scenes, traditional Japanese art, artistic craftsmanship, historical significance.",
        negative_prompt="absence of woodblock prints, muted colors, lack of intricate details, non-traditional Japanese themes, absence of cultural scenes.",
    )

    MK_vintage_airline_poster = PromptStyle(
        name="MK_vintage_airline_poster",
        prompt="vintage airline poster {prompt} . classic aviation fonts, pastel colors, elegant aircraft illustrations, scenic destinations, distressed textures, retro travel allure",
        negative_prompt="modern fonts, bold colors, hyper-realistic, sleek design",
    )

    MK_vintage_travel_poster = PromptStyle(
        name="MK_vintage_travel_poster",
        prompt="vintage travel poster {prompt} . retro fonts, muted colors, scenic illustrations, iconic landmarks, distressed textures, nostalgic vibes",
        negative_prompt="modern fonts, vibrant colors, hyper-realistic, sleek design",
    )

    MK_bauhaus_style = PromptStyle(
        name="MK_bauhaus_style",
        prompt="Bauhaus-inspired {prompt} . minimalism, geometric precision, primary colors, sans-serif typography, asymmetry, functional design",
        negative_prompt="ornate, intricate, excessive detail, complex patterns, serif typography",
    )

    MK_afrofuturism = PromptStyle(
        name="MK_afrofuturism",
        prompt="Afrofuturism illustration {prompt} . vibrant colors, futuristic elements, cultural symbolism, cosmic imagery, dynamic patterns, empowering narratives",
        negative_prompt="monochromatic",
    )

    MK_atompunk = PromptStyle(
        name="MK_atompunk",
        prompt="Atompunk illustation, {prompt} . retro-futuristic, atomic age aesthetics, sleek lines, metallic textures, futuristic technology, optimism, energy",
        negative_prompt="organic, natural textures, rustic, dystopian",
    )

    MK_constructivism = PromptStyle(
        name="MK_constructivism",
        prompt="Constructivism {prompt} . geometric abstraction, bold colors, industrial aesthetics, dynamic compositions, utilitarian design, revolutionary spirit",
        negative_prompt="organic shapes, muted colors, ornate elements, traditional",
    )

    MK_chicano_art = PromptStyle(
        name="MK_chicano_art",
        prompt="Chicano art {prompt} . bold colors, cultural symbolism, muralism, lowrider aesthetics, barrio life, political messages, social activism, Mexico",
        negative_prompt="monochromatic, minimalist, mainstream aesthetics",
    )

    MK_de_stijl = PromptStyle(
        name="MK_de_stijl",
        prompt="De Stijl Art {prompt} . neoplasticism, primary colors, geometric abstraction, horizontal and vertical lines, simplicity, harmony, utopian ideals",
        negative_prompt="complex patterns, muted colors, ornate elements, asymmetry",
    )

    MK_dayak_art = PromptStyle(
        name="MK_dayak_art",
        prompt="Dayak art sculpture of {prompt} . intricate patterns, nature-inspired motifs, vibrant colors, traditional craftsmanship, cultural symbolism, storytelling",
        negative_prompt="minimalist, monochromatic, modern",
    )

    MK_fayum_portrait = PromptStyle(
        name="MK_fayum_portrait",
        prompt="Fayum portrait {prompt} . encaustic painting, realistic facial features, warm earth tones, serene expressions, ancient Egyptian influences",
        negative_prompt="abstract, vibrant colors, exaggerated features, modern",
    )

    MK_illuminated_manuscript = PromptStyle(
        name="MK_illuminated_manuscript",
        prompt="Illuminated manuscript {prompt} . intricate calligraphy, rich colors, detailed illustrations, gold leaf accents, ornate borders, religious, historical, medieval",
        negative_prompt="modern typography, minimalist design, monochromatic, abstract themes",
    )

    MK_kalighat_painting = PromptStyle(
        name="MK_kalighat_painting",
        prompt="Kalighat painting {prompt} . bold lines, vibrant colors, narrative storytelling, cultural motifs, flat compositions, expressive characters",
        negative_prompt="subdued colors, intricate details, realistic portrayal, modern aesthetics",
    )

    MK_madhubani_painting = PromptStyle(
        name="MK_madhubani_painting",
        prompt="Madhubani painting {prompt} . intricate patterns, vibrant colors, nature-inspired motifs, cultural storytelling, symmetry, folk art aesthetics",
        negative_prompt="abstract, muted colors, minimalistic design, modern aesthetics",
    )

    MK_pictorialism = PromptStyle(
        name="MK_pictorialism",
        prompt="Pictorialism illustration{prompt} . soft focus, atmospheric effects, artistic interpretation, tonality, muted colors, evocative storytelling",
        negative_prompt="sharp focus, high contrast, realistic depiction, vivid colors",
    )

    MK_pichwai_painting = PromptStyle(
        name="MK_pichwai_painting",
        prompt="Pichwai painting {prompt} . intricate detailing, vibrant colors, religious themes, nature motifs, devotional storytelling, gold leaf accents",
        negative_prompt="minimalist, subdued colors, abstract design",
    )

    MK_patachitra_painting = PromptStyle(
        name="MK_patachitra_painting",
        prompt="Patachitra painting {prompt} . bold outlines, vibrant colors, intricate detailing, mythological themes, storytelling, traditional craftsmanship",
        negative_prompt="subdued colors, minimalistic, abstract, modern aesthetics",
    )

    MK_samoan_art_inspired = PromptStyle(
        name="MK_samoan_art_inspired",
        prompt="Samoan art-inspired wooden sculpture {prompt} . traditional motifs, natural elements, bold colors, cultural symbolism, storytelling, craftsmanship",
        negative_prompt="modern aesthetics, minimalist, abstract",
    )

    MK_tlingit_art = PromptStyle(
        name="MK_tlingit_art",
        prompt="Tlingit art {prompt} . formline design, natural elements, animal motifs, bold colors, cultural storytelling, traditional craftsmanship, Alaska traditional art, (totem:1.5)",
    )

    MK_adnate_style = PromptStyle(
        name="MK_adnate_style",
        prompt="Painting by Adnate {prompt} . realistic portraits, street art, large-scale murals, subdued color palette, social narratives",
        negative_prompt="abstract, vibrant colors, small-scale art",
    )

    MK_ron_english_style = PromptStyle(
        name="MK_ron_english_style",
        prompt="Painting by Ron English {prompt} . pop-surrealism, cultural subversion, iconic mash-ups, vibrant and bold colors, satirical commentary",
        negative_prompt="traditional, monochromatic",
    )

    MK_shepard_fairey_style = PromptStyle(
        name="MK_shepard_fairey_style",
        prompt="Painting by Shepard Fairey {prompt} . street art, political activism, iconic stencils, bold typography, high contrast, red, black, and white color palette",
        negative_prompt="traditional, muted colors",
    )


class MRE(Enum):
    ALL_NAMES = [
        "mre_ancient_illustration",
        "mre_anime",
        "mre_artistic_vision",
        "mre_bad_dream",
        "mre_brave_art",
        "mre_cinematic_dynamic",
        "mre_comic",
        "mre_dark_cyberpunk",
        "mre_dark_dream",
        "mre_dynamic_illustration",
        "mre_elemental_art",
        "mre_gloomy_art",
        "mre_heroic_fantasy",
        "mre_lyrical_geometry",
        "mre_manga",
        "mre_space_art",
        "mre_spontaneous_picture",
        "mre_sumi_e_detailed",
        "mre_sumi_e_symbolic",
        "mre_surreal_painting",
        "mre_undead_art",
        "mre_underground",
    ]

    mre_cinematic_dynamic = PromptStyle(
        name="mre_cinematic_dynamic",
        prompt="epic cinematic shot of dynamic {prompt} in motion. main subject of high budget action movie. raw photo, motion blur. best quality, high resolution",
        negative_prompt="static, still, motionless, sluggish. drawing, painting, illustration, rendered. low budget. low quality, low resolution",
    )

    mre_spontaneous_picture = PromptStyle(
        name="mre_spontaneous_picture",
        prompt="spontaneous picture of {prompt}, taken by talented amateur. best quality, high resolution. magical moment, natural look. simple but good looking",
        negative_prompt="overthinked. low quality, low resolution",
    )

    mre_artistic_vision = PromptStyle(
        name="mre_artistic_vision",
        prompt="powerful artistic vision of {prompt}. breathtaking masterpiece made by great artist. best quality, high resolution",
        negative_prompt="insignificant, flawed, made by bad artist. low quality, low resolution",
    )

    mre_dark_dream = PromptStyle(
        name="mre_dark_dream",
        prompt="dark and unsettling dream showing {prompt}. best quality, high resolution. created by genius but depressed mad artist. grim beauty",
        negative_prompt="naive, cheerful. comfortable, casual, boring, cliche. low quality, low resolution",
    )

    mre_gloomy_art = PromptStyle(
        name="mre_gloomy_art",
        prompt="astonishing gloomy art made mainly of shadows and lighting, forming {prompt}. masterful usage of lighting, shadows and chiaroscuro. made by black-hearted artist, drawing from darkness. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_bad_dream = PromptStyle(
        name="mre_bad_dream",
        prompt="picture from really bad dream about terrifying {prompt}, true horror. bone-chilling vision. mad world that shouldn't exist. best quality, high resolution",
        negative_prompt="nice dream, pleasant experience. low quality, low resolution",
    )

    mre_underground = PromptStyle(
        name="mre_underground",
        prompt="uncanny caliginous vision of {prompt}, created by remarkable underground artist. best quality, high resolution. raw and brutal art, careless but impressive style. inspired by darkness and chaos",
        negative_prompt="photography, mainstream, civilized. low quality, low resolution",
    )

    mre_surreal_painting = PromptStyle(
        name="mre_surreal_painting",
        prompt="surreal painting representing strange vision of {prompt}. harmonious madness, synergy with chance. unique artstyle, mindbending art, magical surrealism. best quality, high resolution",
        negative_prompt="photography, illustration, drawing. realistic, possible. logical, sane. low quality, low resolution",
    )

    mre_dynamic_illustration = PromptStyle(
        name="mre_dynamic_illustration",
        prompt="insanely dynamic illustration of {prompt}. best quality, high resolution. crazy artstyle, careless brushstrokes, emotional and fun",
        negative_prompt="photography, realistic. static, still, slow, boring. low quality, low resolution",
    )

    mre_undead_art = PromptStyle(
        name="mre_undead_art",
        prompt="long forgotten art created by undead artist illustrating {prompt}, tribute to the death and decay. miserable art of the damned. wretched and decaying world. best quality, high resolution",
        negative_prompt="alive, playful, living. low quality, low resolution",
    )

    mre_elemental_art = PromptStyle(
        name="mre_elemental_art",
        prompt="art illustrating insane amounts of raging elemental energy turning into {prompt}, avatar of elements. magical surrealism, wizardry. best quality, high resolution",
        negative_prompt="photography, realistic, real. low quality, low resolution",
    )

    mre_space_art = PromptStyle(
        name="mre_space_art",
        prompt="winner of inter-galactic art contest illustrating {prompt}, symbol of the interstellar singularity. best quality, high resolution. artstyle previously unseen in the whole galaxy",
        negative_prompt="created by human race, low quality, low resolution",
    )

    mre_ancient_illustration = PromptStyle(
        name="mre_ancient_illustration",
        prompt="sublime ancient illustration of {prompt}, predating human civilization. crude and simple, but also surprisingly beautiful artwork, made by genius primeval artist. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_brave_art = PromptStyle(
        name="mre_brave_art",
        prompt="brave, shocking, and brutally true art showing {prompt}. inspired by courage and unlimited creativity. truth found in chaos. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_heroic_fantasy = PromptStyle(
        name="mre_heroic_fantasy",
        prompt="heroic fantasy painting of {prompt}, in the dangerous fantasy world. airbrush over oil on canvas. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_dark_cyberpunk = PromptStyle(
        name="mre_dark_cyberpunk",
        prompt="dark cyberpunk illustration of brutal {prompt} in a world without hope, ruled by ruthless criminal corporations. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_lyrical_geometry = PromptStyle(
        name="mre_lyrical_geometry",
        prompt="geometric and lyrical abstraction painting presenting {prompt}. oil on metal. best quality, high resolution",
        negative_prompt="photography, realistic, drawing, rendered. low quality, low resolution",
    )

    mre_sumi_e_symbolic = PromptStyle(
        name="mre_sumi_e_symbolic",
        prompt="big long brushstrokes of deep black sumi-e turning into symbolic painting of {prompt}. master level raw art. best quality, high resolution",
        negative_prompt="photography, rendered. low quality, low resolution",
    )

    mre_sumi_e_detailed = PromptStyle(
        name="mre_sumi_e_detailed",
        prompt="highly detailed black sumi-e painting of {prompt}. in-depth study of perfection, created by a master. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_manga = PromptStyle(
        name="mre_manga",
        prompt="manga artwork presenting {prompt}. created by japanese manga artist. highly emotional. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_anime = PromptStyle(
        name="mre_anime",
        prompt="anime artwork illustrating {prompt}. created by japanese anime studio. highly emotional. best quality, high resolution",
        negative_prompt="low quality, low resolution",
    )

    mre_comic = PromptStyle(
        name="mre_comic",
        prompt="breathtaking illustration from adult comic book presenting {prompt}. fabulous artwork. best quality, high resolution",
        negative_prompt="deformed, ugly, low quality, low resolution",
    )


class SAI(Enum):
    ALL_NAMES = [
        "sai_3d_model",
        "sai_analog_film",
        "sai_anime",
        "sai_cinematic",
        "sai_comic_book",
        "sai_craft_clay",
        "sai_digital_art",
        "sai_enhance",
        "sai_fantasy_art",
        "sai_isometric",
        "sai_line_art",
        "sai_lowpoly",
        "sai_neonpunk",
        "sai_origami",
        "sai_photographic",
        "sai_pixel_art",
        "sai_texture",
    ]

    @classmethod
    def all_style_names(cls):
        all_names = []
        for style in dir(cls):
            if isinstance(getattr(cls, style), PromptStyle):
                all_names.append(getattr(cls, style).name)
        return all_names

    sai_3d_model = PromptStyle(
        name="sai_3d_model",
        prompt="professional 3d model {prompt} . octane render, highly detailed, volumetric, dramatic lighting",
        negative_prompt="ugly, deformed, noisy, low poly, blurry, painting",
    )

    sai_analog_film = PromptStyle(
        name="sai_analog_film",
        prompt="analog film photo {prompt} . faded film, desaturated, 35mm photo, grainy, vignette, vintage, Kodachrome, Lomography, stained, highly detailed, found footage",
        negative_prompt="painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured",
    )

    sai_anime = PromptStyle(
        name="sai_anime",
        prompt="anime artwork {prompt} . anime style, key visual, vibrant, studio anime, highly detailed",
        negative_prompt="photo, deformed, black and white, realism, disfigured, low contrast",
    )

    sai_cinematic = PromptStyle(
        name="sai_cinematic",
        prompt="cinematic film still {prompt} . shallow depth of field, vignette, highly detailed, high budget, bokeh, cinemascope, moody, epic, gorgeous, film grain, grainy",
        negative_prompt="anime, cartoon, graphic, text, painting, crayon, graphite, abstract, glitch, deformed, mutated, ugly, disfigured",
    )

    sai_comic_book = PromptStyle(
        name="sai_comic_book",
        prompt="comic {prompt} . graphic illustration, comic art, graphic novel art, vibrant, highly detailed",
        negative_prompt="photograph, deformed, glitch, noisy, realistic, stock photo",
    )

    sai_craft_clay = PromptStyle(
        name="sai_craft_clay",
        prompt="play-doh style {prompt} . sculpture, clay art, centered composition, Claymation",
        negative_prompt="sloppy, messy, grainy, highly detailed, ultra textured, photo",
    )

    sai_digital_art = PromptStyle(
        name="sai_digital_art",
        prompt="concept art {prompt} . digital artwork, illustrative, painterly, matte painting, highly detailed",
        negative_prompt="photo, photorealistic, realism, ugly",
    )

    sai_enhance = PromptStyle(
        name="sai_enhance",
        prompt="breathtaking {prompt} . award-winning, professional, highly detailed",
        negative_prompt="ugly, deformed, noisy, blurry, distorted, grainy",
    )

    sai_fantasy_art = PromptStyle(
        name="sai_fantasy_art",
        prompt="ethereal fantasy concept art of  {prompt} . magnificent, celestial, ethereal, painterly, epic, majestic, magical, fantasy art, cover art, dreamy",
        negative_prompt="photographic, realistic, realism, 35mm film, dslr, cropped, frame, text, deformed, glitch, noise, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, sloppy, duplicate, mutated, black and white",
    )

    sai_isometric = PromptStyle(
        name="sai_isometric",
        prompt="isometric style {prompt} . vibrant, beautiful, crisp, detailed, ultra detailed, intricate",
        negative_prompt="deformed, mutated, ugly, disfigured, blur, blurry, noise, noisy, realistic, photographic",
    )

    sai_line_art = PromptStyle(
        name="sai_line_art",
        prompt="line art drawing {prompt} . professional, sleek, modern, minimalist, graphic, line art, vector graphics",
        negative_prompt="anime, photorealistic, 35mm film, deformed, glitch, blurry, noisy, off-center, deformed, cross-eyed, closed eyes, bad anatomy, ugly, disfigured, mutated, realism, realistic, impressionism, expressionism, oil, acrylic",
    )

    sai_lowpoly = PromptStyle(
        name="sai_lowpoly",
        prompt="low-poly style {prompt} . low-poly game art, polygon mesh, jagged, blocky, wireframe edges, centered composition",
        negative_prompt="noisy, sloppy, messy, grainy, highly detailed, ultra textured, photo",
    )

    sai_neonpunk = PromptStyle(
        name="sai_neonpunk",
        prompt="neonpunk style {prompt} . cyberpunk, vaporwave, neon, vibes, vibrant, stunningly beautiful, crisp, detailed, sleek, ultramodern, magenta highlights, dark purple shadows, high contrast, cinematic, ultra detailed, intricate, professional",
        negative_prompt="painting, drawing, illustration, glitch, deformed, mutated, cross-eyed, ugly, disfigured",
    )

    sai_origami = PromptStyle(
        name="sai_origami",
        prompt="origami style {prompt} . paper art, pleated paper, folded, origami art, pleats, cut and fold, centered composition",
        negative_prompt="noisy, sloppy, messy, grainy, highly detailed, ultra textured, photo",
    )

    sai_photographic = PromptStyle(
        name="sai_photographic",
        prompt="cinematic photo {prompt} . 35mm photograph, film, bokeh, professional, 4k, highly detailed",
        negative_prompt="drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly",
    )

    sai_pixel_art = PromptStyle(
        name="sai_pixel_art",
        prompt="pixel-art {prompt} . low-res, blocky, pixel art style, 8-bit graphics",
        negative_prompt="sloppy, messy, blurry, noisy, highly detailed, ultra textured, photo, realistic",
    )

    sai_texture = PromptStyle(
        name="sai_texture",
        prompt="texture {prompt} top down close-up",
        negative_prompt="ugly, deformed, noisy, blurry",
    )


class TWIRI(Enum):
    ALL_NAMES = [
        "ads_advertising",
        "ads_automotive",
        "ads_corporate",
        "ads_fashion_editorial",
        "ads_food_photography",
        "ads_gourmet_food_photography",
        "ads_luxury",
        "ads_real_estate",
        "ads_retail",
        "artstyle_abstract",
        "artstyle_abstract_expressionism",
        "artstyle_art_deco",
        "artstyle_art_nouveau",
        "artstyle_constructivist",
        "artstyle_cubist",
        "artstyle_expressionist",
        "artstyle_graffiti",
        "artstyle_hyperrealism",
        "artstyle_impressionist",
        "artstyle_pointillism",
        "artstyle_pop_art",
        "artstyle_psychedelic",
        "artstyle_renaissance",
        "artstyle_steampunk",
        "artstyle_surrealist",
        "artstyle_typography",
        "artstyle_watercolor",
        "futuristic_biomechanical",
        "futuristic_biomechanical_cyberpunk",
        "futuristic_cybernetic",
        "futuristic_cybernetic_robot",
        "futuristic_cyberpunk_cityscape",
        "futuristic_futuristic",
        "futuristic_retro_cyberpunk",
        "futuristic_retro_futurism",
        "futuristic_sci_fi",
        "futuristic_vaporwave",
        "game_bubble_bobble",
        "game_cyberpunk_game",
        "game_fighting_game",
        "game_gta",
        "game_mario",
        "game_minecraft",
        "game_pokemon",
        "game_retro_arcade",
        "game_retro_game",
        "game_rpg_fantasy_game",
        "game_strategy_game",
        "game_streetfighter",
        "game_zelda",
        "misc_architectural",
        "misc_disco",
        "misc_dreamscape",
        "misc_dystopian",
        "misc_fairy_tale",
        "misc_gothic",
        "misc_grunge",
        "misc_horror",
        "misc_kawaii",
        "misc_lovecraftian",
        "misc_macabre",
        "misc_manga",
        "misc_metropolis",
        "misc_minimalist",
        "misc_monochrome",
        "misc_nautical",
        "misc_space",
        "misc_stained_glass",
        "misc_techwear_fashion",
        "misc_tribal",
        "misc_zentangle",
        "papercraft_collage",
        "papercraft_flat_papercut",
        "papercraft_kirigami",
        "papercraft_paper_mache",
        "papercraft_paper_quilling",
        "papercraft_papercut_collage",
        "papercraft_papercut_shadow_box",
        "papercraft_stacked_papercut",
        "papercraft_thick_layered_papercut",
        "photo_alien",
        "photo_film_noir",
        "photo_glamour",
        "photo_hdr",
        "photo_iphone_photographic",
        "photo_long_exposure",
        "photo_neon_noir",
        "photo_silhouette",
        "photo_tilt_shift",
    ]

    ads_advertising = PromptStyle(
        name="ads_advertising",
        prompt="advertising poster style {prompt} . Professional, modern, product-focused, commercial, eye-catching, highly detailed",
        negative_prompt="noisy, blurry, amateurish, sloppy, unattractive",
    )

    ads_automotive = PromptStyle(
        name="ads_automotive",
        prompt="automotive advertisement style {prompt} . sleek, dynamic, professional, commercial, vehicle-focused, high-resolution, highly detailed",
        negative_prompt="noisy, blurry, unattractive, sloppy, unprofessional",
    )

    ads_corporate = PromptStyle(
        name="ads_corporate",
        prompt="corporate branding style {prompt} . professional, clean, modern, sleek, minimalist, business-oriented, highly detailed",
        negative_prompt="noisy, blurry, grungy, sloppy, cluttered, disorganized",
    )

    ads_fashion_editorial = PromptStyle(
        name="ads_fashion_editorial",
        prompt="fashion editorial style {prompt} . high fashion, trendy, stylish, editorial, magazine style, professional, highly detailed",
        negative_prompt="outdated, blurry, noisy, unattractive, sloppy",
    )

    ads_food_photography = PromptStyle(
        name="ads_food_photography",
        prompt="food photography style {prompt} . appetizing, professional, culinary, high-resolution, commercial, highly detailed",
        negative_prompt="unappetizing, sloppy, unprofessional, noisy, blurry",
    )

    ads_gourmet_food_photography = PromptStyle(
        name="ads_gourmet_food_photography",
        prompt="gourmet food photo of {prompt} . soft natural lighting, macro details, vibrant colors, fresh ingredients, glistening textures, bokeh background, styled plating, wooden tabletop, garnished, tantalizing, editorial quality",
        negative_prompt="cartoon, anime, sketch, grayscale, dull, overexposed, cluttered, messy plate, deformed",
    )

    ads_luxury = PromptStyle(
        name="ads_luxury",
        prompt="luxury product style {prompt} . elegant, sophisticated, high-end, luxurious, professional, highly detailed",
        negative_prompt="cheap, noisy, blurry, unattractive, amateurish",
    )

    ads_real_estate = PromptStyle(
        name="ads_real_estate",
        prompt="real estate photography style {prompt} . professional, inviting, well-lit, high-resolution, property-focused, commercial, highly detailed",
        negative_prompt="dark, blurry, unappealing, noisy, unprofessional",
    )

    ads_retail = PromptStyle(
        name="ads_retail",
        prompt="retail packaging style {prompt} . vibrant, enticing, commercial, product-focused, eye-catching, professional, highly detailed",
        negative_prompt="noisy, blurry, amateurish, sloppy, unattractive",
    )

    artstyle_abstract = PromptStyle(
        name="artstyle_abstract",
        prompt="abstract style {prompt} . non-representational, colors and shapes, expression of feelings, imaginative, highly detailed",
        negative_prompt="realistic, photographic, figurative, concrete",
    )

    artstyle_abstract_expressionism = PromptStyle(
        name="artstyle_abstract_expressionism",
        prompt="abstract expressionist painting {prompt} . energetic brushwork, bold colors, abstract forms, expressive, emotional",
        negative_prompt="realistic, photorealistic, low contrast, plain, simple, monochrome",
    )

    artstyle_art_deco = PromptStyle(
        name="artstyle_art_deco",
        prompt="art deco style {prompt} . geometric shapes, bold colors, luxurious, elegant, decorative, symmetrical, ornate, detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, modernist, minimalist",
    )

    artstyle_art_nouveau = PromptStyle(
        name="artstyle_art_nouveau",
        prompt="art nouveau style {prompt} . elegant, decorative, curvilinear forms, nature-inspired, ornate, detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, modernist, minimalist",
    )

    artstyle_constructivist = PromptStyle(
        name="artstyle_constructivist",
        prompt="constructivist style {prompt} . geometric shapes, bold colors, dynamic composition, propaganda art style",
        negative_prompt="realistic, photorealistic, low contrast, plain, simple, abstract expressionism",
    )

    artstyle_cubist = PromptStyle(
        name="artstyle_cubist",
        prompt="cubist artwork {prompt} . geometric shapes, abstract, innovative, revolutionary",
        negative_prompt="anime, photorealistic, 35mm film, deformed, glitch, low contrast, noisy",
    )

    artstyle_expressionist = PromptStyle(
        name="artstyle_expressionist",
        prompt="expressionist {prompt} . raw, emotional, dynamic, distortion for emotional effect, vibrant, use of unusual colors, detailed",
        negative_prompt="realism, symmetry, quiet, calm, photo",
    )

    artstyle_graffiti = PromptStyle(
        name="artstyle_graffiti",
        prompt="graffiti style {prompt} . street art, vibrant, urban, detailed, tag, mural",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic",
    )

    artstyle_hyperrealism = PromptStyle(
        name="artstyle_hyperrealism",
        prompt="hyperrealistic art {prompt} . extremely high-resolution details, photographic, realism pushed to extreme, fine texture, incredibly lifelike",
        negative_prompt="simplified, abstract, unrealistic, impressionistic, low resolution",
    )

    artstyle_impressionist = PromptStyle(
        name="artstyle_impressionist",
        prompt="impressionist painting {prompt} . loose brushwork, vibrant color, light and shadow play, captures feeling over form",
        negative_prompt="anime, photorealistic, 35mm film, deformed, glitch, low contrast, noisy",
    )

    artstyle_pointillism = PromptStyle(
        name="artstyle_pointillism",
        prompt="pointillism style {prompt} . composed entirely of small, distinct dots of color, vibrant, highly detailed",
        negative_prompt="line drawing, smooth shading, large color fields, simplistic",
    )

    artstyle_pop_art = PromptStyle(
        name="artstyle_pop_art",
        prompt="pop Art style {prompt} . bright colors, bold outlines, popular culture themes, ironic or kitsch",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, minimalist",
    )

    artstyle_psychedelic = PromptStyle(
        name="artstyle_psychedelic",
        prompt="psychedelic style {prompt} . vibrant colors, swirling patterns, abstract forms, surreal, trippy",
        negative_prompt="monochrome, black and white, low contrast, realistic, photorealistic, plain, simple",
    )

    artstyle_renaissance = PromptStyle(
        name="artstyle_renaissance",
        prompt="renaissance style {prompt} . realistic, perspective, light and shadow, religious or mythological themes, highly detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, modernist, minimalist, abstract",
    )

    artstyle_steampunk = PromptStyle(
        name="artstyle_steampunk",
        prompt="steampunk style {prompt} . antique, mechanical, brass and copper tones, gears, intricate, detailed",
        negative_prompt="deformed, glitch, noisy, low contrast, anime, photorealistic",
    )

    artstyle_surrealist = PromptStyle(
        name="artstyle_surrealist",
        prompt="surrealist art {prompt} . dreamlike, mysterious, provocative, symbolic, intricate, detailed",
        negative_prompt="anime, photorealistic, realistic, deformed, glitch, noisy, low contrast",
    )

    artstyle_typography = PromptStyle(
        name="artstyle_typography",
        prompt="typographic art {prompt} . stylized, intricate, detailed, artistic, text-based",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic",
    )

    artstyle_watercolor = PromptStyle(
        name="artstyle_watercolor",
        prompt="watercolor painting {prompt} . vibrant, beautiful, painterly, detailed, textural, artistic",
        negative_prompt="anime, photorealistic, 35mm film, deformed, glitch, low contrast, noisy",
    )

    futuristic_biomechanical = PromptStyle(
        name="futuristic_biomechanical",
        prompt="biomechanical style {prompt} . blend of organic and mechanical elements, futuristic, cybernetic, detailed, intricate",
        negative_prompt="natural, rustic, primitive, organic, simplistic",
    )

    futuristic_biomechanical_cyberpunk = PromptStyle(
        name="futuristic_biomechanical_cyberpunk",
        prompt="biomechanical cyberpunk {prompt} . cybernetics, human-machine fusion, dystopian, organic meets artificial, dark, intricate, highly detailed",
        negative_prompt="natural, colorful, deformed, sketch, low contrast, watercolor",
    )

    futuristic_cybernetic = PromptStyle(
        name="futuristic_cybernetic",
        prompt="cybernetic style {prompt} . futuristic, technological, cybernetic enhancements, robotics, artificial intelligence themes",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, historical, medieval",
    )

    futuristic_cybernetic_robot = PromptStyle(
        name="futuristic_cybernetic_robot",
        prompt="cybernetic robot {prompt} . android, AI, machine, metal, wires, tech, futuristic, highly detailed",
        negative_prompt="organic, natural, human, sketch, watercolor, low contrast",
    )

    futuristic_cyberpunk_cityscape = PromptStyle(
        name="futuristic_cyberpunk_cityscape",
        prompt="cyberpunk cityscape {prompt} . neon lights, dark alleys, skyscrapers, futuristic, vibrant colors, high contrast, highly detailed",
        negative_prompt="natural, rural, deformed, low contrast, black and white, sketch, watercolor",
    )

    futuristic_futuristic = PromptStyle(
        name="futuristic_futuristic",
        prompt="futuristic style {prompt} . sleek, modern, ultramodern, high tech, detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, vintage, antique",
    )

    futuristic_retro_cyberpunk = PromptStyle(
        name="futuristic_retro_cyberpunk",
        prompt="retro cyberpunk {prompt} . 80's inspired, synthwave, neon, vibrant, detailed, retro futurism",
        negative_prompt="modern, desaturated, black and white, realism, low contrast",
    )

    futuristic_retro_futurism = PromptStyle(
        name="futuristic_retro_futurism",
        prompt="retro-futuristic {prompt} . vintage sci-fi, 50s and 60s style, atomic age, vibrant, highly detailed",
        negative_prompt="contemporary, realistic, rustic, primitive",
    )

    futuristic_sci_fi = PromptStyle(
        name="futuristic_sci_fi",
        prompt="sci-fi style {prompt} . futuristic, technological, alien worlds, space themes, advanced civilizations",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, historical, medieval",
    )

    futuristic_vaporwave = PromptStyle(
        name="futuristic_vaporwave",
        prompt="vaporwave style {prompt} . retro aesthetic, cyberpunk, vibrant, neon colors, vintage 80s and 90s style, highly detailed",
        negative_prompt="monochrome, muted colors, realism, rustic, minimalist, dark",
    )

    game_bubble_bobble = PromptStyle(
        name="game_bubble_bobble",
        prompt="Bubble Bobble style {prompt} . 8-bit, cute, pixelated, fantasy, vibrant, reminiscent of Bubble Bobble game",
        negative_prompt="realistic, modern, photorealistic, violent, horror",
    )

    game_cyberpunk_game = PromptStyle(
        name="game_cyberpunk_game",
        prompt="cyberpunk game style {prompt} . neon, dystopian, futuristic, digital, vibrant, detailed, high contrast, reminiscent of cyberpunk genre video games",
        negative_prompt="historical, natural, rustic, low detailed",
    )

    game_fighting_game = PromptStyle(
        name="game_fighting_game",
        prompt="fighting game style {prompt} . dynamic, vibrant, action-packed, detailed character design, reminiscent of fighting video games",
        negative_prompt="peaceful, calm, minimalist, photorealistic",
    )

    game_gta = PromptStyle(
        name="game_gta",
        prompt="GTA-style artwork {prompt} . satirical, exaggerated, pop art style, vibrant colors, iconic characters, action-packed",
        negative_prompt="realistic, black and white, low contrast, impressionist, cubist, noisy, blurry, deformed",
    )

    game_mario = PromptStyle(
        name="game_mario",
        prompt="Super Mario style {prompt} . vibrant, cute, cartoony, fantasy, playful, reminiscent of Super Mario series",
        negative_prompt="realistic, modern, horror, dystopian, violent",
    )

    game_minecraft = PromptStyle(
        name="game_minecraft",
        prompt="Minecraft style {prompt} . blocky, pixelated, vibrant colors, recognizable characters and objects, game assets",
        negative_prompt="smooth, realistic, detailed, photorealistic, noise, blurry, deformed",
    )

    game_pokemon = PromptStyle(
        name="game_pokemon",
        prompt="Pokémon style {prompt} . vibrant, cute, anime, fantasy, reminiscent of Pokémon series",
        negative_prompt="realistic, modern, horror, dystopian, violent",
    )

    game_retro_arcade = PromptStyle(
        name="game_retro_arcade",
        prompt="retro arcade style {prompt} . 8-bit, pixelated, vibrant, classic video game, old school gaming, reminiscent of 80s and 90s arcade games",
        negative_prompt="modern, ultra-high resolution, photorealistic, 3D",
    )

    game_retro_game = PromptStyle(
        name="game_retro_game",
        prompt="retro game art {prompt} . 16-bit, vibrant colors, pixelated, nostalgic, charming, fun",
        negative_prompt="realistic, photorealistic, 35mm film, deformed, glitch, low contrast, noisy",
    )

    game_rpg_fantasy_game = PromptStyle(
        name="game_rpg_fantasy_game",
        prompt="role-playing game (RPG) style fantasy {prompt} . detailed, vibrant, immersive, reminiscent of high fantasy RPG games",
        negative_prompt="sci-fi, modern, urban, futuristic, low detailed",
    )

    game_strategy_game = PromptStyle(
        name="game_strategy_game",
        prompt="strategy game style {prompt} . overhead view, detailed map, units, reminiscent of real-time strategy video games",
        negative_prompt="first-person view, modern, photorealistic",
    )

    game_streetfighter = PromptStyle(
        name="game_streetfighter",
        prompt="Street Fighter style {prompt} . vibrant, dynamic, arcade, 2D fighting game, highly detailed, reminiscent of Street Fighter series",
        negative_prompt="3D, realistic, modern, photorealistic, turn-based strategy",
    )

    game_zelda = PromptStyle(
        name="game_zelda",
        prompt="Legend of Zelda style {prompt} . vibrant, fantasy, detailed, epic, heroic, reminiscent of The Legend of Zelda series",
        negative_prompt="sci-fi, modern, realistic, horror",
    )

    misc_architectural = PromptStyle(
        name="misc_architectural",
        prompt="architectural style {prompt} . clean lines, geometric shapes, minimalist, modern, architectural drawing, highly detailed",
        negative_prompt="curved lines, ornate, baroque, abstract, grunge",
    )

    misc_disco = PromptStyle(
        name="misc_disco",
        prompt="disco-themed {prompt} . vibrant, groovy, retro 70s style, shiny disco balls, neon lights, dance floor, highly detailed",
        negative_prompt="minimalist, rustic, monochrome, contemporary, simplistic",
    )

    misc_dreamscape = PromptStyle(
        name="misc_dreamscape",
        prompt="dreamscape {prompt} . surreal, ethereal, dreamy, mysterious, fantasy, highly detailed",
        negative_prompt="realistic, concrete, ordinary, mundane",
    )

    misc_dystopian = PromptStyle(
        name="misc_dystopian",
        prompt="dystopian style {prompt} . bleak, post-apocalyptic, somber, dramatic, highly detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, cheerful, optimistic, vibrant, colorful",
    )

    misc_fairy_tale = PromptStyle(
        name="misc_fairy_tale",
        prompt="fairy tale {prompt} . magical, fantastical, enchanting, storybook style, highly detailed",
        negative_prompt="realistic, modern, ordinary, mundane",
    )

    misc_gothic = PromptStyle(
        name="misc_gothic",
        prompt="gothic style {prompt} . dark, mysterious, haunting, dramatic, ornate, detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, cheerful, optimistic",
    )

    misc_grunge = PromptStyle(
        name="misc_grunge",
        prompt="grunge style {prompt} . textured, distressed, vintage, edgy, punk rock vibe, dirty, noisy",
        negative_prompt="smooth, clean, minimalist, sleek, modern, photorealistic",
    )

    misc_horror = PromptStyle(
        name="misc_horror",
        prompt="horror-themed {prompt} . eerie, unsettling, dark, spooky, suspenseful, grim, highly detailed",
        negative_prompt="cheerful, bright, vibrant, light-hearted, cute",
    )

    misc_kawaii = PromptStyle(
        name="misc_kawaii",
        prompt="kawaii style {prompt} . cute, adorable, brightly colored, cheerful, anime influence, highly detailed",
        negative_prompt="dark, scary, realistic, monochrome, abstract",
    )

    misc_lovecraftian = PromptStyle(
        name="misc_lovecraftian",
        prompt="lovecraftian horror {prompt} . eldritch, cosmic horror, unknown, mysterious, surreal, highly detailed",
        negative_prompt="light-hearted, mundane, familiar, simplistic, realistic",
    )

    misc_macabre = PromptStyle(
        name="misc_macabre",
        prompt="macabre style {prompt} . dark, gothic, grim, haunting, highly detailed",
        negative_prompt="bright, cheerful, light-hearted, cartoonish, cute",
    )

    misc_manga = PromptStyle(
        name="misc_manga",
        prompt="manga style {prompt} . vibrant, high-energy, detailed, iconic, Japanese comic style",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, Western comic style",
    )

    misc_metropolis = PromptStyle(
        name="misc_metropolis",
        prompt="metropolis-themed {prompt} . urban, cityscape, skyscrapers, modern, futuristic, highly detailed",
        negative_prompt="rural, natural, rustic, historical, simple",
    )

    misc_minimalist = PromptStyle(
        name="misc_minimalist",
        prompt="minimalist style {prompt} . simple, clean, uncluttered, modern, elegant",
        negative_prompt="ornate, complicated, highly detailed, cluttered, disordered, messy, noisy",
    )

    misc_monochrome = PromptStyle(
        name="misc_monochrome",
        prompt="monochrome {prompt} . black and white, contrast, tone, texture, detailed",
        negative_prompt="colorful, vibrant, noisy, blurry, deformed",
    )

    misc_nautical = PromptStyle(
        name="misc_nautical",
        prompt="nautical-themed {prompt} . sea, ocean, ships, maritime, beach, marine life, highly detailed",
        negative_prompt="landlocked, desert, mountains, urban, rustic",
    )

    misc_space = PromptStyle(
        name="misc_space",
        prompt="space-themed {prompt} . cosmic, celestial, stars, galaxies, nebulas, planets, science fiction, highly detailed",
        negative_prompt="earthly, mundane, ground-based, realism",
    )

    misc_stained_glass = PromptStyle(
        name="misc_stained_glass",
        prompt="stained glass style {prompt} . vibrant, beautiful, translucent, intricate, detailed",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic",
    )

    misc_techwear_fashion = PromptStyle(
        name="misc_techwear_fashion",
        prompt="techwear fashion {prompt} . futuristic, cyberpunk, urban, tactical, sleek, dark, highly detailed",
        negative_prompt="vintage, rural, colorful, low contrast, realism, sketch, watercolor",
    )

    misc_tribal = PromptStyle(
        name="misc_tribal",
        prompt="tribal style {prompt} . indigenous, ethnic, traditional patterns, bold, natural colors, highly detailed",
        negative_prompt="modern, futuristic, minimalist, pastel",
    )

    misc_zentangle = PromptStyle(
        name="misc_zentangle",
        prompt="zentangle {prompt} . intricate, abstract, monochrome, patterns, meditative, highly detailed",
        negative_prompt="colorful, representative, simplistic, large fields of color",
    )

    papercraft_collage = PromptStyle(
        name="papercraft_collage",
        prompt="collage style {prompt} . mixed media, layered, textural, detailed, artistic",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic",
    )

    papercraft_flat_papercut = PromptStyle(
        name="papercraft_flat_papercut",
        prompt="flat papercut style {prompt} . silhouette, clean cuts, paper, sharp edges, minimalist, color block",
        negative_prompt="3D, high detail, noise, grainy, blurry, painting, drawing, photo, disfigured",
    )

    papercraft_kirigami = PromptStyle(
        name="papercraft_kirigami",
        prompt="kirigami representation of {prompt} . 3D, paper folding, paper cutting, Japanese, intricate, symmetrical, precision, clean lines",
        negative_prompt="painting, drawing, 2D, noisy, blurry, deformed",
    )

    papercraft_paper_mache = PromptStyle(
        name="papercraft_paper_mache",
        prompt="paper mache representation of {prompt} . 3D, sculptural, textured, handmade, vibrant, fun",
        negative_prompt="2D, flat, photo, sketch, digital art, deformed, noisy, blurry",
    )

    papercraft_paper_quilling = PromptStyle(
        name="papercraft_paper_quilling",
        prompt="paper quilling art of {prompt} . intricate, delicate, curling, rolling, shaping, coiling, loops, 3D, dimensional, ornamental",
        negative_prompt="photo, painting, drawing, 2D, flat, deformed, noisy, blurry",
    )

    papercraft_papercut_collage = PromptStyle(
        name="papercraft_papercut_collage",
        prompt="papercut collage of {prompt} . mixed media, textured paper, overlapping, asymmetrical, abstract, vibrant",
        negative_prompt="photo, 3D, realistic, drawing, painting, high detail, disfigured",
    )

    papercraft_papercut_shadow_box = PromptStyle(
        name="papercraft_papercut_shadow_box",
        prompt="3D papercut shadow box of {prompt} . layered, dimensional, depth, silhouette, shadow, papercut, handmade, high contrast",
        negative_prompt="painting, drawing, photo, 2D, flat, high detail, blurry, noisy, disfigured",
    )

    papercraft_stacked_papercut = PromptStyle(
        name="papercraft_stacked_papercut",
        prompt="stacked papercut art of {prompt} . 3D, layered, dimensional, depth, precision cut, stacked layers, papercut, high contrast",
        negative_prompt="2D, flat, noisy, blurry, painting, drawing, photo, deformed",
    )

    papercraft_thick_layered_papercut = PromptStyle(
        name="papercraft_thick_layered_papercut",
        prompt="thick layered papercut art of {prompt} . deep 3D, volumetric, dimensional, depth, thick paper, high stack, heavy texture, tangible layers",
        negative_prompt="2D, flat, thin paper, low stack, smooth texture, painting, drawing, photo, deformed",
    )

    photo_alien = PromptStyle(
        name="photo_alien",
        prompt="alien-themed {prompt} . extraterrestrial, cosmic, otherworldly, mysterious, sci-fi, highly detailed",
        negative_prompt="earthly, mundane, common, realistic, simple",
    )

    photo_film_noir = PromptStyle(
        name="photo_film_noir",
        prompt="film noir style {prompt} . monochrome, high contrast, dramatic shadows, 1940s style, mysterious, cinematic",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, realism, photorealistic, vibrant, colorful",
    )

    photo_glamour = PromptStyle(
        name="photo_glamour",
        prompt="glamorous photo {prompt} . high fashion, luxurious, extravagant, stylish, sensual, opulent, elegance, stunning beauty, professional, high contrast, detailed",
        negative_prompt="ugly, deformed, noisy, blurry, distorted, grainy, sketch, low contrast, dull, plain, modest",
    )

    photo_hdr = PromptStyle(
        name="photo_hdr",
        prompt="HDR photo of {prompt} . High dynamic range, vivid, rich details, clear shadows and highlights, realistic, intense, enhanced contrast, highly detailed",
        negative_prompt="flat, low contrast, oversaturated, underexposed, overexposed, blurred, noisy",
    )

    photo_iphone_photographic = PromptStyle(
        name="photo_iphone_photographic",
        prompt="iphone photo {prompt} . large depth of field, deep depth of field, highly detailed",
        negative_prompt="drawing, painting, crayon, sketch, graphite, impressionist, noisy, blurry, soft, deformed, ugly, shallow depth of field, bokeh",
    )

    photo_long_exposure = PromptStyle(
        name="photo_long_exposure",
        prompt="long exposure photo of {prompt} . Blurred motion, streaks of light, surreal, dreamy, ghosting effect, highly detailed",
        negative_prompt="static, noisy, deformed, shaky, abrupt, flat, low contrast",
    )

    photo_neon_noir = PromptStyle(
        name="photo_neon_noir",
        prompt="neon noir {prompt} . cyberpunk, dark, rainy streets, neon signs, high contrast, low light, vibrant, highly detailed",
        negative_prompt="bright, sunny, daytime, low contrast, black and white, sketch, watercolor",
    )

    photo_silhouette = PromptStyle(
        name="photo_silhouette",
        prompt="silhouette style {prompt} . high contrast, minimalistic, black and white, stark, dramatic",
        negative_prompt="ugly, deformed, noisy, blurry, low contrast, color, realism, photorealistic",
    )

    photo_tilt_shift = PromptStyle(
        name="photo_tilt_shift",
        prompt="tilt-shift photo of {prompt} . selective focus, miniature effect, blurred background, highly detailed, vibrant, perspective control",
        negative_prompt="blurry, noisy, deformed, flat, low contrast, unrealistic, oversaturated, underexposed",
    )


if __name__ == "__main__":
    for styleobj in [Fooocus, Diva, Mark_K3nt3l, MRE, SAI, TWIRI]:
        ...