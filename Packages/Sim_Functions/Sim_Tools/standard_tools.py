# import system
import os, sys, numpy, math, time

def report_section(inputs, record_section, print_string):
	h = inputs['h']
	header1 = "+---> REPORTING {0} <---+".format(print_string[:1].upper() + print_string[1:])
	header2 = '+'+(''.join(['-' for c in xrange(len(header1)-2)]))+'+'
	print header1
	print "---> report_section() <---"
	record_section.push()
	print "section: {0}".format(h.secname())
	print '___ initial values ___'
	for ivar, ival in inputs['initial_values'].iteritems():
		print "~ {0}: {1}".format(ivar,getattr(record_section(0.5),ivar+inputs['mod_suffix']))
	print '___ record variables ___'
	for ivar in inputs['record_variables']:
		print "~ {0}: {1}".format(ivar,getattr(record_section,ivar))
	h.pop_section()
	print header2

def tsupdate(inputs):
	if inputs['run_STEPS']:
		tprofiling(inputs,'update_tsupdate')
		for tet, tet_sl in inputs['tet_hoc'].iteritems():
			for rv in inputs['read_vars']:
				rv[0](inputs,tet)
			for s in tet_sl:
				for wv in inputs['write_vars']:
					wv(inputs,tet,s)
				for rv in inputs['read_vars']:
					rv[1](inputs,tet,s)
			for rv in inputs['read_vars']:
				rv[2](inputs,tet)
		tprofiling(inputs,'update_tsupdate')

def gaps(inputs):
	if (inputs['gaps']):
		tprofiling(inputs,'update_gaps')
		gap_species = inputs['gap_species']
		h = inputs['h']
		gaps = inputs['gaps']
		set_gap = {}
		# gather values
		for section, pairlist in inputs['gaps'].iteritems():
			set_gap[section] = {}
			for gs_others, gs_self in gap_species.iteritems():
				s_others = 0.00
				s_self = getattr(section(0.5),gs_self)
				for pair in pairlist:
					s_others += (getattr(pair(0.5),gs_self) - s_self)
				set_gap[section][gs_others] = s_others
		# set values
		for section in set_gap.keys():
			for gs_others, s_others in set_gap[section].iteritems():
				setattr(section(0.5), gs_others, s_others)
		tprofiling(inputs,'update_gaps')


def set_time(inputs):
	# set NEURON time (ms)
	inputs['h'].tstop = inputs['tstop']
	inputs['h'].dt = inputs['dt']
	inputs['h'].steps_per_ms = (1.0/inputs['dt'])

	# set STEPS time (s)
	INT = inputs['h'].tstop*1e-3
	DT = inputs['h'].dt*1e-3
	tpnts = numpy.arange(0,INT+DT,DT)
	ntpnts = len(tpnts)

	# save time settings to inputs
	inputs['tpnts'] = tpnts
	inputs['ntpnts'] = ntpnts
	inputs['INT'] = INT
	inputs['DT'] = DT

def set_sim_style(inputs):
	# choose simulation style
	if (inputs['sim_style'] == 'parallel') and (inputs['run_STEPS']):
		import steps.mpi.solver as solvmod
		import steps.utilities.geom_decompose as gd
		tet_hosts = gd.binTetsByAxis(inputs['mesh'], steps.mpi.nhosts)
		sim = solvmod.TetOpSplit(inputs['model'], inputs['mesh'], inputs['rng'], False, tet_hosts)
		inputs['sim'] = sim
	elif (inputs['sim_style'] == 'serial') and (inputs['run_STEPS']):
		import steps.solver as solvmod
		sim = solvmod.Tetexact(inputs['model'], inputs['mesh'], inputs['rng'])
		inputs['sim'] = sim
	elif (inputs['run_STEPS']) and (inputs['sim_style'] == None):
		print "FATAL ERROR ({0}): no sim style detected, but mesh exists.".format(os.path.basename(os.path.abspath(__file__)))
		sys.exit()

def set_vis_log(inputs):
	# set up logging dicts for visualization
	for v, sl in inputs['vis_log_sects'].iteritems():
		new_list = []
		if (sl == ['all_sects']):
			for s in inputs['h'].allsec():
				new_list.append(s)
			inputs['vis_log_sects'][v] = new_list

	if (inputs['run_STEPS']):
		for v, tl in inputs['vis_log_tets'].iteritems():
			new_list = []
			if (tl == ['all_tets']):
				for tet in inputs['comp'].tets:
					new_list.append(tet)
				inputs['vis_log_tets'][v] = new_list

	for v, sl in inputs['vis_log_sects'].iteritems():
		inputs['vis_log_sects'][v] = {}
		for s in sl:
			inputs['vis_log_sects'][v][s] = []

	if (inputs['run_STEPS']):
		for v, tl in inputs['vis_log_tets'].iteritems():
			inputs['vis_log_tets'][v] = {}
			for tet in tl:
				inputs['vis_log_tets'][v][tet] = []

def pre_loop(inputs):
	tprofiling(inputs,'pre_loop')

	# tet initials 
	if inputs['run_STEPS']:
		inputs['sim'].reset()

	# sect initials
	for s in inputs['h'].allsec():
		for ivar, ival in inputs['initial_values'].iteritems():
			setattr(s(0.5),ivar+inputs['mod_suffix'],ival[0])

	# tet stimulate
	if inputs['run_STEPS']:
		for tet, stimvals in inputs['stim_tets'].iteritems():
			inputs['sim'].setTetConc(tet,stimvals[0],stimvals[1])

	# sect stimulate 
	for s, stimvals in inputs['stim_sects'].iteritems():
		setattr(s(0.5),stimvals[0],stimvals[1])

	# pre-simulation
	inputs['h']("{finitialize()}")
	if inputs['run_STEPS']:
		inputs['sim'].run(inputs['tpnts'][0])
		inputs['tind'] = 0
	
	# update all
	tsupdate(inputs)
	gaps(inputs)

	tprofiling(inputs,'pre_loop')

def report(inputs,stage):
	if inputs['reporting_enabled']:
		if ((stage in inputs['report_stages']) or (inputs['report_stages'] == ['all'])):
			if (stage == 'sim_block'):
				print '\n{:=^30}'.format(" {0} ".format(os.path.basename(__file__)))
				for tag, slist in inputs['sim_report_block'].iteritems():
					print tag.format(*[ inputs[sv] for sv in slist[:-1] ])
				print '{:=^30}\n'.format( "" )
			elif ( (stage == 'initials') or (stage == 'finals') ):
				for s in inputs['h'].allsec():
					report_section(inputs, s, stage)
					break 

def vis_log(inputs):
	# log variables for visualization
	tprofiling(inputs,'vis_log_sects')
	for v, sl in inputs['vis_log_sects'].iteritems():
		for s in sl:
			inputs['vis_log_sects'][v][s].append(getattr(s(0.5),v))
	tprofiling(inputs,'vis_log_sects')

	if inputs['run_STEPS']:
		tprofiling(inputs,'vis_log_tets')
		for v, tl in inputs['vis_log_tets'].iteritems():
			for tet in tl:
				inputs['vis_log_tets'][v][tet].append(inputs['sim'].getTetConc(tet,v))
		tprofiling(inputs,'vis_log_tets')


def tprofiling(inputs,stage):
	if (inputs['tprofiling_enabled']):

		if (stage == 'absolute'):
			print '\n{:=^30}'.format(" tprofiling() ")
			for stage, interval in inputs['tprofiling'].iteritems():
				print '{:^30}'.format( "{0}: {1:.2f} s".format(stage, interval) )
			print '{:=^30}\n'.format( "" )

		elif (stage == 'percentage'):
			print '\n{:=^30}'.format(" tprofiling() ")
			tmax = max(inputs['tprofiling'].values())
			for stage, interval in inputs['tprofiling'].iteritems():
				print '{:^30}'.format( "{0}: {1:.2f}% of total".format(stage, 100.0*interval/tmax ) )
			print '{:=^30}\n'.format( "" )

		elif ((stage in inputs['tprofiling_stages']) or (inputs['tprofiling_stages'] == ['all'])):

			if (stage == 'reset'):
				inputs['tprofiling'] = {}

			elif (stage not in inputs['tprofiling']):
				inputs['tprofiling'][stage] = time.time()

			elif (stage in inputs['tprofiling']):
				inputs['tprofiling'][stage] = time.time() - inputs['tprofiling'][stage]

def imports(inputs):
	if (inputs['run_STEPS']):
		import steps
		import steps.utilities.meshio as smeshio
		import steps.model as smodel
		import steps.geom as stetmesh
		import steps.rng as srng


def all_initials(inputs):
	inputs['tprofiling_enabled'] = inputs['sim_tprofiling']
	inputs['reporting_enabled'] = inputs['sim_reporting']
	set_time(inputs)
	set_sim_style(inputs)
	set_vis_log(inputs)


def update_all(inputs):
	tsupdate(inputs)
	gaps(inputs)

def logging(inputs):
	log_path = os.getcwd()+'/Packages/Projects/'+inputs['project_name']+'/Logs/'
	for log_fname, log_flist in inputs['log'].iteritems():
		log_fpath = log_path+str(log_fname)
		for logf in log_flist:
			logf(inputs,log_fpath)
	

def loop(inputs):
	# run loop
	begint = time.time()
	tprofiling(inputs,'loop')

	for j in xrange(1,inputs['ntpnts']):
		inputs['tind'] = j

		if inputs['run_STEPS']:
			tprofiling(inputs,'STEPS')
			inputs['sim'].run(inputs['tpnts'][j])
			tprofiling(inputs,'STEPS')

		tprofiling(inputs,'fadvance')
		inputs['h']("{fadvance()}")
		tprofiling(inputs,'fadvance')

		for f in inputs['sim_in_loop']:
			f(inputs)
		
		vis_log(inputs)
		update_all(inputs)
	
	tprofiling(inputs,'loop')
	endt = time.time()
	inputs['tot_run_time'] = (endt-begint)
	inputs['realtime_factor'] = (inputs['tot_run_time']/inputs['INT'])