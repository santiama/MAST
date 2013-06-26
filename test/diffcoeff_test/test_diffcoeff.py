import pymatgen
import os
import shutil
import sys
import unittest
import time
import filecmp
from filecmp import dircmp
import subprocess

from MAST.ingredients.optimize import Optimize
from MAST.utility import MASTError
from pymatgen.io.vaspio import Poscar
from MAST.utility.dirutil import *

class TestDiffCoeff(unittest.TestCase):
    def setUp(self):
        scripts = get_mast_install_path()
        os.chdir(os.path.join(scripts, 'test','diffcoeff_test'))

        #self.myOpt=Optimize(name="test_opt1", program="vasp", program_keys={'ibrion':2, 'mast_kpoints':[4,4,4,"M"], 'mast_xc':"PBE", 'mast_setmagmom':"5 1", 'mast_adjustnelect':"-1"})

    def tearDown(self):
        pass
        #shutil.rmtree('test_opt1')
        #try:
        #    shutil.rmtree('test_opt2')
        #except OSError:
        #    pass
    
    def test_run_from_prompt(self):
        mastpath = get_mast_install_path()
        myp=subprocess.Popen([mastpath+"/MAST/utility/diffusioncoefficient.py", mastpath+"/test/diffcoeff_test/diffcoeff_singlevac", "73", "1273", "100", "1", "w0=vac1-vac2","1"])
            #stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #myp.communicate()[0]
        myp.wait()


