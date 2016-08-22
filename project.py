
template = 'default'

def project_inputs(inputs):
	# customize project from template
	inputs['mesh_meta'] = 'network'
	inputs['mesh_meta_style'] = 'layers'
	inputs['net_cells'] = 'auto'
	inputs['net_rowlen'] = 1
	inputs['net_layers'] = 1
	inputs['mesh_style'] = 'overwrite' 

	inputs['sim_meta'] = 'lscale_finder'
	inputs['sim_meta_style'] = 'none'
	inputs['report_stages'] = ['sim_block']
	inputs['gap_mark'] = '^'
	inputs['vis_title'] = 'New Vis Title'
	inputs['tstop'] = 200.0