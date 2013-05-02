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

import numpy as np
import pymatgen as pmg

from MAST.utility import InputOptions
from MAST.utility import MASTObj
from MAST.utility import MASTError

ALLOWED_KEYS = {\
                 'inputfile'    : (str, 'mast.inp', 'Input file name'),\
               }

MAST_KEYWORDS = {'program': 'vasp',
                 'system_name': 'mast',
                 'scratch_directory': os.path.expanduser(os.environ['MAST_SCRATCH']),
                }

STRUCTURE_KEYWORDS = {'posfile': None,
                      'spacegroup': None,
                      'symmetry_only': False,
                      'coord_type': 'cartesian',
                      'atom_list': list(),
                      'coordinates': list(),
                      'lattice': list(),
                     }

UNITCELL_KEYWORDS = ['lattice_constant',
                     'a',
                     'b',
                     'c',
                     'alpha',
                     'beta',
                     'gamma',
                    ]

DEFECTS_KEYWORDS = ['coord_type',
                    'vacancy',
                    'interstial',
                    'antisite',
                   ]

INGREDIENTS_KEYWORDS = ['singlepoint',
                        'optimization',
                        'neb',
                   ]

RECIPE_KEYWORDS = {'recipe_file': None,
                  }

class InputParser(MASTObj):
    """Parses input file and returns the options.
    """
    def __init__(self, **kwargs):
        MASTObj.__init__(self, ALLOWED_KEYS, **kwargs)
        self.section_end = '$end'
        self.delimiter = ' ' # how we're breaking up each line
        self.section_parsers = {\
                                    'mast'     : self.parse_mast_section,
                                    'structure' : self.parse_structure_section,
                                    'ingredients' : self.parse_ingredients_section,
                                    'defects'  : self.parse_defects_section,
                                    'recipe'   : self.parse_recipe_section,
                                    'neb'      : self.parse_neb_section,
                                    'chemical_potentials' : self.parse_chemical_potentials_section,
                               }

    def parse(self):
        """Parses information from the input file"""
        options   = InputOptions()
        infile    = file(self.keywords['inputfile'])
# read in the input file and convert everything to lower case
        contents  = infile.read().lower()
        infile.close()

        sections  = contents.strip().split(self.section_end)[:-1]
        for section_content in sections:
# First we strip off any whitespace from each line, then split it according to
# newline.  We then filter out any blank lines, then any lines that would be a comment,
# i.e. starts with a \'#\' or a \'!\' symbol.
            section_content = section_content.strip().split('\n')
            section_content = [line for line in section_content if line]
            section_content = [line for line in section_content if not (line.startswith('#') or \
                                                                        line.startswith('!'))]
            section_name = section_content[0][1:]

            print '\nFound section %s.  Reading in options.' % section_name
            if section_name not in self.section_parsers:
                error = 'Section %s not recognized' % section_name
                MASTError(self.__class__.__name__, error)
                return

            self.section_parsers[section_name](section_name, section_content[1:], options)
            print 'Finished parsing section %s.' % section_name

        return options

    def parse_mast_section(self, section_name, section_content, options):
        """Parse the mast section and populate the options"""
        mast_dict = MAST_KEYWORDS.copy()

        for line in section_content:
            line = line.split(self.delimiter)
            if (line[0] not in mast_dict):
                error = 'Section keyword %s not recognized' % line[0]
                MASTError(self.__class__.__name__, error)
                return
            else:
                mast_dict[line[0]] = line[1]

        for key, value in mast_dict.items():
            options.set_item(section_name, key, value)
        print mast_dict

    def parse_structure_section(self, section_name, section_content, options):
        """Parse the structure section and populate the options

            Format is along the lines of:
                coord_type fractional

                begin coordinates
                Ga 0.000000 0.000000 0.000000
                Ga 0.500000 0.500000 0.000000
                Ga 0.000000 0.500000 0.500000
                Ga 0.500000 0.000000 0.500000
                As 0.250000 0.250000 0.250000
                As 0.750000 0.750000 0.250000
                As 0.250000 0.750000 0.750000
                As 0.750000 0.250000 0.750000
                end

                begin lattice
                2.0 0.0 0.0
                0.0 2.0 0.0
                0.0 0.0 2.0
                end

            Note that coord_type will default to "cartesian" if not specified.

        """
        structure_dict = STRUCTURE_KEYWORDS.copy() # Initialize with default values
        subsection_dict = dict()

        for line in section_content:
            line = line.split(self.delimiter)

            if (line[0] in structure_dict):
                structure_dict[line[0]] = line[1]
            elif ('begin' in line[0]):
                subsection = line[1]
                subsection_list = list()
            elif ('end' not in line):
                subsection_list.append(line)
            elif ('end' in line):
                subsection_dict[subsection] = subsection_list

# Here we the .title() to re-capitalize the first letter of all the atomic symbols to comply with what
# pymatgen needs
#                    structure_dict['atom_list'].append(line[0].title())
#                    structure_dict['coordinates'].append(line[1:])

#        print 'in InputParser.parse_structure_section:', subsection_dict
        for key, value in subsection_dict.items():
            if (key == 'coordinates'):
                value = np.array(value)
                structure_dict['atom_list'] = [val.title() for val in value[:, 0]]
                structure_dict['coordinates'] = np.array(value[:, 1:], dtype='float')
            if (key == 'lattice'):
                structure_dict['lattice'] = np.array(value, dtype='float')

        for key, value in structure_dict.items():
            options.set_item(section_name, key, value)

    def parse_defects_section(self, section_name, section_content, options):
        """Parse the defects section and populate the options.
            This will get removed in favor of a defects section down in ingredients
        """
        defect_types = dict()

        count = 0
        for line in section_content:
            type_dict = dict()

            line = line.split(self.delimiter)

            if (line[0] == 'coord_type'):
                defect_types['coord_type'] = line[1]
            else:
                coord = line[1:-1]

                type_dict['type'] = line[0]
                type_dict['coordinates'] = np.array(coord, dtype='float')
                type_dict['symbol'] = line[-1]

                defect_types['defect%i' % count] = type_dict

                count += 1

        if ('coord_type' not in defect_types):
            defect_types['coord_type'] = 'cartesian'

        options.set_item(section_name, 'num_defects', count)
        options.set_item(section_name, 'defects', defect_types)

    def parse_recipe_section(self, section_name, section_content, options):
        """Parse the recipe section and populate the options"""
        recipe_dict = RECIPE_KEYWORDS.copy()

        for line in section_content:
            line = line.split(self.delimiter)
            if (line[0] not in recipe_dict):
                error = 'Section keyword %s not recognized' % line[0]
                MASTError(self.__class__.__name__, error)
                return
            elif (line[0] == 'recipe_file'):
                try:
                    recipe_path = os.environ['MAST_RECIPE_PATH']
                except KeyError:
                    error = 'MAST_RECIPE_PATH environment variable not set'
                    MASTError(self.__class__.__name__, error)
 
                recipe_dict['recipe_file'] = '%s/%s' % (recipe_path, line[1])
            else:
                recipe_dict[line[0]] = line[1]

        for key, value in recipe_dict.items():
            options.set_item(section_name, key, value)

    def parse_ingredients_section(self, section_name, section_content, options):
        """Parse the ingredients section and populate the options
            Section takes the form of:
                $ingredients
                begin ingredients_global
                kpoints 3x3x3
                xc pbe
                end

                begin singlepoint
                encut 400
                end

                begin optimize
                encut 300
                ibrion 2
                end

                $end

            kpoints are parsed out as a 3 index list of integers, everything else is parsed out
            as a string.

            Anything in ingredients_global are then appended onto each individual ingredient.
        """

        global_dict = dict()
        ingredients_dict = dict()

        for line in section_content:
            if (line.startswith('begin')):
# Each ingredient section starts with "begin", check for this line, and initialize the individual
# ingredient dictionary
                ingredient_name = line.split()[1]
                ingredient_dict = dict()
            elif ('end' not in line):
                opt = line.split()
#                print opt
                if (opt[0] == 'mast_kpoints'):
                    kpts = map(int, opt[1].split('x'))
                    if len(opt) > 2:
                        kpts.append(opt[2])
                    ingredient_dict[opt[0]] = kpts
                else:
                    ingredient_dict[opt[0]] = opt[1]
            elif ('end' in line):
# Each ingredient section ends with "end", if present finish that current section and assign
# the neccessary element in the ingredients dictionary and create the global dictionary
                if (ingredient_name == 'ingredients_global'):
                    global_dict = ingredient_dict
                else:
                    ingredients_dict[ingredient_name] = ingredient_dict

# Each value in ingredients_dict is a dictionary containing the relevant
# ingredient and option(s).  We append the global_dict (containing global
# ingredients options here, after checking to make sure the ingredient in
# question does not contain the option/value.
        for ing_key, ing_value in ingredients_dict.items():
            for glob_key, glob_value in global_dict.items():
                if glob_key not in ing_value:
                    ing_value[glob_key] = glob_value
            options.set_item(section_name, ing_key, ing_value)

        options.set_item(section_name, 'global', global_dict)

        #TTM add defects section
        if options.get_item('defects','num_defects') == None:
            print "TTM DEBUG: PASS IN DEFECTS"
            pass
        else:
            for ingname in ingredients_dict.keys():
                print "TTM DEBUG: SETTING mast_defects for", ingname
                ingredients_dict[ingname]['mast_defects'] = options.get_item('defects','defects')
        #print "OPTIONS DEBUG TTM: ", options
#        print 'DEBUG: ingredients_dict =', ingredients_dict

    def parse_neb_section(self, section_name, section_content, options):
        """Parse the neb section and populate the options.
            Format example:
            hops 1-2 1-3 3-4
            images 3
            The hops correspond to the defects listed in the defects
            section, e.g. defects 1 through 4 are:
            vacancy 0 0 0
            vacancy 0.5 0.5 0.5 
            interstitial 0.25 0.25 0
            interstitial 0.25 0.75 0
        """
        hoplist = list()
        hopfrom = dict()
        images = 0

        count = 0
        for line in section_content:
            type_dict = dict()
            line = line.strip()
            line = line.split(self.delimiter)

            if (line[0] == 'hops'):
                hoplist = line[1:] #this is a list
            elif (line[0] == 'images'):
                images = int(line[1])
        hop=""
        hfrom=0
        hto=0
        for hop in hoplist:
            hfrom = int(hop.split('-')[0])
            hto = int(hop.split('-')[1])
            if not hfrom in hopfrom.keys():
                hopfrom[hfrom]=list()
            hopfrom[hfrom].append(hto)
        print "images: ", images
        print "hopfrom_dict: ", hopfrom
        options.set_item(section_name, 'images', images)
        options.set_item(section_name, 'hopfrom_dict', hopfrom)

    def parse_chemical_potentials_section(self, section_name, section_content,
                                          options):
        """Parse the chemical_potentials section and populate the options.
            Section uses the standard begin...end subsection structure, but with
            a modification:  instead of strict subsection titles (i.e. structure,
            lattice etc.), subsection titles are the conditions under which the
            chemical potentials are for.  Any combination of white spacing is
            allowed, however note that all conditions will be converted to lower
            case first!

            Using a GaAs example, hypothetically we could have a chemical_potential
            section like the following:
                $chemical_potentials
                begin As rich
                Ga 4.5
                As 3.5
                end

                begin Ga rich
                Ga 3.5
                As 4.5
                end
                $end

            For charged defects, note that the chemical potential of the
            electron will be calculated automatically from the Fermi level and
            appropiate potential shift correction.  However, if one desires to
            manually give an electron chemical potential (for whatever reason!)
            this can be done by specifiying \'electron\' in the appropiate
            condition.
        """
        chempot_dict = dict()

        for line in section_content:
            if (line.startswith('begin')):
                condition_name = ' '.join(line.split()[1:])
                condition_dict = dict()
            elif ('end' not in line):
                opt = line.split()
                condition_dict[opt[0]] = float(opt[1])
            elif ('end' in line):
                chempot_dict[condition_name] = condition_dict

        for key, value in chempot_dict.items():
            options.set_item(section_name, key, value)

#        print 'DEBUG: chempot_dict =', chempot_dict

