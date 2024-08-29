import os
import shutil
import pandas as pd
from msd_calc import calculate_self_diffusion_coefficient, save_msd
from P1 import calculate_p1, save_p1

#TODO: output manager!
#TODO: output manager!

def manage_files(lambdas=None):
    diffusion_coeff =[]
    root = os.getcwd()
    p1_data = []
    print('Working on', root)
 #TODO more flexible data management!
    os.mkdir('DHDL')
    os.mkdir('LOGS')
    os.mkdir('GROs')
    # os.mkdir('PDBs')
    os.mkdir('XTCs')
    dirs = os.listdir(root)
    for dir in dirs:
        if dir=='DHDL':
            dhdl_data = os.path.join(root, 'DHDL')
        elif dir=='LOGS':
            logfiles = os.path.join(root, 'LOGS')
        elif dir == 'GROs':
            grofiles = os.path.join(root, 'GROs')
        elif dir == 'XTCs':
            xtcfiles = os.path.join(root, 'XTCs')
        else:
            continue

    for i in range(0, lambdas):
        for dir in dirs:
            if dir == 'lambda-%02i' %i:
                os.chdir(dir)
                print('Retrieving data from', dir)
                shutil.copy('dhdl.%02i.log' % i, logfiles)
                shutil.copy('dhdl.%02i.xvg' % i, dhdl_data)
                shutil.copy('dhdl.%02i.gro' % i, grofiles)
                shutil.copy('dhdl.%02i.xtc' % i, xtcfiles)


                traj_file = 'dhdl.%02i.xtc' %i  # Replace with your trajectory file
                top_file = 'dhdl.%02i.tpr' %i # Replace with your topology file
                diffusion_coefficient_mean, diffusion_coefficient_error = calculate_self_diffusion_coefficient(traj_file, top_file, atom_selection="all", timestep=1.0)
                diffusion_coeff.append([i,diffusion_coefficient_mean, diffusion_coefficient_error])
                #
                # Calculate P1
                cmd = f'echo -e "0" | gmx dipoles -f dhdl.{i:02}.xtc -s dhdl.{i:02}.tpr > dip.txt'
                os.system(cmd)
                #
                P1_mean, P1_error = calculate_p1()

                # Collect P1 data
                p1_data.append([i, P1_mean, P1_error])


                os.chdir(root)
            else:
                continue

    # Save data
    save_msd(diffusion_coeff, root)
    save_p1(p1_data, root)

    check = []
    os.chdir(logfiles)
    end_phrase = 'Finished mdrun'
    log = os.listdir()
    for l in log:
        with open(l, "r") as l:
            if end_phrase in l.read():
                check.append('true')
            else:
                check.append('false')
    if "false" in check:
        simu = False
        print('Simulation incomplete at lambda state', check.index('false'))
    else:
        simu = True
        print('Simulations for all lambda states completed')

    return simu


def gmxbar_FE(dhdl_data):

    os.chdir(dhdl_data)
    cmd = 'gmx bar -f dhdl.*.xvg -b 8000000 -o bar.xvg -oi barint.xvg -oh histobar.xvg -quiet -prec 4 -xvg none | tee gmx_bar_output.log'
    os.system(cmd)


