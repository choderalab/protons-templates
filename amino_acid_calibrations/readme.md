README
------

`run_calibration.py` is a script that reads in a JSON file with settings. Each of the "results" directories contain a settings.json file.

`submit_calibration.sh` is a template submit script
`amino_acid_calibration.json` is a template settings file. 

The settings json file points to where the input files are located, and sets some simulation defaults. 

Pay special attention to the parameters sections.
Note that filenames are specified according to the `basename` and `methodname` parameters for programmability/reusability of the template.

The `master_submit.sh` file is used to submit all of there calibrations. You can find out how to run the script from there.
Typically, from _this directory_, use bsub < subdir/submit.sh, so that all relative paths match

`generate_calibrations.py` fills in the templates and makes the subdirectories.
