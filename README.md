## How to Run
To start the suite, execute ```python run.py```.

The suite immediately reads from the ```project.py``` file.
In this file there must be a ```template``` variable and a 
```project_inputs``` function.

The ```template``` variable references a file in the Templates
folder. Inside this file are functions which create and populate
a dictionary called ```inputs```. This dictionary specifies which
files the suite should execute, as well as a variety of other specifications
relating to those files. 

The dictionary from the template file only serves as a basis for the user's 
current project. It represents a set of standard values which are more or less
what's needed for a general class of projects. Although most of the specifications from a chosen template should be accurate for the current project, 
some will need to be tailored.

This is done with the ```project_inputs``` function,
in which the user can modify the ```inputs``` dictionary before it's passed to the
rest of the suite. If the user finds themselves making extensive modifications in the
```project_inputs``` function, they should consider making a new template instead. 

Here's an example of a ```project.py``` file:
```
template = 'default'
def project_inputs(inputs):
	# customize project from template
	inputs['mesh_meta'] = 'network'
	inputs['mesh_meta_style'] = 'layers'
	inputs['net_cells'] = 'auto'
	inputs['net_rowlen'] = 1
	inputs['net_layers'] = 1
	inputs['mesh_style'] = 'overwrite' 
	inputs['project_name'] = 'github_project'
```

When the suite is run, a new project directories is created at
``` ~/Astro_Suite/Packages/Projects/project_name ```.

Inside this project directory all of the NEURON files (.hoc, .mod, .asc) which the project is specified
to use are copied, a copy of the ```project.py``` file is made under the ```Logs``` subdirectory, and the
STEPS mesh files created by the meshing functions specified in ```inputs``` are stored under the ```Meshes```
subdirectory. The project directory exists to preserve the files, settings and results of its project. 

All of the project's relevant files are also copied to the ```Current_Project``` folder, where its 
NEURON files are compiled and from which the suite runs the actual simulation. Whereas a project's 
named directory persists until overwritten by another project of the same name, the ```Current_Project```
folder is overwritten every time the suite is run. 

Two types of command line arguments are also available when running the suite:
```python run.py -help``` and ```python run.py -show ____```, where '____' stands for the name of a 
template function.

The ```-help``` command lists all currently available command line arguments, and the
```-show ____``` command lists available settings for the specified function. 

## Creating a Project

In order to understand and use the suite's features, it's useful to understand the
suite's file architecture:
```
.
+-- project.py   
+-- run.py
+-- _Templates 
|	+-- default.py
|	+-- create_project.py  
+-- _Packages
|	+-- _Projects
|	+-- _Current_Project
|	+-- _Documentation
|	+-- _Generate
|		+-- generate_architecture.py
|	+-- _Meshing_Functions
|		+-- coarse.py
|		+-- _Meta
|			+-- auto.py
|			+-- network.py
|	+-- _Sim_Functions
|		+-- standard.py
|		+-- _Meta
|			+-- auto.py
|			+-- lscale_finder.py
|			+-- steadystate.py
|			+-- vis.py
|		+-- _Sim_Tools
|			+-- standard_tools.py
|	+-- _NEURON
```
When the suite is run, it chooses a meshing function to create the STEPS mesh and to configure the NEURON network
for a project, and a sim function to run the simulation which produces the project's output. To specify 
which functions to use, ```inputs``` has ```sim_file``` and ```mesh_file``` keys. For example,
```inputs['mesh_file'] == 'coarse'``` means that the meshing_function in ```~/Meshing_Functions/coarse.py```
will be used to create the mesh for the current project. Every ```sim_file``` must have a ```run_sim``` function,
and every ```mesh_file``` must have a ```run_meshing``` function in order for these functions to be called 
automatically by the suite. Additional settings can be passed to these files
by the ```sim_style``` and ```mesh_style``` keys in ```inputs```. 

The ```inputs``` dictionary also has options for ```sim_meta``` and ```mesh_meta```. These keys specify 
'meta' files which will execute their respective category of file. For example, the ```network.py``` mesh meta
file creates a network from the project's NEURON files before passing that network
to be meshed by ```mesh_file```, and the sim meta ```vis.py``` creates a visualization after running its simulation. 
Generally meta files exist to manipulate normal meshing or simulation in some pre-determined way, and they too can be passed 
additional settings via ```sim_meta_style``` and ```mesh_meta_style``` in ```inputs```. Note that meta meshing is executed before 
meta simulation. 

In case the user has no need for meta files, the ```auto.py``` meta file is available for both meshing and simulation.
This file simply executes the normal sim or mesh file and performs no additional meta computation. 

After the user has specified their desired sim and meshing files, metas and settings, they have two ways to further modify their project.

1. Static ```inputs``` settings
  * Each sim/meshing file may read or write different values to ```inputs```, but most rely on a common group of settings (e.g. ```NEURON_list```, which lists all NEURON-type files to be used for the project).

2. Functional ```inputs``` settings
	* Some inputs values are data objects containing functions which are executed at various points in the project's simulation or meshing (e.g. ```sim_in_loop```, which contains functions that are executed at every iteration of a simulation's run loop.)
