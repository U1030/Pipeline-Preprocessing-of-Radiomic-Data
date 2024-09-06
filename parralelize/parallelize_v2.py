import os 
import psutil
import time
from multiprocessing import Pool
from tqdm import tqdm
from functools import partial

import sys
#sys.path.append("")


from handle_paths import extract_paths


def compute_patients_paths(path,depth=2, direct=True):
    if direct :
      subfolders = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
      patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
      patients_paths = extract_paths.get_folders_at_depth(path, depth) 
    return patients_paths

def parralelize_for_patients(patients_paths,function, processes=-1):    
    start = time.time()    
    if processes <= 0:
        num_cpus = psutil.cpu_count(logical=False)
    else:
        num_cpus = processes
    process_pool = Pool(processes=num_cpus)
    results = []
    for _ in tqdm(process_pool.imap_unordered(function, patients_paths), total=len(patients_paths)):
        results.append(_)
    process_pool.close()
    process_pool.join()
    end = time.time()
    print('Completed in: %s sec' % (end - start))
    return results

def parralelize_for_patients_several_args(paths_patients, function, processes=-1, **kwargs):  
    start = time.time()    
    if processes <= 0:
        num_cpus = psutil.cpu_count(logical=False)
    else:
        num_cpus = processes
    process_pool = Pool(processes=num_cpus)
    results = []
    for _ in tqdm(process_pool.imap_unordered(partial(function, **kwargs), paths_patients), total=len(paths_patients)):
        results.append(_)
    process_pool.close()
    process_pool.join()
    end = time.time()
    print('Completed in: %s sec' % (end - start))
    return results

