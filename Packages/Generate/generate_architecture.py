
# import system
import os, sys
import importlib
import shutil
import subprocess


# suite architecture

core_architecture = [
	'/Packages/',
	'/Packages/Documentation/',
	'/Packages/Current_Project/',
	'/Packages/Generate/',
	'/Packages/Sim_Functions/',
	'/Packages/Sim_Functions/Meta/',
	'/Packages/Sim_Functions/Sim_Tools/',
	'/Packages/Meshing_Functions/',
	'/Packages/Meshing_Functions/Meta/',
	'/Packages/Projects/',
	'/Packages/NEURON/'
]

def architect(inputs):
	# relevant paths
	cwd = os.getcwd()
	NEURON_path = cwd+'/Packages/NEURON/'

	# create core architecture directories
	for path in core_architecture:
		if (not os.path.isdir(cwd+path)):
			os.mkdir(cwd+path)
	
	# assign project information
	project_name = inputs['project_name']
	inputs['mesh_name'] = str(inputs['mesh_file'])+'_'+str(inputs['cl']) # naming convention
	mesh_name = inputs['mesh_name']
	NEURON_list = inputs['NEURON_list']

	# overwrite project-specific directories
	project_dir = cwd+'/Packages/Projects/'+project_name
	current_project_dir = cwd+'/Packages/Current_Project/'
	if (os.path.isdir(project_dir)):
		for p in os.listdir(project_dir):
			if ((inputs['mesh_style']=='no_build')and(p=='Meshes')):
				continue
			else:
				ppath = (project_dir+'/'+p)
				if os.path.isfile(ppath):
					os.remove(ppath)
	
	# determine imports for each subpackage
	import_by_package = {
		('/Packages/NEURON/'):inputs['NEURON_list'],
		('/Packages/Current_Project/'):[],

		('/Packages/Projects/'+inputs['project_name']+'/'):[],
		('/Packages/Projects/'+inputs['project_name']+'/Logs/'):inputs['log_list'],
		('/Packages/Projects/'+inputs['project_name']+'/Meshes/'):[str(inputs['mesh_file'])+'_'+str(inputs['cl'])+'.txt', str(inputs['mesh_file'])+'_'+str(inputs['cl'])+'.xml'],

		('/Packages/Meshing_Functions/'):[inputs['mesh_file'],'Meta'],
		('/Packages/Meshing_Functions/Meta/'):[inputs['mesh_meta']],

		('/Packages/Sim_Functions/') : [inputs['sim_file'],'Meta'],
		('/Packages/Sim_Functions/Meta/') : [inputs['sim_meta']],
		('/Packages/Sim_Functions/Sim_Tools/') :[],
	}

	# create subpackage directories and __init__.py files
	for path, all_list in import_by_package.iteritems():
		p = cwd+path
		if not os.path.isdir(p):
			os.makedirs(p)
		init_py = open(p+'__init__.py','w')
		if (type(all_list) == list):
			init_py.write('__all__ = {0}'.format(all_list))
		elif (all_list):
			init_py.write('__all__ = ["{0}"]'.format(str(all_list)))
		init_py.close()

	# copy NEURON files to project directories
	for n in NEURON_list:
		if (os.path.isfile(NEURON_path+n)):
			shutil.copy(NEURON_path+n,current_project_dir)
			shutil.copy(NEURON_path+n,project_dir)
		else:
			print "FATAL ERROR ({0}) -- specified NEURON file ({1}) not found in path {2}.".format(os.path.basename(os.path.abspath(__file__)),n,NEURON_path)
			sys.exit()
	if (inputs['hoc_template']):
		shutil.copy(NEURON_path+inputs['hoc_template'],current_project_dir)
		shutil.copy(NEURON_path+inputs['hoc_template'],project_dir)

	# copy project.py to project directory log folder
	shutil.copy(cwd+'/project.py',project_dir+'/Logs/')

	# copy inputs to project directory
	inputs_file = open((os.getcwd()+'/Packages/Projects/'+inputs['project_name']+'/Logs/inputs.txt'),'w')
	#inputs_file.write(str('inputs: \n {0}'.format(str(inputs['original']))))
	inputs_file.write('inputs: project ({0}) template ({1})\n'.format(inputs['project_name'],inputs['template']))
	for k, v in inputs.iteritems():
		inputs_file.write('{0}: {1}\n'.format(str(k),str(v)))
	inputs_file.close()

	# compile current project
	sbp = subprocess.Popen('nrnivmodl', cwd=current_project_dir, shell=True, stdout=open(os.devnull, 'wb'))
	sbp.wait()

	return True



