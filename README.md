Manager for gromacs thermodynamic integration: Liquid Crystals model (OPLS-AAFF)
What is this?
This is a file manager for free energy calculations using thermodynamic integration in gromacs. This version is specifically made for liquid crystals and uses the OPLS force field.
How to run
The work directory needs to include:
-	the python scripts (FE_run.py, prepare_FE_mdp.py, fe_manager.py) 
-	the force field and topology files (oplsaa.ff, dwn.itp, upp.itp, system.top)
-	initial configuration (conf.gro)
-	the job template (t_job.sh)
-	the templates folder 
Then run : 
python FE_run.py
Available scripts
•	FE_run.py : main script where simulation parameters and simulation workflow are defined.
•	prepare_FE_mpd.py :  prepares the gromacs input files from available templates and defines the lambda vector.
•	fe_manager.py : manages the calculation inputs and builds directories for each point in the lambda vector.
  To do
•	add an output manager and analyzer 

