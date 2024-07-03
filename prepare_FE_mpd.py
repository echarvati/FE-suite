import os
import shutil
import subprocess
from subprocess import Popen, PIPE




def prepare_mdp_from_FEtemplate(FEtemplate, FEmdp_out='FEgrompp.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=298, P=1, TANNEAL=368, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='eq',vdw_vector=None ,coul_vector=None,
                                lambdaneighs=2, molecule='molecule'):

    workdir = os.getcwd()
    temp_dir = os.path.join(workdir, 'templates')
    os.chdir(temp_dir)

    if tcoupl.lower() == 'langevin':
        integrator = 'sd'
        tcoupl = 'no'
        tau_t = str(0.001 / dt)  # inverse friction coefficient
    else:
        raise Exception('Invalid tcoupl, only Langevin is adapted for coupling')

    if pcoupl.lower() == 'berendsen':
        tau_p = '0.5'
    elif pcoupl.lower() == 'parrinello-rahman':
        tau_p = '2.0'
    else:
        raise Exception('Invalid pcoupl, should be one of berendsen or parrinello-rahman')

    if restart:
        genvel = 'no'
        continuation = 'yes'
    else:
        genvel = 'yes'
        continuation = 'no'


    if step == 'eq':
        dhdl = 0
    elif step == 'prod':
        dhdl = 50


    if len(vdw_vector) != len(coul_vector):
        print('Invalid lambda vectors!')
    elif len(vdw_vector) == len(coul_vector):
        print(len(vdw_vector))
    vdw_lambdas = str(vdw_vector).strip('[]').replace(',', '')
    coul_lambdas = str(coul_vector).strip('[]').replace(',', '')

    nstenergy = 100 # output energy


    with open(FEtemplate) as f_t_fe:
        contents = f_t_fe.read()

        contents = contents.replace('%T%', str(T)).replace('%ref-p%', str(P)).replace('%nsteps%', str(int(nsteps))) \
                .replace('%dt%', str(dt)).replace('%nstenergy%', str(nstenergy)).replace('%nstdhdl%', str(dhdl)) \
                .replace('%nstxtcout%', str(nstxtcout)).replace('%xtcgrps%', str(xtcgrps)) \
                .replace('%genvel%', genvel).replace('%continuation%', continuation) \
                .replace('%integrator%', integrator).replace('%tcoupl%', tcoupl).replace('%tau-t%', tau_t) \
                .replace('%pcoupl%', pcoupl).replace('%taup%', tau_p).replace('%constraints%', constraints) \
                .replace('%sc-alpha%', str(scalpha)).replace('%sc-power%', str(scpower)).replace('%sc-sigma%', str(scsigma)) \
                .replace('%vdw_lambdas%', vdw_lambdas).replace('%coul_lambdas%', coul_lambdas) \
                .replace('%calc_lambda_neighbors%', str(lambdaneighs)).replace('%TANNEAL%', str(TANNEAL))\
                .replace('%molecule%', str(molecule))


    with open(FEmdp_out, 'w') as FE_f_mdp:
        FE_f_mdp.write(contents)

    source_file = os.path.join(temp_dir, FEmdp_out)
    destination_file = os.path.join(workdir, FEmdp_out)
    shutil.move(source_file, destination_file)
    os.chdir(workdir)



def prepare_slurm(composition):

    workdir = os.getcwd()
    os.chdir(workdir)

    job_out = 'FE_job_slurm.sh'

    slurm_file = 't_job.sh' # job template

    with open(slurm_file) as job:
        contents = job.read()
        contents = contents.replace('%composition%', str(composition))


    with open(job_out, 'w') as FE_slurm:
        FE_slurm.write(contents)



