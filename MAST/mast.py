############################################################################
# MAterials Simulation Toolbox (MAST)
# Version: January 2013
# Programmers: Tam Mayeshiba, Tom Angsten, Glen Jenness, Hyunwoo Kim,
#              Kumaresh Visakan Murugan, Parker Sear
# Created at the University of Wisconsin-Madison.
# Replace this section with appropriate license text before shipping.
# Add additional programmers and schools as necessary.
############################################################################
import os
import time

from MAST.utility import MASTObj
from MAST.utility import MAST2Structure
from MAST.utility import MASTError
from MAST.utility.picklemanager import PickleManager
from MAST.utility.dirutil import *
from MAST.utility import InputOptions

#from MAST.ingredients.ingredients_loader import IngredientsLoader

from MAST.parsers import InputParser
from MAST.parsers import IndepLoopInputParser
from MAST.parsers import InputPythonCreator
from MAST.parsers.recipetemplateparser import RecipeTemplateParser
from MAST.recipe.recipesetup import RecipeSetup

from MAST.ingredients import *

ALLOWED_KEYS     = {\
                       'inputfile'    : (str, 'mast.inp', 'Input file name'),\
                       'outputfile'   : (str, 'mast.out', 'Output file name'),\
                   } 


class MAST(MASTObj):
    """User interface to set up a calculation group.

        Each instance of Interface sets up one calculation group.

        Attributes:
            self.input_options <InputOptions object>: used to store the options
                                           parsed from input file

    """

    def __init__(self, **kwargs):
        MASTObj.__init__(self, ALLOWED_KEYS, **kwargs)
        self.input_options = None
        #self.recipe_name = None
        #self.structure = None
        #self.unique_ingredients = None

    def check_independent_loops(self):
        """Checks for independent loops. If no independent loops are found,
            parse and run the input file. Otherwise, parse and run the
            generated set of input files.
        """
        ipl_obj = IndepLoopInputParser(inputfile=self.keywords['inputfile'])
        loopfiles = ipl_obj.main()
        #print "TTM DEBUG: loopfiles: ", loopfiles
        if len(loopfiles) == 0:
            self.parse_and_run_input()
        else:
            for ipfile in loopfiles:
                self.keywords['inputfile']=ipfile
                self.parse_and_run_input()


    def parse_and_run_input(self):
        """
            Parses the *.inp input file and fetches the options.
            Sets an input stem name.
            Parses the recipe template file and creates a personalized recipe.
            Creates a *.py input script from the fetched options.
            Runs the *.py input script.
        """ 
        #parse the *.inp input file
        parser_obj = InputParser(inputfile=self.keywords['inputfile'])
        self.input_options = parser_obj.parse()
        
        #set additional keys
        #self._set_structure_from_inputs()
        #self._set_input_stem_and_timestamp()
        #self._set_sysname_and_working_directory()
        #self._validate_execs()

        #create the *.py input script
        ipc_obj = InputPythonCreator(input_options=self.input_options)
        ipc_filename = ipc_obj.write_script()
        
        #run the *.py input script
        import subprocess
        oppath=self.input_options.get_item('mast','input_stem') + 'output'
        opfile = open(oppath, 'ab')
        run_input_script = subprocess.Popen(['python ' + ipc_filename], 
                shell=True, stdout=opfile, stderr=opfile)
        run_input_script.wait()
        opfile.close()
        return None
   

    def _set_input_stem_and_timestamp(self):
        inp_file = self.keywords['inputfile']
        if not ".inp" in inp_file:
            raise MASTError(self.__class__.__name__, "File '%s' should be named with a .inp extension and formatted correctly." % inp_file)
        
        timestamp = time.strftime('%Y%m%dT%H%M%S')
        tstamp = time.asctime()

        stem_dir = os.path.dirname(inp_file)
        if len(stem_dir) == 0:
            stem_dir = get_mast_scratch_path()
        inp_name = os.path.basename(inp_file).split('.')[0]
        stem_name = os.path.join(stem_dir, inp_name + '_' + timestamp + '_')
        self.input_options.update_item('mast', 'input_stem', stem_name)
        self.input_options.update_item('mast', 'timestamp', tstamp)

    def _set_sysname_and_working_directory(self):
        """Get the system name and working directory."""
        element_str = self._get_element_string()
        ipf_name = '_'.join(os.path.basename(self.input_options.get_item('mast','input_stem')).split('_')[0:-1]).strip('_')
              
        system_name = self.input_options.get_item("mast", "system_name", "sys")
        system_name = system_name + '_' + element_str

        dir_name = "%s_%s_%s_%s" % (system_name, element_str, self.input_options.get_item('recipe','recipe_name'), ipf_name)
        dir_path = os.path.join(self.input_options.get_item('mast', 'scratch_directory'), dir_name)
        self.input_options.update_item('mast', 'working_directory', dir_path)
        self.input_options.update_item('mast', 'system_name', system_name)

    def _get_element_string(self):
        """Get the element string from the structure."""
        mystruc = self.input_options.get_item('structure','structure')
        elemset = set(mystruc.species)
        elemstr=""
        elemok=1
        while elemok == 1:
            try:
                elempop = elemset.pop()
                elemstr = elemstr + elempop.symbol
            except KeyError:
                elemok = 0
        return elemstr
    def _validate_execs(self):
        """Make sure each ingredient has a mast_exec line."""
        for ingredient, options in self.input_options.get_item('ingredients').items():
            print ingredient, options
            if 'mast_exec' in options:
                have_exec = True
                break
            else:
                have_exec = False

        if (not have_exec):
            error = 'mast_exec keyword not found in the $ingredients section'
            raise MASTError(self.__class__.__name__, error)
    def _set_structure_from_inputs(self):
        """Make a pymatgen structure and update the 
            structure key.
        """
        strposfile = self.input_options.get_item('structure','posfile')
        if strposfile is None:
            iopscoords=self.input_options.get_item('structure','coordinates')
            iopslatt=self.input_options.get_item('structure','lattice')
            iopsatoms=self.input_options.get_item('structure','atom_list')
            iopsctype=self.input_options.get_item('structure','coord_type')
            structure = MAST2Structure(lattice=iopslatt,
                coordinates=iopscoords, atom_list=iopsatoms,
                coord_type=iopsctype)
        elif ('poscar' in strposfile.lower()):
            from pymatgen.io.vaspio import Poscar
            structure = Poscar.from_file(strposfile).structure
        elif ('cif' in strposfile.lower()):
            from pymatgen.io.cifio import CifParser
            structure = CifParser(strposfile).get_structures()[0]
        else:
            error = 'Cannot build structure from file %s' % strposfile
            raise MASTError(self.__class__.__name__, error)
        self.input_options.update_item('structure','structure',structure)
    def start_from_input_options(self, input_options):
        """Start the recipe template parsing and ingredient creation
            once self.input_options has been set.
        """
        print 'in start_from_input_options'
        self.input_options = input_options
        
        #parse the recipe template file and create a personal file
        self.make_working_directory()
        self._parse_recipe_template()

        #make recipe plan object
        setup_obj = RecipeSetup(recipeFile=self.input_options.get_item('mast','input_stem') + 'personal_recipe.txt', 
                inputOptions=self.input_options,
                structure=self.input_options.get_item('structure','structure'), 
                )
        recipe_plan_obj = setup_obj.start()

        self.pickle_plan(recipe_plan_obj)
        self.pickle_input_options() 

    def make_working_directory(self):
        """Initialize the directory information for writing the 
            recipe and ingredient folders.
        """
        dir_path = self.input_options.get_item('mast',
                    'working_directory')
        try:
            os.mkdir(dir_path)
            topmeta = Metadata(metafile='%s/metadata.txt' % dir_path)
            topmeta.write_data('directory created', self.input_options.get_item('mast', 'timestamp'))
            topmeta.write_data('system name', self.input_options.get_item('mast','system_name'))
        except:
            MASTError(self.__class__.__name__, "Cannot create working directory %s !!!" % dir_path)

    def pickle_plan(self, recipe_plan_obj):
        """Pickles the reciple plan object to the respective file
           in the scratch directory
        """

        pickle_file = os.path.join(self.input_options.get_item('mast', 'working_directory'), 'mast.pickle')
        pm = PickleManager(pickle_file)
        pm.save_variable(recipe_plan_obj) 
   
    def pickle_input_options(self):
        """Temporary solution to input_options not being saved to the pickle correctly"""

        pickle_file = os.path.join(self.input_options.get_item('mast', 'working_directory'), 'input_options.pickle')
        pm = PickleManager(pickle_file)
        pm.save_variable(self.input_options)

    def _parse_recipe_template(self):
        """Parses the recipe template file."""

        recipe_file = self.input_options.get_item('recipe', 'recipe_file')

        parser_obj = RecipeTemplateParser(templateFile=recipe_file, 
            inputOptions=self.input_options,
            personalRecipe=self.input_options.get_item('mast','input_stem') + 'personal_recipe.txt',
            working_directory=self.input_options.get_item('mast', 'working_directory')
                                         )
        self.input_options.update_item('recipe','recipe_name', parser_obj.parse())

