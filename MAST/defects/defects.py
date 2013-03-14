import os
import shutil as sh

import numpy as np

import MAST.utility.mastobj import MASTObj


allowed_keys = {'sizelimit': (int, 1, 'How big to extrapolate out to'),
                'vacancies': (list, [], 'List of vacancy positions'),
                'interstitials': (list, [], 'List of intersitial positions'),
                'chempot': (list, [], 'List of chemical potential'),
               }

class Defects(MASTObj):
    def __init__(self, **kwargs):
        MASTobj.__init__(self, allowed_keys, **kwargs)
