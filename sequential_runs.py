import os, shutil
from jinja2 import Template, Environment, FileSystemLoader

env = Environment(trim_blocks=True, keep_trailing_newline=True, loader=FileSystemLoader('templates'))

run_template_prot = env.get_template('sequential_calibration_plus_protein.py.j2', parent='protons_base.j2')
run_template_lig = env.get_template('sequential_calibration_solvent.py.j2', parent='protons_base.j2')
submit_template = env.get_template('submit_calibration.sh.j2')

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
driver['ncmc_steps_per_trial'] = '10000' # *2 fs =  20 ps
driver['total_iterations'] = '1000'

# Parameters for the calibration. Beta is between 1.0 and 0.5
# the flatness criterion is a heuristic for how flat histogram 
# produced by the sams chain should be before switch
sams = dict()
sams['beta'] = 0.5
sams['flatness_criterion'] = 0.2


abl = dict(name="Abl-Imatinib-full", inputpdb="2HYY-H.pdb", ligandxml='imatinib.xml', type='protein+ligand')
abl_ligonly = dict(name="Abl-Imatinib-ligonly", inputpdb="2HYY-H.pdb", ligandxml='imatinib.xml', type='ligand')
imatinib = dict(name="Imatinib-solvent", inputpdb="imatinib-solvated-for-calibration.pdb", ligandxml='imatinib.xml', type="ligand")
# ddr1 = dict(name="DDR1-Ponatinib-full", inputpdb="3ZOS-H.pdb", ligandxml="ponatinib.xml", type="protein+ligand")
# ddr1_ligonly = dict(name="DDR1-Ponatinib-ligonly", inputpdb="3ZOS-H.pdb", ligandxml="ponatinib.xml", type="ligand")
# ponatinib =  dict(name="Ponatinib-solvent", inputpdb="ponatinib-solvated-for-calibration.pdb", ligandxml="ponatinib.xml", type="ligand")

for dirname in ['Sequential Abl']:
    integrator['class'] = "GBAOAB"
    inputfiledir = os.path.abspath("input_files")
    os.makedirs(dirname, exist_ok=True)    
    for runtype in [abl, abl_ligonly, imatinib]:#, ddr1, ddr1_ligonly, ponatinib]:
        subdirname = os.path.join(dirname, runtype['name'])
        os.makedirs(subdirname, exist_ok=True)        

        simulation = dict()
        simulation['type'] = runtype['type']
        options['integrator'] = integrator
        options['simulation'] = simulation
        options['system'] = system
        options['driver'] = driver
        options['sams'] = sams

        shutil.copyfile(os.path.join(inputfiledir, runtype['inputpdb']), os.path.join(subdirname, runtype['inputpdb']))
        shutil.copyfile(os.path.join(inputfiledir, runtype['ligandxml']), os.path.join(subdirname, runtype['ligandxml']))

        # Do 5 runs
        for series in range(1,6):
            inputdict = dict()
            inputdict['pdbfile'] = runtype['inputpdb']
            inputdict['ligandxml'] = runtype['ligandxml']
            output = dict()
            basename = runtype['name'] + "-%d" % series
            prev_name = runtype['name'] + "-%d" % (series -1)
            output['basename'] = basename
            options['input'] = inputdict
            options['output'] = output
            output_context_xml = "resume-%s-state.xml" % prev_name
            output_drive_xml = "resume-%s-drive.xml" % prev_name
            output_sams_json = "resume-%s-calibration.json" % prev_name
            script = dict(name="run_simulation-%d.py"%series)
            # First iteration does not have checkpoint files
            if series > 1:
                script['resume'] = dict(state_xml=output_context_xml, drive_xml=output_drive_xml, sams_json=output_sams_json)
            options['script'] = script

            options['job'] = dict(title=basename + '-' + integrator['class'] )
            # Last iteration does not have resubmission script
            if series < 5:
                options['job']['resubmission_script'] = "submit_simulation-%d.sh" % (series+1)

            # Choose the right template.
            if simulation['type'] == 'ligand':
                run_template = run_template_lig
            elif simulation['type'] == 'protein+ligand':
                run_template = run_template_prot
            else:
                raise ValueError("Invalid simulation type {}".format(simulation['type']))

            rendered = run_template.render(options)
            with open(os.path.join(subdirname, script['name']), 'w') as run_script:
                run_script.write(rendered)

            rendered = submit_template.render(options)
            with open(os.path.join(subdirname, "submit_simulation-%d.sh"%series), 'w') as submit_script:
                submit_script.write(rendered)

        
