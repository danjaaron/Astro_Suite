#--- pre-reporting / help ---#

def show_settings(inputs,stage):
	if ( type(stage) == list ):
		if (stage[0] == 'all'):
			print '\n{:=^30}'.format(' show_settings() ')
			print '{:=^30}'.format( 'showing all available settings' )
			for k, vl in inputs['show_settings_dict'].iteritems():
				print '{:<30}'.format( '>> {0}'.format(k) )
				print '{:<30}'.format( str(vl) )
			print '{:=^30}\n'.format('')
		else:
			print '\n{:=^30}'.format(' show_settings() ')
			print '{:<30}'.format( '>> {0}'.format( stage[0] ) )
			print '{:<30}'.format( str(inputs['show_settings_dict'][stage[0]]) )
			print '{:=^30}\n'.format('')
	elif not (stage in inputs['show_settings_dict']):
		inputs['show_settings_dict'][stage] = inputs.keys()
	elif (stage in inputs['show_settings_dict']):
		inputs['show_settings_dict'][stage] = [ setting for setting in inputs.keys() if setting not in inputs['show_settings_dict'][stage] ]

#--- NEURON ---#
def set_initial_values(inputs):
	show_settings(inputs,'initials')
	initial_values = {

		# rules of thumb from MacDonald 2013 --
		#		cmin = 2*(cai steady state)
		#		krel = half maximal cai during transient

		# states
		('cinit') : [0.01],
		('ipinit') : [0.001],
		('ip30') : [0.001],
		('ca_ERinit') : [400.0],
		('hinit') : [0.99],

		# stimulation
		('gluinit') : [0.00],
		('eATPinit') : [0.00],
		('ip30') : [0.00],

		# parameters
		('krel') : [0.08],
		('cmin') : [0.02],
		('jatpmax') : [1.00],
		('sdev') : [0.02],
		('kler') : [6.0e-4],
		('klext') : [1.0e-4],

	}
	inputs['initial_values'] = initial_values
	show_settings(inputs,'initials')

#--- simulation ---#

def set_inputs():
	import numpy, math
	inputs = {
		# files
		'project_name':'MacDonald13',
		'mod_suffix':'_mcd',
		'NEURON_list':['single_morph.hoc','mcd13.mod','Astrocyte4.Smt.SptGraph.asc'],
		'morph_file':'Astrocyte4.Smt.SptGraph.asc',
		'hoc_template':'template.hoc',

		# mesh
		'mesh_meta':'auto',
		'mesh_meta_style':'layers',
		'mesh_file':'coarse',
		'mesh_style':'overwrite',
		'cl':50,

		# network (mesh meta)
		'net_rowlen': 1,
		'net_cells':1,
		'net_layers': 1,
		'net_cell_shift': 75,

		# sim
		'sim_meta':'auto',
		'sim_meta_style':'none',
		'sim_file':'standard',
		'sim_style':'serial',

		# run control
		'tstop':300.00,
		'dt':0.25,

		# verbosity
		'verbose':True,
		'sim_meta_verbose':True,

		# lscale
		'lscale':1e-22,
		'lscale_range':[ math.pow(10,x) for x in numpy.arange(-15,-35,-1) ],
		'check_lscale':True,

		# project-specific (misc.)
		'sd':0.02,
		'read_var_expround':2, # number of digits accuracy in rounding read variables (summed over all sections)

		# logging files to access
		'log_list':[],

		# dictionary to store input settings for user access
		'show_settings_dict':{}
	}
	show_settings({'show_settings_dict':{}},'inputs')
	show_settings(inputs,'inputs')
	return inputs


#--- logging ---#

def set_logging(inputs):
	show_settings(inputs,'log')
	# log_function(inputs,log_fpath)
	inputs['log'] = {
		# 'log_file.txt':[log_functions]
	}
	show_settings(inputs,'log')


#--- read/write vars ---#

def set_tet_sec(inputs):
	show_settings(inputs,'NEURON-STEPS')
	import os, numpy

	# write 
	def write_rand(cinputs,tet,s):
		setattr(s(0.5),'rand'+cinputs['mod_suffix'],numpy.random.uniform(0.00,cinputs['sd']))

	def write_eATP(cinputs,tet,s):
		setattr(s(0.5),'eATP'+cinputs['mod_suffix'],cinputs['ATP_count'][tet]*1e6)

	# read

	def set_j_ATP(cinputs,tet):
		if not ('ATP_count' in cinputs):
			cinputs['ATP_count'] = {}
		if not ('j_ATP_count' in cinputs):
			cinputs['j_ATP_count'] = {}
		cinputs['ATP_count'][tet] = inputs['sim'].getTetConc(tet,'ATP')
		cinputs['j_ATP_count'][tet] = 0.00

	def count_j_ATP(cinputs,tet,s):
		cinputs['j_ATP_count'][tet] += (cinputs['lscale'])*(1e-6)*getattr(s(0.5),'j_ATP'+cinputs['mod_suffix'])*(1.0/(cinputs['hoc_tetcount'][s]))

	def finalize_j_ATP(cinputs,tet):
		newtetc = float(("{:."+str(cinputs['read_var_expround'])+"e}").format(cinputs['ATP_count'][tet]+cinputs['j_ATP_count'][tet]))
		inputs['sim'].setTetConc(tet,'ATP',newtetc)
		# check lscale roundoff 
		if (cinputs['check_lscale']):
			assert( (cinputs['ATP_count'][tet] == 0) == (newtetc == 0) ), \
				"({0}) lscale roundoff to zero in tsupdate() while reading j_ATP.".format(os.path.basename(os.path.abspath(__file__)))

	# assign to inputs

	inputs['write_vars'] = [
		write_rand,
		write_eATP,
	]

	inputs['read_vars'] = [
		[set_j_ATP,count_j_ATP,finalize_j_ATP],
	]

	show_settings(inputs,'NEURON-STEPS')


#--- STEPS ---#

def set_STEPS(inputs):
	show_settings(inputs,'STEPS')

	inputs['run_STEPS'] = True

	inputs['species'] = [
		'ATP',
	]

	inputs['diffusion'] = {
		# 'species':(diffusion coefficient [um^2/s])
		'ATP':(150.0),
	}

	inputs['reactions'] = {
		# 'reaction_name': [lhs,rhs,kcst]
		'ATP_degrade': ['ATP','ATP',0.65], 
	}

	show_settings(inputs,'STEPS')

#--- reporting ---#

def set_reporting(inputs):
	show_settings(inputs,'report')
	import collections
	inputs['record_variables'] = [ 
		'cai',
		'IP3i',
		('ca_ER'+inputs['mod_suffix']),
		('h'+inputs['mod_suffix']),
		('eATP'+inputs['mod_suffix']),
		('j_ATP'+inputs['mod_suffix']),
	]

	inputs['sim_report_block'] = collections.OrderedDict({})
	inputs['sim_report_block']['> STEPS: {0} '] = ['run_STEPS','{:<30}']
	inputs['sim_report_block'][' tstop: {0} dt: {1} '] = ['tstop','dt','{:^30}']
	inputs['sim_report_block'][' INT: {0} DT: {1} '] = ['INT','DT','{:^30}']
	inputs['sim_report_block'][' number of cells: {0} '] = ['net_cells','{:^30}']
	inputs['sim_report_block']['> run time: {0:.2f} s '] = ['tot_run_time','{:<30}']
	inputs['sim_report_block']['> factor: {0:.2f}x realtime '] = ['realtime_factor','{:<30}']

	inputs['sim_reporting'] = True
	inputs['report_stages'] = ['all']

	inputs['sim_tprofiling'] = True
	inputs['tprofiling_stages'] = ['all'] #['loop','fadvance','update_tsupdate','update_gaps']
	inputs['tprofiling_final'] = 'percentage'
	inputs['tprofiling'] = {}
	show_settings(inputs,'report')

#--- stimulation ---#

def set_stim(inputs):
	show_settings(inputs,'stim')
	inputs['stim_sects'] = {}
	inputs['stim_tets'] = {}

	inputs['enable_stim_sects'] = False
	inputs['enable_stim_tets'] = False
	show_settings(inputs,'stim')


#--- visualization ---#

def set_vis(inputs):
	show_settings(inputs,'vis')
	# vis logging variables
	inputs['vis_log_sects'] = {
		('cai'):['all_sects'],
	}

	inputs['vis_log_tets'] = {
		('ATP'):['all_tets'],
	}

	# frames
	inputs['skip_frame'] = 30.0
	inputs['delay_frame'] = 1000.0 # (ms)
	inputs['delay_initial'] = 10000.0 # (ms)
	inputs['rotate'] = True
	inputs['rotate_angle'] = inputs['skip_frame']

	# plot bools
	inputs['vis_tets'] = True
	inputs['vis_sects'] = True

	# edge colors
	inputs['tet_edge'] = 'black'
	inputs['sect_edge'] = 'black'

	# edge markers
	inputs['tet_mark'] = '^'
	inputs['sect_mark'] = 'o'
	inputs['gap_mark'] = 's'

	# face colors (red, blue or green)
	inputs['tet_fcolor'] = 'red'
	inputs['sect_fcolor'] = 'red'

	# face color style
	inputs['tet_fcolor_style'] = 'boolean'
	inputs['sect_fcolor_style'] = 'gradient'

	# alpha values
	inputs['tet_alpha'] = 0.75
	inputs['sect_alpha'] = 1.0

	# text
	inputs['xlabel'] = 'x'
	inputs['ylabel'] = 'y'
	inputs['zlabel'] = 'z'
	inputs['vis_title'] = 'Test Title'
	show_settings(inputs,'vis')


#--- gap junctions ---#

def set_gaps(inputs):
	show_settings(inputs,'gaps')
	inputs['gaps'] = {}
	inputs['gap_species'] = {
		# external_variable : internal_variable
		('gap_cai'+inputs['mod_suffix']):'cai',
		('gap_IP3i'+inputs['mod_suffix']):'IP3i',
	}
	show_settings(inputs,'gaps')

#--- assign all to inputs ---#

def set_loop(inputs):
	show_settings(inputs,'loop')
	# inputs['sim_in_loop'] = [ loop_functions(inputs) ]
	inputs['sim_in_loop'] = []
	show_settings(inputs,'loop')

def set_misc(inputs):
	show_settings(inputs,'misc')
	import os 
	inputs['lscale_path'] = (os.path.isfile(os.getcwd()+"/Packages/Projects/"+inputs['project_name']+"/Logs/lscale.txt"))
	inputs['original'] = dict(inputs)
	show_settings(inputs,'misc')
	

#--- check inputs consistency ---#

def check_inputs(inputs):
	# sim and meta must be distinct
	assert (inputs['sim_meta'] != inputs['sim_file']), \
		"sim_meta == sim_file \n--> inputs['sim_meta'] = '{0}', inputs['sim_file'] = '{1}'".format(inputs['sim_meta'],inputs['sim_file'])

#--- run entire template ---#

def set_all():
	# configure system
	import sys
	sys.dont_write_bytecode = True
	# configure inputs
	inputs = set_inputs()
	set_initial_values(inputs)
	set_logging(inputs)
	set_STEPS(inputs)
	set_tet_sec(inputs)
	set_reporting(inputs)
	set_stim(inputs)
	set_vis(inputs)
	set_gaps(inputs)
	set_loop(inputs)
	set_misc(inputs)
	inputs['show_settings'] = show_settings
	check_inputs(inputs)
	return inputs


