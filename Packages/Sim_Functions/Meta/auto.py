def run_sim(inputs):
	exec ('from Packages.Sim_Functions.' + inputs['sim_file'] + ' import run_sim as simulate')
	simulate(inputs)