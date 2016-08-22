

#--- MOVIES ---#

def animate(inputs):
    exec ('from Packages.Sim_Functions.' + inputs['sim_file'] + ' import run_sim as simulate') in locals()
    import matplotlib
    matplotlib.use('TKAgg')
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import numpy as np
    from mpl_toolkits.mplot3d import Axes3D
    import sys, math

    h = inputs['h']
    fig = plt.figure()
    ax = fig.add_subplot(111,projection = '3d')

    # plot sections in space
    sects = [ [], [], [] ]
    sec_count = 0
    for s in h.allsec():
        sects[0].append(h.x3d(0))
        sects[1].append(h.y3d(0))
        sects[2].append(h.z3d(0))
        sec_count += 1

    # run sim and gather results
    simulate(inputs)
    cai_dict = inputs['cai_dict']
    print len(cai_dict.keys()), len(cai_dict[cai_dict.keys()[0]])
    all_cai = []
    for s in h.allsec():
        for v in cai_dict[s]:
            all_cai.append(v)

    print "MAX: ", max(all_cai), " MIN: ", min(all_cai)
    nframes = int(inputs['tstop']/(inputs['dt']))
    skip_frame = inputs['skip_frame']
    frame_list = [f*skip_frame for f in xrange(nframes) if (f*skip_frame < nframes)]

    def init():
        cai_list = []
        for s in h.allsec():
            cai_list.append(math.fabs(cai_dict[s][0])/max(all_cai))
        color_list = [str(1.0-j) for j in cai_list]
        global scat 
        scat = ax.scatter(sects[0],sects[1],sects[2], facecolors=color_list, animated=True)
        ax.set_xlim([min(sects[0]),max(sects[0])])
        ax.set_ylim([min(sects[1]),max(sects[1])])
        ax.set_zlim([min(sects[2]),max(sects[2])])
        return scat,

    def update(i):
        cai_list = []
        print "frame: ", i, " of ", nframes
        for s in h.allsec():
            cai_list.append(math.fabs(cai_dict[s][i])/max(all_cai))
        color_list = [str(1.0-j) for j in cai_list]
        scat.set_facecolor(color_list)
        return scat,

    
    ani = animation.FuncAnimation(fig, update, init_func=init, frames=frame_list, interval=10, blit=True)
    plt.show()

def loop3D(inputs):
	exec ('from Packages.Sim_Functions.' + inputs['sim_file'] + ' import run_sim as simulate') in locals()
	import matplotlib
	import matplotlib.pyplot as plt
	import matplotlib.animation as animation
	import numpy as np
	from mpl_toolkits.mplot3d import Axes3D
	import sys

	h = inputs['h']
	fig = plt.figure()
	ax = fig.add_subplot(111,projection = '3d')
	verbose = inputs['sim_meta_verbose']
	
	plot_sects = inputs['vis_sects']
	plot_tets = inputs['vis_tets']

	# plot tets in space
	if (plot_tets):
		tets = [ [], [], [] ]
		for tet in inputs['comp'].tets:
			p = inputs['mesh'].getTetBarycenter(tet)
			tets[0].append(p[0])
			tets[1].append(p[1])
			tets[2].append(p[2])

	# plot sects in space
	if (plot_sects):
		sects = [ [], [], [] ]
		for s in inputs['h'].allsec():
		    sects[0].append(h.x3d(0))
		    sects[1].append(h.y3d(0))
		    sects[2].append(h.z3d(0))

	# stimulation
	st_tets = inputs['enable_stim_tets']
	st_sects = inputs['enable_stim_sects']
	
	if (st_tets):
		# stimulate tets
		inputs['stim_tets'][tet] = ['ATP',1e-30]

	if (st_sects):
		# stimulate sects
		scount = 0
		smax = 400
		for s in h.allsec():
			if (scount == smax):
				break
			inputs['stim_sects'][s] = ['gluinit'+inputs['mod_suffix'],10.0]
			scount += 1

	# run sim and gather results
	simulate(inputs)

	# gather tets
	if (plot_tets):
		all_v = {}
		for v, vdict in inputs['vis_log_tets'].iteritems():
			all_v[v] = []
			for tet, vlist in vdict.iteritems():
				for val in vlist:
					all_v[v].append(val)
			all_v[v] = [max(all_v[v]),min(all_v[v])]
			if (verbose):
				print "Tets -- MAX: ", all_v[v][0], " MIN: ", all_v[v][1]

	# gather sects
	if (plot_sects):
		for v, vdict in inputs['vis_log_sects'].iteritems():
			all_v[v] = []
			for s, vlist in vdict.iteritems():
				for val in vlist:
					all_v[v].append(val)
			all_v[v] = [max(all_v[v]),min(all_v[v])]
			if (verbose):
				print "Sections -- MAX: ", all_v[v][0], " MIN: ", all_v[v][1]

	# set frame values
	nframes = int(inputs['tstop']/inputs['dt'])
	skip_frame = inputs['skip_frame']
	frame_list = [int(f*skip_frame) for f in xrange(nframes) if (f*skip_frame < nframes)]
	view_angle = 0

	

	# run visualization
	for frame in frame_list:
		# set text
		ax.set_xlabel(inputs['xlabel'])
		ax.set_ylabel(inputs['ylabel'])
		ax.set_zlabel(inputs['zlabel'])
		ax.set_title(inputs['vis_title'])
		if (verbose):
			print "frame {0} of {1}".format(frame,nframes)
		color_v = {}
		# color tets
		if (plot_tets):
			for v, vdict in inputs['vis_log_tets'].iteritems():
				color_v[v] = []
				for tet in inputs['comp'].tets:
					if inputs['tet_fcolor_style'] == 'boolean':
						if (vdict[tet][frame] > 0.0):
							if (inputs['tet_fcolor'] == 'red'):
								color = (1.0,0.0,0.0)
							elif (inputs['tet_fcolor'] == 'green'):
								color = (0.0,1.0,0.0)
							elif (inputs['tet_fcolor'] == 'blue'):
								color = (0.0,0.0,1.0)
						else:
							color = (1.0,1.0,1.0)
						color_v[v].append( color )
					elif inputs['tet_fcolor_style'] == 'gradient':
						try:
							tetval = 1.0 - (vdict[tet][frame]-all_v[v][1])/(all_v[v][0]-all_v[v][1])
							if (inputs['tet_fcolor'] == 'red'):
								color = (1.0,tetval,tetval)
							elif (inputs['tet_fcolor'] == 'green'):
								color = (tetval,1.0,tetval)
							elif (inputs['tet_fcolor'] == 'blue'):
								color = (tetval,tetval,1.0)
							color_v[v].append( color )
						except ZeroDivisionError:
							color_v[v].append( ( 1.0, 1.0, 1.0 ) )
				ax.scatter(tets[0],tets[1],tets[2],facecolors=color_v[v],edgecolors=inputs['tet_edge'],animated=False,alpha=inputs['tet_alpha'],marker=inputs['tet_mark'])
		# color sects 
		if (plot_sects):
			for v, vdict in inputs['vis_log_sects'].iteritems():
				color_v[v] = []
				for s in h.allsec():
					if inputs['sect_fcolor_style'] == 'boolean':
						if (vdict[s][frame] > 0.0):
							if (inputs['sect_fcolor'] == 'red'):
								color = (1.0,0.0,0.0)
							elif (inputs['sect_fcolor'] == 'green'):
								color = (0.0,1.0,0.0)
							elif (inputs['sect_fcolor'] == 'blue'):
								color = (0.0,0.0,1.0)
						else:
							color = (1.0,1.0,1.0)
					elif inputs['sect_fcolor_style'] == 'gradient':
						try:
							sectval = 1.0 - (vdict[s][frame]-all_v[v][1])/(all_v[v][0]-all_v[v][1])
							if (inputs['sect_fcolor'] == 'red'):
								color = (1.0,sectval,sectval)
							elif (inputs['sect_fcolor'] == 'green'):
								color = (sectval,1.0,sectval)
							elif (inputs['sect_fcolor'] == 'blue'):
								color = (sectval,sectval,1.0)
							color_v[v].append( color )
						except ZeroDivisionError:
							color_v[v].append( ( 1.0, 1.0, 1.0 ) )
				ax.scatter(sects[0],sects[1],sects[2],facecolors=color_v[v],edgecolors=inputs['sect_edge'],animated=False,alpha=inputs['sect_alpha'],marker=inputs['sect_mark'])
		# rotate
		if (inputs['rotate']):
			view_angle += inputs['rotate_angle']
			ax.view_init(elev=10., azim=(view_angle%360))
		plt.draw()
		if (frame == 0):
			plt.pause(inputs['delay_initial']*1e-3)
		else:
			plt.pause((inputs['delay_frame']*1e-3))
		plt.cla()

	return True


def loop2D(inputs):
	exec ('from Packages.Sim_Functions.' + inputs['sim_file'] + ' import run_sim as simulate') in locals()
	import matplotlib
	import matplotlib.pyplot as plt
	import numpy as np
	import sys

	h = inputs['h']
	fig = plt.figure()
	ax = fig.add_subplot(111)
	verbose = inputs['sim_meta_verbose']
	plot_sects = inputs['vis_sects']

	# plot sects in space
	if (plot_sects):
		sects = [ [], [] ]
		gaps = [ [], [] ]
		for s in inputs['h'].allsec():
			if (s in inputs['gaps']):
				gaps[0].append(h.x3d(0))
				gaps[1].append(h.y3d(0))
			else:
				sects[0].append(h.x3d(0))
				sects[1].append(h.y3d(0))

	#minstance = matplotlib.markers.MarkerStyle(marker=all_markers)
	
	# stimulation
	st_sects = inputs['enable_stim_sects']

	if (st_sects):
		# stimulate sects
		scount = 0
		smax = 400
		for s in h.allsec():
			if (scount == smax):
				break
			inputs['stim_sects'][s] = ['gluinit'+inputs['mod_suffix'],10.0]
			scount += 1

	# run sim and gather results
	simulate(inputs)

	# gather sects
	if (plot_sects):
		all_v = {}
		for v, vdict in inputs['vis_log_sects'].iteritems():
			all_v[v] = []
			for s, vlist in vdict.iteritems():
				for val in vlist:
					all_v[v].append(val)
			all_v[v] = [max(all_v[v]),min(all_v[v])]
			if (verbose):
				print "Sections -- MAX: ", all_v[v][0], " MIN: ", all_v[v][1]

	# set frame values
	nframes = int(inputs['tstop']/inputs['dt'])
	skip_frame = inputs['skip_frame']
	frame_list = [int(f*skip_frame) for f in xrange(nframes) if (f*skip_frame < nframes)]

	# plot initial sects
	if gaps[0]:
		ax.set_xlim(min(min(sects[0]),min(gaps[0]))-5.0,max(max(sects[0]),max(gaps[0]))+5.0)
	else:
		ax.set_xlim(min(sects[0])-5.0,max(sects[0])+5.0)
	if gaps[1]:
		ax.set_ylim(min(min(sects[1]),min(gaps[1]))-5.0,max(max(sects[1]),max(gaps[1]))+5.0)
	else:
		ax.set_ylim(min(sects[1])-5.0,max(sects[1])+5.0)
	ax.scatter(sects[0],sects[1],facecolors='white',edgecolors=inputs['sect_edge'],animated=False,alpha=inputs['sect_alpha'],marker=inputs['sect_mark'])
	ax.scatter(gaps[0],gaps[1],facecolors='white',edgecolors=inputs['sect_edge'],animated=False,alpha=inputs['sect_alpha'],marker=inputs['gap_mark'])
	plt.draw()
	plt.pause(2.5)

	# run visualization
	for frame in frame_list:
		# set text
		ax.set_xlabel(inputs['xlabel'])
		ax.set_ylabel(inputs['ylabel'])
		if gaps[0]:
			ax.set_xlim(min(min(sects[0]),min(gaps[0]))-5.0,max(max(sects[0]),max(gaps[0]))+5.0)
		else:
			ax.set_xlim(min(sects[0])-5.0,max(sects[0])+5.0)
		if gaps[1]:
			ax.set_ylim(min(min(sects[1]),min(gaps[1]))-5.0,max(max(sects[1]),max(gaps[1]))+5.0)
		else:
			ax.set_ylim(min(sects[1])-5.0,max(sects[1])+5.0)
		ax.set_title(inputs['vis_title'])
		if (verbose):
			print "frame {0} of {1}".format(frame,nframes)
		color_sects = {}
		color_gaps = {}
		# color sects 
		if (plot_sects):
			for v, vdict in inputs['vis_log_sects'].iteritems():
				color_sects[v] = []
				color_gaps[v] = []
				for s in h.allsec():
					if inputs['sect_fcolor_style'] == 'boolean':
						if (vdict[s][frame] > 0.0):
							if (inputs['sect_fcolor'] == 'red'):
								color = (1.0,0.0,0.0)
							elif (inputs['sect_fcolor'] == 'green'):
								color = (0.0,1.0,0.0)
							elif (inputs['sect_fcolor'] == 'blue'):
								color = (0.0,0.0,1.0)
						else:
							color = (1.0,1.0,1.0)
						if (s in inputs['gaps']):
							color_gaps[v].append( color )
						else:
							color_sects[v].append( color )
					elif inputs['sect_fcolor_style'] == 'gradient':
						try:
							sectval = 1.0 - (vdict[s][frame]-all_v[v][1])/(all_v[v][0]-all_v[v][1])
							if (inputs['sect_fcolor'] == 'red'):
								color = (1.0,sectval,sectval)
							elif (inputs['sect_fcolor'] == 'green'):
								color = (sectval,1.0,sectval)
							elif (inputs['sect_fcolor'] == 'blue'):
								color = (sectval,sectval,1.0)
							if (s in inputs['gaps']):
								color_gaps[v].append( color )
							else:
								color_sects[v].append( color )
						except ZeroDivisionError:
							if (s in inputs['gaps']):
								color_gaps[v].append( color )
							else:
								color_sects[v].append( color )
				ax.scatter(sects[0],sects[1],facecolors=color_sects[v],edgecolors=inputs['sect_edge'],animated=False,alpha=inputs['sect_alpha'],marker=inputs['sect_mark'])
				ax.scatter(gaps[0],gaps[1],facecolors=color_gaps[v],edgecolors=inputs['sect_edge'],animated=False,alpha=inputs['sect_alpha'],marker=inputs['gap_mark'])
		plt.draw()
		if (frame == 0):
			plt.pause(inputs['delay_initial']*1e-3)
		else:
			plt.pause((inputs['delay_frame']*1e-3))
		plt.cla()

	return True

#--- STILL PLOTS ---#

def still_sections(inputs):
	import numpy as np
	from mpl_toolkits.mplot3d import Axes3D
	import matplotlib.pyplot as plt

	h = inputs['h']
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	alpha = 0.2
	gapcolor = 'green'
	sectcolor = 'blue'

	# plot sections and gap junctions
	for s in h.allsec():
		if (s in inputs['gaps']):
			color = gapcolor
		else:
			color = sectcolor
		ax.scatter(h.x3d(0),h.y3d(0),h.z3d(0),c=color,marker='o',alpha=0.2)

	ax.set_xlabel('X Label')
	ax.set_ylabel('Y Label')
	ax.set_zlabel('Z Label')

	plt.show()

def still_tets(inputs):
	import numpy as np
	from mpl_toolkits.mplot3d import Axes3D
	import matplotlib.pyplot as plt
	import sys

	h = inputs['h']
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	alpha = 0.3
	color = 'orange'

	# plot tets
	for tet in inputs['comp'].tets:
		# barycenters
		b = inputs['mesh'].getTetBarycenter(tet)
		ax.scatter(b[0],b[1],b[2],c=color,marker='^',alpha=alpha)
		# vertices
		plist = zip(*([ inputs['mesh'].getVertex(v) for v in (inputs['mesh'].getTet(tet)) ]))
		ax.scatter(plist[0],plist[1],plist[2],c=color,marker='^',alpha=alpha)

	ax.set_xlabel('X Label')
	ax.set_ylabel('Y Label')
	ax.set_zlabel('Z Label')

	plt.show()

def still_all(inputs):
	import numpy as np
	from mpl_toolkits.mplot3d import Axes3D
	import matplotlib.pyplot as plt

	h = inputs['h']
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	tetalpha = 0.3
	sectalpha = 0.3
	tetcolor = 'orange'
	sectcolor = 'blue'
	gapcolor = 'green'

	# plot tets
	for tet in inputs['comp'].tets:
		# barycenters
		b = inputs['mesh'].getTetBarycenter(tet)
		ax.scatter(b[0],b[1],b[2],c=tetcolor,marker='^',alpha=tetalpha)
		# vertices
		plist = zip(*([ inputs['mesh'].getVertex(v) for v in (inputs['mesh'].getTet(tet)) ]))
		ax.scatter(plist[0],plist[1],plist[2],c=tetcolor,marker='^',alpha=tetalpha)
	# plot sections and gap junctions
	for s in h.allsec():
		if (s in inputs['gaps']):
			color = gapcolor
		else:
			color = sectcolor
		ax.scatter(h.x3d(0),h.y3d(0),h.z3d(0),c=color,marker='o',alpha=sectalpha)

	ax.set_xlabel('X Label')
	ax.set_ylabel('Y Label')
	ax.set_zlabel('Z Label')

	plt.show()



#--- RUN VISUALIZATION ---#

def run_sim(inputs):
	exec (inputs['sim_meta_style']+"(inputs)")


