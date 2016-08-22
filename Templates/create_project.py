# imports for run 
import numpy, math, time, os, sys
# configure system
sys.dont_write_bytecode = True


def create_inputs(template_name='default'):
	global tname
	tname = template_name
	# load template and create inputs
	exec ( "from Templates.{0} import set_all".format(template_name) ) in globals()
	inputs = set_all()
	return inputs

def run_project(inputs):
	# check inputs before running
	exec ( "from Templates.{0} import check_inputs".format(tname) )
	check_inputs(inputs)
	# run project meta functions
	sys.modules[("Packages.Meshing_Functions.Meta."+inputs['mesh_meta'])].run_meshing(inputs)
	sys.modules[("Packages.Sim_Functions.Meta."+inputs['sim_meta'])].run_sim(inputs)
