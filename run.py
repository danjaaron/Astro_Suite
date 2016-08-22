
# -------------- #

def parse_command_line(inputs,argv):
	# handles user-specified command line arguments
	if (len(argv) > 1):
		first_arg = argv[1]
		if (first_arg == '-help'):
			print "Available command line arguments:"
			print "-show *template_function* \n (e.g. '-show all', '-show vis')"
			sys.exit()
		elif (first_arg == '-show'):
			inputs['show_settings'](inputs,argv[2:])
			sys.exit()
		else:
			print "Command line argument not recognized."

# -------------- #

# configure system
import sys, os
sys.dont_write_bytecode = True
# create inputs from template
import Templates.create_project as cproj
from project import template
inputs = cproj.create_inputs(template)
inputs['template'] = template
# handle command line arguments
parse_command_line(inputs,sys.argv)
# adjust template to project specifications
from project import project_inputs
project_inputs(inputs)
# build architecture based on inputs
import Packages
from Packages.Generate import *
Packages.Generate.generate_architecture.architect(inputs)
from Packages.Current_Project import *
from Packages.Sim_Functions import *
from Packages.Sim_Functions.Meta import *
from Packages.Meshing_Functions import *
from Packages.Meshing_Functions.Meta import *
from Packages.Projects import *

# -------------- #

# run project
cproj.run_project(inputs)

