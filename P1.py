import numpy as np
import os,sys
import pandas as pd

import os,sys
def xvg2csv(fname):
    delimiter = ','
    if fname[-3:] != "xvg":
        print("The provided file is not in .xvg format.")
        sys.exit(0)

    with open(fname, 'r') as fid:
      ll = fid.readlines()

    try:
      rem = int(sys.argv[2])
    except:
      rem = 1

    fout = open(fname[:-3]+'csv','w')

    it = 0
    M = len(ll[-1].split())
    labels = [""]*M
    labels[0] = "Time (ps)"
    #print("Found" + str(M) + "columns:")
    #print('  ',"Time")

    i=1
    for l in ll:
      if l.startswith("@ s"):
          label = (' '.join(l.split()[3:])[1:-1])
          #print('  ',label)
          labels[i] = label
          i += 1
          if i == M:
              fout.write(delimiter.join(labels)+'\n')
      if l[0] in ['#','@']:
        continue
      elif it%rem == 0:
        s = l.split()
        fout.write(delimiter.join(s)+'\n')
      it += 1
    fout.close()
    
def GetB(array):
    N = 2
    newval = 0
    (np.put_along_axis(array,np.argpartition(array,N,axis=1)[:,N:],newval,axis=1))
    return(array[:,1:])
    
def GetDipData(fname='dip.txt'):
    '''
    Retrieves dipole data from dip.txt
    '''
    
    with open(fname,'r') as fid:
         ll = fid.readlines()
    
    NMols  = int(ll[3].split()[2])
    Dipole = float(ll[8].split()[2])    

    return(NMols, Dipole)


def save_p1(p1_data, root_directory, filename="P1_results.csv"):
    # Ensure the root directory exists
    if not os.path.exists(root_directory):
        os.makedirs(root_directory)

    # Create the full path for the CSV file
    filepath = os.path.join(root_directory, filename)

    # Save the data to the CSV file
    df = pd.DataFrame(p1_data, columns=["Lambda", "P1_mean", "P1_error"])
    df.to_csv(filepath, index=False)
    print(f"Saved P1 data to {filepath}")


def calculate_p1():
    xvg2csv('Mtot.xvg')
    TotDip = np.genfromtxt('Mtot.csv', delimiter=',')[1:, 4]

    NMols, Dipole = GetDipData()

    P1 = TotDip / (NMols * Dipole)
    np.savetxt("P1.csv", P1, delimiter=",")

    P1_mean = np.round(np.mean(P1), 3)
    P1_error = np.round(np.std(P1), 3)

    print("")
    print("Results:")
    print(f"<P1> is: {P1_mean} +/- {P1_error}")

    return P1_mean, P1_error

