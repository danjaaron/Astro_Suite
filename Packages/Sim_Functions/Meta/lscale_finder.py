import os, sys

def run_sim(inputs):
	assert(inputs['sim_style'] == 'serial'), \
		"lscale_finder meta can only run in serial mode."
	# check for log file
	lscale_path = os.getcwd()+'/Packages/Projects/'+inputs['project_name']+'/Logs/lscale.txt'
	if (os.path.isfile(lscale_path) and (raw_input('> lscale.txt found in project folder, overwrite? (y/n) ') != 'y')):
		sys.exit()
	lscale_file = open(lscale_path,'w')
	# assign from inputs
	inputs['check_lscale'] = True
	exec ('from Packages.Sim_Functions.' + inputs['sim_file'] + ' import run_sim as simulate')
	verbose = inputs['verbose']
	# test all lscales in range
	feasible_lscales = []
	for ls in inputs['lscale_range']:
		inputs['lscale'] = ls
		try:
			simulate(inputs)
		except AssertionError:
			if (verbose):
				print "lscale: {0} too large (rounds off to zero), moving forward.".format(ls)
		except NameError:
			if (verbose):
				print "lscale: {0} too small (molecule count > max uint), moving forward.".format(ls)
		else:
			if (verbose):
				print "lscale: {0} IS feasible, adding to feasible list.".format(ls)
			feasible_lscales.append(ls)
	# write feasible lscales to file
	for fl in feasible_lscales:
		lscale_file.write(str(fl)+'\n')
	lscale_file.close()
	return True