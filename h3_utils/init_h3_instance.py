# Init h3_instance.py

import os, sys
rootdir = os.path.abspath(__file__).split("Hooocus")[0]+"Hooocus"
sys.path.append(rootdir)



def init_launch():
    import logging
    # Clear logging cache
    logging.shutdown()
