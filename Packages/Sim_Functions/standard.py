from Sim_Tools.standard_tools import *

def run_sim(inputs):
	imports(inputs)
	all_initials(inputs)

	pre_loop(inputs)
	report(inputs,'initials')
	loop(inputs)
	report(inputs,'sim_block')
	report(inputs,'finals')

	tprofiling(inputs,inputs['tprofiling_final'])
	logging(inputs)


