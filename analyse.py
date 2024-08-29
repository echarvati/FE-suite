import sys
import os
import shutil
import itertools
from prepare_FE_mpd import prepare_mdp_from_FEtemplate, prepare_slurm
from output_manager import gmxbar_FE, manage_files

def analyseFE(lambdas):


    workspace = os.getcwd()


    data=[]

    manage_files(lambdas=lambdas)


    # gmx_dipole(lambdas=lambdas)

    logs = os.path.join(workspace, 'LOGS')
    dhdl= os.path.join(workspace, 'DHDL')
    datum = gmxbar_FE(dhdl)
    data.append(datum)
    os.chdir(workspace)

    print('Writing summary...')

# cmd_00 = 'module purge;'
# cmd_01 = 'module load gcc/8.4.1;'
# cmd_02 = 'module load fftw/3.3.9;'
# cmd_03 = 'module load cuda/11.6;'
# cmd_04 = 'module load gromacs/2022.5;'
#
# os.system(cmd_00)
# os.system(cmd_01)
# os.system(cmd_03)
# os.system(cmd_02)
# os.system(cmd_04)


analyseFE(lambdas=44)


    #print(output)

    # with open('summary.csv', 'w') as out:
    #     for otp in output:
    #         out.write(str(otp) + '\n')
