# import system
import itertools, os, sys

def run_sim(inputs):
	assert(inputs['sim_style'] == 'serial'), \
		"steadystate meta can only run in serial mode."
	# designate recorded section
	for s in inputs['h'].allsec():
		inputs['record_section'] = s
		break 
	# check for log file
	ss_path = os.getcwd() + '/Packages/Projects/'+inputs['project_name']+'/Logs/steadystate.txt'
	if (os.path.isfile(ss_path) and (raw_input('> steadystate.txt found in project folder, overwrite? (y/n) ') != 'y')):
		sys.exit()
	ss_file = open(ss_path,'w')
	# write original inputs
	ss_file.write('original inputs: \n {0} \n'.format(str(inputs['original'])))
	# assign from inputs
	initial_values = inputs['initial_values']
	exec ('from Packages.Sim_Functions.' + inputs['sim_file'] + ' import run_sim as simulate')
	# assign and run all permutations of initial values
	for permutation in itertools.product(*initial_values.values()):
		new_initials = {}
		# assign and simulate
		for val_key in xrange(len(initial_values)):
			new_initials[ (initial_values.keys()[val_key]) ] = [permutation[val_key]]
		inputs['initial_values'] = new_initials
		simulate(inputs)
		# log all results to file
		ss_file.write('------------\n')
		# write initials
		for iv, ival in new_initials.iteritems():
			ss_file.write('{0} {1} \n'.format(iv,str(ival)))
		ss_file.write('~~~~\n')
		# write results
		for rv in inputs['record_variables']:
			ss_file.write('{0} {1} \n'.format(rv,str(getattr(inputs['record_section'],rv))))
	ss_file.close()
	return True