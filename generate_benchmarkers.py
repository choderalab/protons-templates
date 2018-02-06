import os, shutil
from jinja2 import Template, Environment, FileSystemLoader
env = Environment(trim_blocks=True, keep_trailing_newline=True, loader=FileSystemLoader('templates'))
aa_template = env.get_template('ncmc_amino_acid_benchmark.j2')
submit_template = env.get_template('submit_ncmc_benchmark.j2')

options = dict()
integrator = dict()
integrator['timestep'] = '2.0' # femtoseconds
integrator['collision_rate'] = '1.0' # /picosecond
integrator['number_R_steps'] = '1'

system = dict()
system['ewaldErrorTolerance'] = '1.e-5'
system['barostatInterval'] = '25'
system['switching_distance'] = '0.85' # nanometers
system['nonbondedCutoff'] = '1.0' # nanometers
system['pressure'] = '1.0' # atmosphere
system['temperature'] = '300.0' # kelvin

driver = dict()
# TODO override this

driver['total_iterations'] = '100'

runs = list()
# instantaneous, 200 fs, 2 ps,10 ps, 20 ps, 100 ps
his = dict(basename='his', states=3, steps=[1,100,1000,5000, 10000,50000], inpcrd='his.inpcrd', prmtop='his.prmtop')
runs.append(his)

for dirname in ['Benchmarks-2017-12-01']:
    inputfiledir = os.path.abspath("input")
    os.makedirs(dirname, exist_ok=True)    
    for run in runs:
        subdirname = os.path.join(dirname, run['basename'])
        os.makedirs(subdirname, exist_ok=True)        
        
        simulation = dict()
        options['integrator'] = integrator
        options['simulation'] = simulation
                
        inputdict = dict()
        inputdict['inpcrd'] = run['inpcrd']
        inputdict['prmtop'] = run['prmtop']
        options['system'] = system
        shutil.copyfile(os.path.join(inputfiledir, run['inpcrd']), os.path.join(subdirname, run['inpcrd']))
        shutil.copyfile(os.path.join(inputfiledir, run['prmtop']), os.path.join(subdirname, run['prmtop']))
        for starting_state in range(run['states']):
            options['simulation']['state'] = '%d' % starting_state
            
            for num_ncmc_steps in run['steps']:
                driver['ncmc_steps_per_trial'] = '%d' % num_ncmc_steps # each step is 2 fs
                options['driver'] = driver

                output = dict()
                basename = '%s-%dsteps-state%d' % (run['basename'], num_ncmc_steps, starting_state)
                output['basename'] = basename
                options['input'] = inputdict
                options['output'] = output        
                
                script = dict(name="run_simulation-%dsteps_state%d.py"%(num_ncmc_steps, starting_state))
                options['script'] = script

                rendered = aa_template.render(options)
                with open(os.path.join(subdirname, script['name']), 'w') as run_script:
                    run_script.write(rendered)
