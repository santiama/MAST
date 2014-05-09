"""Tests for Defectformationenergy"""

from MAST.utility.defect_formation_energy.defectformationenergy import DefectFormationEnergy

import unittest
from unittest import SkipTest
import os
import time
import MAST
import pymatgen
from MAST.utility import dirutil
import shutil
from MAST.utility import MASTFile
testname="defect_formation_energy_test"
testdir = os.path.join(os.getenv("MAST_INSTALL_PATH"),'test',testname)
oldarchive = os.getenv("MAST_ARCHIVE")
      
class TestDefectformationenergy(unittest.TestCase):

    def setUp(self):
        os.environ['MAST_ARCHIVE'] = os.path.join(testdir,'archive')
        os.chdir(testdir)

    def tearDown(self):
        os.environ['MAST_ARCHIVE'] = oldarchive
        if os.path.isdir("GaAs_defects_AsGa_recipe_defects_20131125T220427_dfe_results"):
            shutil.rmtree("GaAs_defects_AsGa_recipe_defects_20131125T220427_dfe_results")

    def test_dfe_tool(self):
        import subprocess
        mydfetest=subprocess.Popen(["%s/tools/defect_formation_energy 2 3" % os.getenv("MAST_INSTALL_PATH")],shell=True)
        mydfetest.wait()
        compare_walk = dirutil.walkfiles("compare_results")
        res_walk = dirutil.walkfiles("GaAs_defects_AsGa_recipe_defects_20131125T220427_dfe_results")
        compare_walk.sort()
        res_walk.sort()
        self.assertEqual(len(compare_walk), len(res_walk))
        for idx in range(0,len(compare_walk)):
            compfile = MASTFile(compare_walk[idx])
            myfile = MASTFile(res_walk[idx])
            self.assertEqual(compfile.data, myfile.data)

    def test___init__(self):
        raise SkipTest
        #self.testclass.__init__(directory=None, plot_threshold=0.01)

    def test__calculate_defect_formation_energies(self):
        raise SkipTest
        recipepath = os.path.join(testdir, 'archive','GaAs_defects_AsGa_recipe_defects_20131125T220427')
        mydfe = DefectFormationEnergy(directory=recipepath)
        mydfe._calculate_defect_formation_energies() 
        self.assertEqual(True,True)
        #self.testclass._calculate_defect_formation_energies()

    def test_get_total_energy(self):
        raise SkipTest
        #self.testclass.get_total_energy(directory)

    def test_get_fermi_energy(self):
        raise SkipTest
        #self.testclass.get_fermi_energy(directory)

    def test_get_structure(self):
        raise SkipTest
        #self.testclass.get_structure(directory)

    def test_get_potential_alignment(self):
        raise SkipTest
        #self.testclass.get_potential_alignment(perf_dir, def_dir)

    def test_get_defect_formation_energies(self):
        raise SkipTest
        #self.testclass.get_defect_formation_energies()

    def test_defect_formation_energies(self):
        raise SkipTest
        #self.testclass.defect_formation_energies()

    def test_dfe(self):
        raise SkipTest
        #self.testclass.dfe()

    def test_print_table(self):
        raise SkipTest
        #self.testclass.print_table()