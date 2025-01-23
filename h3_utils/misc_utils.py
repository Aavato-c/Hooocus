import random
import string
import os, sys
rootdir = os.path.abspath(__file__).split("Hooocus")[0]+"Hooocus"
sys.path.append(rootdir)


def get_random_string(n: int = 5):
    return ''.join(random.choices(string.digits + string.ascii_letters, k=n))