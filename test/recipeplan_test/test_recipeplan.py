"""Tests for Recipeplan"""

from MAST.recipe.recipeplan import RecipePlan

import unittest
from unittest import SkipTest
import os
import time
import MAST
import pymatgen
from MAST.utility import dirutil
from MAST.utility import MASTFile
from MAST.utility import MASTError
testname="recipeplan_test"
testdir = os.path.join(os.getenv("MAST_INSTALL_PATH"),'test',testname)

class TestRecipeplan(unittest.TestCase):

    def setUp(self):
        os.chdir(testdir)

    def tearDown(self):
        removelist=list()
        removelist.append("recipedir/status.txt")
        removelist.append("recipedir/ing2b/INCAR")
        removelist.append("recipedir/ing2b/POSCAR")
        removelist.append("recipedir/ing2b/POTCAR")
        removelist.append("recipedir/ing2b/KPOINTS")
        removelist.append("recipedir/ing2b/submit.sh")
        for myfile in removelist:
            try:
                os.remove(myfile)
            except OSError:
                pass

    def test___init__(self):
        rp = RecipePlan("test_recipe","recipedir")
        self.assertEquals(rp.working_directory,"recipedir")
        self.assertEquals(rp.status,"I")
        self.assertEquals(rp.name,"test_recipe")
        #raise SkipTest
        #self.testclass.__init__(name, working_directory)

    def test_write_ingredient(self):
        topmetad = MASTFile("files/top_metadata_single")
        topmetad.data.append("origin_dir = %s/files\n" % testdir) #give origin directory
        topmetad.to_file("recipedir/metadata.txt")
        #metad = MASTFile("files/metadata_single")
        #metad.to_file("%s/metadata.txt" % ingdir)
        rp = RecipePlan("test_recipe","recipedir")
        rp.ingredients['ing2b'] = "I"
        kdict=dict()
        kdict['mast_program']='vasp'
        kdict['mast_xc']='pw91'
        kdict['mast_kpoints']=[1,2,3,"G"]
        rp.ingred_input_options['ing2b']=dict()
        rp.ingred_input_options['ing2b']['name']="recipedir/ing2b"
        rp.ingred_input_options['ing2b']['program_keys']=kdict
        rp.ingred_input_options['ing2b']['structure']=pymatgen.io.vaspio.Poscar.from_file("files/perfect_structure").structure
        rp.write_methods['ing2b']='write_singlerun'
        rp.write_ingredient('ing2b')
        self.assertTrue(os.path.isfile('recipedir/ing2b/INCAR'))
        self.assertTrue(os.path.isfile('recipedir/ing2b/POSCAR'))
        self.assertTrue(os.path.isfile('recipedir/ing2b/POTCAR'))
        self.assertTrue(os.path.isfile('recipedir/ing2b/KPOINTS'))
        self.assertTrue(os.path.isfile('recipedir/ing2b/submit.sh'))
        #self.testclass.write_ingredient(iname)

    def test_complete_ingredient(self):
        topmetad = MASTFile("files/top_metadata_single")
        topmetad.data.append("origin_dir = %s/files\n" % testdir) #give origin directory
        topmetad.to_file("recipedir/metadata.txt")
        #metad = MASTFile("files/metadata_single")
        #metad.to_file("%s/metadata.txt" % ingdir)
        rp = RecipePlan("test_recipe","recipedir")
        rp.ingredients['ing1'] = "I"
        kdict=dict()
        kdict['mast_program']='vasp'
        kdict['mast_xc']='pw91'
        kdict['mast_kpoints']=[1,2,3,"G"]
        rp.ingred_input_options['ing1']=dict()
        rp.ingred_input_options['ing1']['name']="recipedir/ing1"
        rp.ingred_input_options['ing1']['program_keys']=kdict
        rp.ingred_input_options['ing1']['structure']=pymatgen.io.vaspio.Poscar.from_file("files/perfect_structure").structure
        rp.complete_methods['ing1']='complete_singlerun'
        self.assertTrue(rp.complete_ingredient('ing1'))
        #self.testclass.complete_ingredient(iname)

    def test_ready_ingredient(self):
        raise SkipTest
        #self.testclass.ready_ingredient(iname)

    def test_run_ingredient(self):
        raise SkipTest
        #self.testclass.run_ingredient(iname)

    def test_update_children(self):
        raise SkipTest
        #self.testclass.update_children(iname)

    def test_fast_forward_check_complete(self):
        raise SkipTest
        #self.testclass.fast_forward_check_complete()

    def test_check_if_have_parents(self):
        raise SkipTest
        #self.testclass.check_if_have_parents()

    def test_check_if_ready_to_proceed_are_complete(self):
        raise SkipTest
        #self.testclass.check_if_ready_to_proceed_are_complete()

    def test_check_if_parents_are_complete(self):
        raise SkipTest
        #self.testclass.check_if_parents_are_complete()

    def test_run_staged_ingredients(self):
        raise SkipTest
        #self.testclass.run_staged_ingredients()

    def test_check_recipe_status(self):
        raise SkipTest
        #self.testclass.check_recipe_status(verbose=1)

    def test_print_status(self):
        raise SkipTest
        #self.testclass.print_status(verbose=1)

    def test___repr__(self):
        raise SkipTest
        #self.testclass.__repr__()

    def test_get_statuses_from_file(self):
        rp = RecipePlan("test_recipe","recipedir")
        mystatus = MASTFile("files/status_random.txt")
        self.assertRaises(MASTError, rp.get_statuses_from_file)
        mystatus.to_file("recipedir/status.txt")
        rp.ingredients['ing1']="I"
        rp.ingredients['ing2a']="I"
        rp.ingredients['ing2b']="I"
        self.assertRaises(MASTError,rp.get_statuses_from_file)
        rp.ingredients['ing3']="I"
        rp.get_statuses_from_file()
        statusdict=dict()
        statusdict={'ing1':'alpha','ing2a':'beta','ing2b':'gamma','ing3':'delta'}
        self.assertEquals(rp.ingredients, statusdict)
        #self.testclass.get_statuses_from_file()

