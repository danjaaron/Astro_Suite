# import system
import os, sys

# import STEPS
import steps
import steps.utilities.meshio as smeshio
import steps.model as smodel
import steps.geom as stetmesh
import steps.rng as srng


def run_meshing(inputs):
	
	# assign from inputs
	h = inputs['h']
	species = inputs['species']
	diffusion = inputs['diffusion']
	reactions = inputs['reactions'] # rlist = [lhs, rhs, kcst]
	cl = inputs['cl']

	# create STEPS model objects
	mdl = smodel.Model() 
	vsys = smodel.Volsys('cytosolv', mdl)

	# assign STEPS reactions and diffusions
	for s in species:
		exec ('{0} = smodel.Spec("{0}", mdl)'.format(s))
	for d, dcst in diffusion.iteritems():
		exec ('diff_{0} = smodel.Diff("diff_{0}",vsys,{0})'.format(d))
		exec ('diff_{0}.setDcst({1})'.format(d,dcst))
	for r, rlist in reactions.iteritems():
		exec ('{0} = smodel.Reac("{0}",vsys,lhs=[{1}],rhs=[{2}],kcst={3})'.format(r,rlist[0],rlist[1],rlist[2]))

	# paths
	suite_path = os.getcwd()
	mesh_path = (suite_path+'/Packages/Projects/'+inputs['project_name']+'/Meshes/'+inputs['mesh_file']+'_'+str(inputs['cl']))

	# ----------- #
	# check / generate STEPS meshes	
	if (((os.path.isfile(mesh_path+'.txt'))or(os.path.isfile(mesh_path+'.xml')))and(inputs['mesh_style']!='overwrite')):
			# load existing files
			inputs['mesh'] = smeshio.loadMesh(mesh_path)[0]
	elif ((not((os.path.isfile(mesh_path+'.txt'))and(os.path.isfile(mesh_path+'.xml'))))or(inputs['mesh_style']=='overwrite')):
		if (inputs['mesh_style'] != 'no_build'):
			# import Meshpy if mesh_style allows building
			from meshpy.tet import MeshInfo, build
		elif (inputs['mesh_style'] == 'no_build'):
			# quit if mesh_style doesn't allow building, given that no files were detected
			print "FATAL ERROR ({0}): STEPS mesh files not detected and mesh_style == 'no_build', so must quit.".format(os.path.basename(os.path.abspath(__file__)))
			sys.exit()
		# remove files if necessary
		if (inputs['mesh_style']=='overwrite'):
			if os.path.isfile(mesh_path+'.txt'):
				os.remove(mesh_path+'.txt')
			if os.path.isfile(mesh_path+'.xml'):
				os.remove(mesh_path+'.xml')
		# create new mesh from scratch
		allp = [[],[],[]]
		for s in h.allsec():
			for j in range(int(h.n3d())):
				allp[0].append(h.x3d(j))
				allp[1].append(h.y3d(j))
				allp[2].append(h.z3d(j))
		maxl = [int(max(allp[0]))+1,int(max(allp[1]))+1,int(max(allp[2]))+1]
		minl = [int(min(allp[0]))-1,int(min(allp[1]))-1,int(min(allp[2]))-1]
		bdim = [int(maxl[0] - minl[0])+2, int(maxl[1] - minl[1])+2, int(maxl[2] - minl[2])+2]
		bmin = list(minl)
		box_w = bdim[0]
		box_l = bdim[1]
		box_h = bdim[2]
		min_x = bmin[0]
		min_y = bmin[1]
		min_z = bmin[2]
		while (box_w%cl != 0):
			box_w += 1
		while (box_l%cl != 0):
			box_l += 1
		while (box_h%cl != 0):
			box_h += 1
		wpoints = int(1+(box_w)/cl)
		lpoints = int(1+(box_l)/cl)
		hpoints = int(1+(box_h)/cl)
		cpoints = []
		hfacets = []
		vfacets = []
		for hp in xrange(hpoints):
			for lp in xrange(lpoints):
				for wp in xrange(wpoints):
					cpoints.append((min_x+wp*cl,min_y+lp*cl,min_z+hp*cl))
					pindex = (hp*lpoints*wpoints)+(lp*wpoints)+wp
					# horizontal facets
					if (wp < int(wpoints)-1 and lp < int(lpoints)-1):
						hfacets.append([int(pindex), int(pindex+1), int(pindex+1+wpoints), int(pindex+wpoints)])
					# vertical facets
					if (hp > 0):
						if (wp > 0):
							vfacets.append([int(pindex),int(pindex-1),int(pindex-1-lpoints*wpoints),int(pindex-lpoints*wpoints)])
						if (lp > 0):
							vfacets.append([int(pindex),int(pindex-wpoints),int(pindex-wpoints-lpoints*wpoints),int(pindex-lpoints*wpoints)])
		all_facets = hfacets+vfacets
		# pass mesh to steps
		mesh_info = MeshInfo()
		mesh_info.set_points(cpoints)
		mesh_info.set_facets(all_facets)
		m = build(mesh_info)
		# write mesh proxies
		nodeproxy = smeshio.ElementProxy('node',3)
		for i, p in enumerate(m.points):
		    nodeproxy.insert(i,p)
		tetproxy = smeshio.ElementProxy('tet',4)
		newtet = [0,0,0,0]
		for i, t in enumerate(m.elements):
		    newtet[0] = nodeproxy.getSTEPSID(t[0])
		    newtet[1] = nodeproxy.getSTEPSID(t[1])
		    newtet[2] = nodeproxy.getSTEPSID(t[2])
		    newtet[3] = nodeproxy.getSTEPSID(t[3])
		    tetproxy.insert(i, newtet)
		# build mesh from proxies and save in STEPS format (xml & ASCII)
		nodedata = nodeproxy.getAllData()
		tetdata = tetproxy.getAllData()
		newmesh = steps.geom.Tetmesh(nodedata, tetdata)
		smeshio.saveMesh(mesh_path,newmesh)
		# load new STEPS files and assign mesh to inputs
		inputs['mesh'] = smeshio.loadMesh(mesh_path)[0]
	# ----------- #

	# associate tets and sections
	mesh = inputs['mesh']
	tet_hoc = {}
	hoc_tetcount = {}
	for s in h.allsec():
		hoc_tetcount[s] = 0
		for j in range(int(h.n3d())):
			containing_tet = mesh.findTetByPoint((h.x3d(j),h.y3d(j),h.z3d(j)))
			if (containing_tet) not in tet_hoc.keys():
				tet_hoc[containing_tet] = [s]
				hoc_tetcount[s] += 1
			elif (containing_tet) in tet_hoc.keys():
				if (s) not in tet_hoc[containing_tet]:
					tet_hoc[containing_tet].append(s)
					hoc_tetcount[s] += 1
	'''
	for tet in tet_hoc.keys():
		if (tet == -1):
			del tet_hoc[tet]
	'''
	# create a STEPS compartment for all tetrahedra
	ntets = mesh.countTets()
	comp = stetmesh.TmComp('cyto', mesh, range(ntets))
	comp.addVolsys('cytosolv')
	
	# assign to inputs
	inputs['tet_hoc'] = tet_hoc
	inputs['hoc_tetcount'] = hoc_tetcount
	inputs['comp'] = comp
	inputs['ntets'] = ntets
	inputs['model'] = mdl
	inputs['vsys'] = vsys
	inputs['rng'] = srng.create('mt19937', 512) 
	inputs['rng'].initialize(2903)
	
	return True
