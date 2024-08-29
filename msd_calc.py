import MDAnalysis as mda
import MDAnalysis.analysis.msd as msd
from scipy.stats import linregress
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

def save_msd(msd_data, root_directory, filename="msd_results.csv"):
    # Ensure the root directory exists
    if not os.path.exists(root_directory):
        os.makedirs(root_directory)

    # Create the full path for the CSV file
    filepath = os.path.join(root_directory, filename)

    # Save the data to the CSV file
    df = pd.DataFrame(msd_data, columns=["Lambda", "MSD_mean", "MSD_error"])
    df.to_csv(filepath, index=False)
    print(f"Saved MSD data to {filepath}")


def calculate_self_diffusion_coefficient(traj_file, top_file, atom_selection="all", timestep=1.0, n_blocks=5):
    # Load the trajectory
    u = mda.Universe(top_file, traj_file)

    # Select the atoms for which you want to calculate the MSD
    atoms = u.select_atoms(atom_selection)

    # Calculate the mean square displacement (MSD)
    MSD = msd.EinsteinMSD(u, select=atom_selection, msd_type='xyz', fft=True)
    MSD.run(verbose=False)

    # Time data in picoseconds
    nframes = MSD.n_frames
    lagtimes = np.arange(nframes) * timestep  # make the lag-time axis
    msd_data = MSD.results.timeseries

    # Linear fit of MSD vs. time to extract diffusion coefficient
    slope, intercept, _, _, _ = linregress(lagtimes, msd_data)
    diffusion_coefficient = slope / 6.0

    # Error estimation using block averaging
    block_size = nframes // n_blocks
    diffusion_coefficients = []

    for i in range(n_blocks):
        start = i * block_size
        end = (i + 1) * block_size
        slope_block, _, _, _, _ = linregress(lagtimes[start:end], msd_data[start:end])
        D_block = slope_block / 6.0
        diffusion_coefficients.append(D_block)

    # Calculate the mean and standard error of the diffusion coefficients
    diffusion_coefficient_mean = np.mean(diffusion_coefficients)
    diffusion_coefficient_std = np.std(diffusion_coefficients, ddof=1)
    diffusion_coefficient_error = diffusion_coefficient_std / np.sqrt(n_blocks)

    # Print the result with error estimation
    print(f"Self-Diffusion Coefficient: {diffusion_coefficient_mean:.5e} ± {diffusion_coefficient_error:.5e} cm^2/s")

    # Plot MSD vs Time
    fig, ax = plt.subplots()
    ax.plot(lagtimes, msd_data, color="black", linestyle="-", label=r'3D random walk')
    ax.plot(lagtimes, slope * lagtimes + intercept, color="red", linestyle="--", label=f'Fit: D = {diffusion_coefficient_mean:.5e} cm^2/s')
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('MSD (Å²)')
    ax.legend()
    plt.title('Mean Square Displacement')
    plt.savefig('msd.png')


    return diffusion_coefficient_mean, diffusion_coefficient_error

