import os, sys
currdir = os.path.abspath(__file__)
sys.path.append(currdir.split("Hooocus")[0]+"Hooocus")

import random
import re
import json
import math

from random import Random

from modules.sdxl_styles.prompt_styles import PromptStyles, VALID_STYLE_NAMES


def get_random_style() -> str:
    return PromptStyles[random.choice(VALID_STYLE_NAMES)].value


def apply_style(style, positive, is_lambda_style=False):
    if not is_lambda_style:
        _name, p, n = PromptStyles[style].value.tuple
    else:
        _name, p, n = style

    has_placeholder = False
    if p:
        if '{prompt}' in p:
            p = p.replace('{prompt}', positive)
            has_placeholder = True

    else:
        p = ""

    if not n:
        n = ""
    
    return_res = p.splitlines(), n.splitlines(), has_placeholder

    return return_res


def get_words(arrays, total_mult, index):
    if len(arrays) == 1:
        return [arrays[0].split(',')[index]]
    else:
        words = arrays[0].split(',')
        word = words[index % len(words)]
        index -= index % len(words)
        index /= len(words)
        index = math.floor(index)
        return [word] + get_words(arrays[1:], math.floor(total_mult / len(words)), index)


def apply_arrays(text, index):
    arrays = re.findall(r'\[\[(.*?)\]\]', text)
    if len(arrays) == 0:
        return text

    print(f'[Arrays] processing: {text}')
    mult = 1
    for arr in arrays:
        words = arr.split(',')
        mult *= len(words)
    
    index %= mult
    chosen_words = get_words(arrays, mult, index)
    
    i = 0
    for arr in arrays:
        text = text.replace(f'[[{arr}]]', chosen_words[i], 1)   
        i = i+1
    
    return text

