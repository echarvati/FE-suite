import sys
import os
import shutil
from prepare_FE_mpd import prepare_mdp_from_FEtemplate, prepare_slurm
from fe_manager import filemanager


#Set-up. Units follow the gromacs units
Teq = 375 # temprature for equilibration
Tprod = 444 # temprature for production
P = 1

# Set lambda vector for vdw and coulomb interactions.
# The two vectors should have the same size!

#Example lambda vectors
# vdw_vector = [0.00, 0.10, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.60, 0.70, 0.80,
#                   1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00, 1.00]
# coul_vector = [0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.00,
#                    0.00, 0.30, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00]
# vdw_vector = [0, 0.05, 0.1, 0.15, 0.17, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1, 1, 1, 1, 1, 1,1]
# coul_vector = [0, 0,0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.3, 0.6, 0.7, 0.8, 0.9, 0.95, 1]

# vdw_vector = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.8, 0.7,0.6, 0.5,0.4, 0.3,0.2, 0.1, 0.0]
# coul_vector = [1.0, 0.9, 0.8, 0.7,0.6,0.3, 0.0,0.0,0.0,0.0,0.0, 0.0,0.0, 0.0,0.0,0.0]

vdw_vector = [1.00,	1.00,1.00,1.00,	1.00,1.00,1.00,	1.00,1.00,1.00,	1.00,1.00,1.00,	1.00,1.00,0.95,	0.9,0.80,0.85,0.70,0.65,0.60,0.55,0.50,0.45,0.40,0.35,0.30,0.25,0.20,0.10,0.00]
coul_vector = [1.00,0.95,0.90,0.85,	0.80,0.75,0.70,	0.65,0.60,0.55,	0.50,0.45,0.40,	0.35,0.30,0.00,	0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00]


lambdas = len(vdw_vector) #number of points in the lambda vactor
up = 399 #number of upwords pointing LC molecules
down= 1 #number of downwords pointing LC molecules
composition = '%i_%i' %(up, down)

run_calc ='no' #do you want to run this set-up?


#Start FE set-up
prepare_slurm(composition)

# Coupling depends on the compositions. The configuration ("up" or "down") that has more moleules is the one getting
# coupled at each lambda point.
if up << down:
    prepare_mdp_from_FEtemplate(FEtemplate='t_emcoupl_fe.mdp', FEmdp_out='grompp-alq-em.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=Teq, P=P, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='eq',
                                vdw_vector=vdw_vector, coul_vector=coul_vector
                                ,lambdaneighs=2, molecule='DWN')

    prepare_mdp_from_FEtemplate(FEtemplate='t_npt_fe.mdp', FEmdp_out='grompp-npt-eq.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=Teq, P=P, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='eq', vdw_vector=vdw_vector, coul_vector=coul_vector,
                                lambdaneighs=2, molecule='DWN')

    prepare_mdp_from_FEtemplate(FEtemplate='t_npt_fe.mdp', FEmdp_out='grompp-npt-prod.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=Tprod, P=P, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='prod',vdw_vector=vdw_vector, coul_vector=coul_vector,
                                lambdaneighs=2, molecule='DWN')

elif up >> down:
    prepare_mdp_from_FEtemplate(FEtemplate='t_emcoupl_fe.mdp', FEmdp_out='grompp-alq-em.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=Teq, P=P, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='eq',vdw_vector=vdw_vector, coul_vector=coul_vector,
                                lambdaneighs=2, molecule='UPP')

    prepare_mdp_from_FEtemplate(FEtemplate='t_npt_fe.mdp', FEmdp_out='grompp-npt-eq.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=Teq, P=P, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='eq',vdw_vector=vdw_vector, coul_vector=coul_vector,
                                lambdaneighs=2, molecule='UPP')

    prepare_mdp_from_FEtemplate(FEtemplate='t_npt_fe.mdp', FEmdp_out='grompp-npt-prod.mdp', tcoupl='langevin',
                                pcoupl='parrinello-rahman',
                                T=Tprod, P=P, nsteps=400000, dt=0.001, nstxtcout=10000,
                                xtcgrps='System',
                                restart=False, constraints='h-bonds', dielectric=None, scalpha=0.5,
                                scpower=1, scsigma=0.3, step='prod', vdw_vector=vdw_vector, coul_vector=coul_vector,
                                lambdaneighs=2, molecule='UPP')

prepare_slurm(composition)

filemanager(lambdas,run_calc)

# manage_outputs(lambdas)
