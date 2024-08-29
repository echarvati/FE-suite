import os
import shutil, numpy as np
import sys
import pandas as pd
from distutils.dir_util import copy_tree
from prepare_FE_mpd import prepare_mdp_from_FEtemplate


def filemanager(lambdas=None, run_calc ='no' ):
    print('setting up FE directories')

    src = os.getcwd()


    files = ['system.top', 'conf.gro', 'upp.itp','dwn.itp','grompp-alq-em.mdp','grompp-npt-eq.mdp', 'grompp-npt-prod.mdp', 'FE_job_slurm.sh' ]

    FE_temp = ['grompp-alq-em.mdp','grompp-npt-eq.mdp', 'grompp-npt-prod.mdp', 'FE_job_slurm.sh']

    FE_out = ['alq_em.mdp','npt_eq.mdp', 'npt_prod.mdp','_job_slurm.sh']


    print('set lambda points')
    lambda_points = {}
    names = []
    gtx_dirs = []
    temp_paths = []
    for i in range(0, lambdas):
        name = 'lambda-%02i' %i
        os.mkdir(name)
        names.append(name)
        for nm in names:
            dest = os.path.abspath(nm)
        lambda_points[i] = name, dest


    for point in lambda_points:
        lambda_dir, lambda_dest = lambda_points[point]
        for file in files:
            # print('aaaaaaaa', lambda_dest, src,file)
            if file=='system.top':
                with open('system.top') as topin:
                    contents = topin.read()

                    contents = contents.replace('%path%', str(src))
                with open('system.top', 'w') as topout:
                    topout.write(contents)

            shutil.copy(file, lambda_dest)


        os.chdir(lambda_dest)
        for out, temp in zip(FE_out, FE_temp):
            with open(temp, 'r') as f_in, open(out, 'w') as f_out:
                contents = f_in.read()
                contents = contents.replace('%lambda%', str(point).zfill(2))
                temp_paths.append(os.path.join(lambda_dest, temp))
                f_out.write(contents)

    for path in temp_paths:
        os.remove(path)

    for pnt in lambda_points:
        dir, dest = lambda_points[pnt]
        os.chdir(dest)
        os.rename('alq_em.mdp', 'grompp-alq-em.mdp')
        os.rename('npt_eq.mdp', 'grompp-npt-eq.mdp')
        os.rename('npt_prod.mdp', 'grompp-npt-prod.mdp')

        if run_calc == 'yes':

            os.system('sbatch _job_slurm.sh')

        elif run_calc == 'no':
            continue

#TODO: output manager!
#TODO: output manager!
def manage_outputs(lambdas=None):
    dhdllogs =[]
    root = os.getcwd()
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
        # elif dir == 'LOGS':
        #     pdbfiles = os.path.join(root, 'PDBs')
        elif dir == 'XTCs':
            xtcfiles = os.path.join(root, 'XTCs')
        else:
            continue

    for i in range(0, lambdas):
        for dir in dirs:
            if dir == 'lambda-%02i' %i:
                os.chdir(dir)
                shutil.copy('dhdl.%02i.log' % i, logfiles)
                shutil.copy('dhdl.%02i.xvg' % i, dhdl_data)
                shutil.copy('dhdl.%02i.gro' % i, grofiles)
                # shutil.copy('dhdl.%02i.pdb' % i, pdbfiles)
                shutil.copy('dhdl.%02i.xtc' % i, xtcfiles)
                print('Retrieving data from', dir)
                os.chdir(root)
            else:
                continue

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


#TODO: analyzer!
def gmxbar( dhdl_data):
        datum=[]
        deltas = []
        os.chdir(dhdl_data)
        # stdoutOrigin = sys.stdout
        # sys.stdout = open("gmxlog.log", "w")
        cmd_00 = 'module purge'
        cmd_01 = 'module load gcc/8.4.1'
        cmd_02 = 'module load fftw/3.3.9'
        cmd_03 = 'module load cuda/11.6'
        cmd_04 = 'module load gromacs/2022.5'
        cmd = 'gmx bar -f dhdl.*.xvg -b 50000000 -o bar.xvg -oi barint.xvg -oh histobar.xvg -quiet -prec 4 -xvg none | tee gmx_bar_output.log'
        # cmd_1 = 'gracebat -hdevice JPEG -printfile barint.jpg barint.xvg'
        # cmd_2 = 'gracebat -hdevice JPEG -printfile bar.jpg bar.xvg'
        # cmd_3 = 'gracebat -hdevice JPEG -printfile histobar.jpg histobar.xvg'
        os.system(cmd_00)
        os.system(cmd_01)
        os.system(cmd_02)
        os.system(cmd_03)
        os.system(cmd_04)
        os.system(cmd)
        # os.system(cmd_1)
        # os.system(cmd_2)
        # os.system(cmd_3)
        # sys.stdout.close()
        # sys.stdout = stdoutOrigin
        fout = pd.read_csv('bar.xvg', skiprows=(16), header=(0), sep='\s+', names=['lambda', 'DG', 'err'])
        DG_kT = fout['DG']
        err = fout['err']
        DGdata = DG_kT.tolist()
        errdata = err.tolist()
        for i in range(len(DGdata)-1):
            j = i+1
            DeltaDG = DGdata[i] - DGdata[j]
            Delta_err = errdata[i] - errdata[j]
            delta_pt = [i, j, DeltaDG, Delta_err]
            deltas.append(delta_pt)
        # print(deltas, type(deltas))
        df_deltas = pd.DataFrame(deltas, columns=["i", "i+1", "DeltaDG", "delta_err"])
        df_deltas.to_csv("diffs.csv", index=False, sep=" ")

        TotDG_kT = sum(fout['DG'])
        TotDG_kcalmol = (TotDG_kT * 2.479) / 4.18
        Toterr_kT = sum(fout['err'])
        Toterr_kcalmol = Toterr_kT * 2.479 / 4.18
        datum.append(TotDG_kcalmol)
        datum.append(Toterr_kcalmol)
        return datum



