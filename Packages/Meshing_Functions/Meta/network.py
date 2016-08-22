# import system
import itertools, os, sys

def layers(inputs):
	# assign from inputs
	rows = inputs['net_rowlen']
	layers = inputs['net_layers']
	shift = inputs['net_cell_shift']
	#num_cells = (rows*rows*layers)
	if (inputs['net_cells'] == 'auto'):
		num_cells = (rows*rows*layers)
		inputs['net_cells'] = num_cells
	else:
		num_cells = int(inputs['net_cells'])
		assert (num_cells <= (rows*rows*layers)), \
			"Number of cells exceeds grid dimensions."
	# create cells
	cwd = os.getcwd()
	os.chdir(cwd+'/Packages/Current_Project/')
	from neuron import h, gui
	inputs['h'] = h
	h.load_file(inputs['hoc_template'])
	h('num_cells = '+str(num_cells))
	h('strdef morph_string')
	h('morph_string = "'+inputs['morph_file']+'"')
	h('''
	objref cell[num_cells]
	for i=0,num_cells-1 {
		cell[i] = mkcell(morph_string)
	}
	''')
	h("forall {insert "+inputs['mod_suffix'][1:]+"}")
	# assemble cells into network
	r = 0
	c = 0
	l = 0
	for ncell in xrange(num_cells):
		if (r >= rows):
			r = 0
			c += 1
		if (c >= rows):
			r = 0
			c = 0
			l += 1
		for s in h.Cell[ncell].all:
			for n in xrange(int(h.n3d())):
				h.pt3dchange(n, h.x3d(n)+(r*shift), h.y3d(n)+(c*shift), h.z3d(n)+(l*shift), h.diam3d(n))
		r += 1
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
	# update inputs
	inputs['gaps'] = dict(collisions)
	os.chdir(cwd)
	# run network through meshing style
	exec ("from Packages.Meshing_Functions.{0} import run_meshing as mesh".format(inputs['mesh_file']))
	mesh(inputs)
	return True 

def randnet2D(inputs):
	# assign from inputs
	rowlength = inputs['net_gridlen']
	shift = inputs['net_cell_shift']
	num_cells = inputs['net_cells']

	assert(num_cells <= rowlength*rowlength), \
		'More cells to create than spaces in grid.'

	# create cells
	cwd = os.getcwd()
	os.chdir(cwd+'/Packages/Current_Project/')

	from neuron import h, gui
	import sys, numpy, math

	h('objref soma[{0}]'.format(num_cells))
	sl = []
	shift = inputs['net_cell_shift']
	inputs['h'] = h

	# create artificial (py only) network
	for s in xrange(num_cells):
		sect = h.Section(name='soma[{0}]'.format(s))
		sect.insert(inputs['mod_suffix'][1:])
		sl.append(sect)
		h.pop_section()

	# randomize cells in 2D grid
	cell_grid = {}
	for cell in sl:
		p = ( numpy.random.randint(0,rowlength+1), numpy.random.randint(0,rowlength+1) )
		while p in cell_grid.keys():
			p = ( numpy.random.randint(0,rowlength+1), numpy.random.randint(0,rowlength+1) )
		cell_grid[p] = cell

	# detect gap junctions by adjacency
	gaps = {}
	for p in cell_grid:
		gaps[cell_grid[p]] = []
	for p in cell_grid:
		for p2 in cell_grid:
			if (p != p2):
				dist = math.sqrt( math.pow((p2[1]-p[1]),2) + math.pow((p2[0]-p[0]),2) )
				if (dist == 1.0):
					pcell = cell_grid[p]
					p2cell = cell_grid[p2]
					if (p2cell not in gaps[pcell]):
						gaps[pcell].append(p2cell)
					if (pcell not in gaps[p2cell]):
						gaps[p2cell].append(pcell)

	# update inputs
	inputs['gaps'] = dict(gaps)
	inputs['sim_style'] = None
	inputs['run_STEPS'] = False
	os.chdir(cwd)
	return True 

def run_meshing(inputs):
	exec (inputs['mesh_meta_style']+"(inputs)")
	#if (inputs['mesh_meta_style']) == 'layers':
	#	layers(inputs)


