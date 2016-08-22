def run_meshing(inputs):

	# configure system
	import os, sys
	sys.dont_write_bytecode = True

	# load hoc files
	cwd = os.getcwd()
	os.chdir(cwd+'/Packages/Current_Project/')
	from neuron import h, gui
	inputs['h'] = h
	for fname in inputs['NEURON_list']:
		if ('.hoc' == fname[-4:]):
			h.load_file(fname)
	os.chdir(cwd)

	# detect gap junctions by box overlap
	xboxmax = {}
	xboxmin = {}
	yboxmax = {}
	yboxmin = {}
	zboxmax = {}
	zboxmin = {}
	for s in h.allsec():
		nmax = h.n3d()-1
		xboxmax[s] = max(h.x3d(0),h.x3d(nmax))
		xboxmin[s] = min(h.x3d(0),h.x3d(nmax))
		yboxmax[s] = max(h.y3d(0),h.y3d(nmax))
		yboxmin[s] = min(h.y3d(0),h.y3d(nmax))
		zboxmax[s] = max(h.z3d(0),h.z3d(nmax))
		zboxmin[s] = min(h.z3d(0),h.z3d(nmax))
	collisions = {}
	for s in h.allsec():
		collisions[s] = []
		for sp in h.allsec():
			if ( (s != sp) and ((xboxmin[s] < xboxmax[sp])and(xboxmax[s] > xboxmin[sp])) and ((yboxmin[s] < yboxmax[sp])and(yboxmax[s] > yboxmin[sp])) and ((zboxmin[s] < zboxmax[sp])and(zboxmax[s] > zboxmin[sp])) ):
				collisions[s].append(sp)
		if (not collisions[s]):
			del collisions[s]
	inputs['gaps'] = dict(collisions)

	# create mesh
	exec ('from Packages.Meshing_Functions.' + inputs['mesh_file'] + ' import run_meshing as mesh')
	mesh(inputs)
	