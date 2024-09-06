import os
import subprocess

import sys
#sys.path.append("")

from parralelize import parallelize_v2 as par
from handle_paths import extract_paths


def contains_dicom_files(folder_path):
    """Check if the folder contains any .dcm files."""
    if not os.path.isdir(folder_path):
        return False
    
    for file in os.listdir(folder_path):
        if file.endswith('.dcm'):
            return True
    
    return False

def convert_one_patient(patient_path):            
    sub_subfolders = os.listdir(patient_path)
    test = any(contains_dicom_files(os.path.join(patient_path, folder)) for folder in sub_subfolders)    
    if test:        
        subprocess.run(["conv-dcm2nii", "-i", patient_path, "-o", patient_path])       
   
    for sub_time in sub_subfolders:        
        sub_time_path = os.path.join(patient_path, sub_time)
        sub_sub_subfolders = os.listdir(sub_time_path)
        test = any(contains_dicom_files(os.path.join(sub_time_path, folder)) for folder in sub_sub_subfolders)        
        if test:            
            subprocess.run(["conv-dcm2nii", "-i", sub_time_path, "-o", sub_time_path])             
            
        for sub_loc in sub_sub_subfolders:           
            sub_loc_path = os.path.join(sub_time_path, sub_loc)
            if os.path.isdir(sub_loc_path):
                sub_sub_sub_subfolders = os.listdir(sub_loc_path)
                test = any(contains_dicom_files(os.path.join(sub_loc_path, folder)) for folder in sub_sub_sub_subfolders)            
                if test:                    
                    subprocess.run(["conv-dcm2nii", "-i", sub_loc_path, "-o", sub_loc_path])              
    
    return


def process_all_patients(path,depth = 2, direct = True):    
    if direct :
      subfolders = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
      patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
      patients_paths = extract_paths.get_folders_at_depth(path, depth)   

    results = par.parralelize_for_patients(patients_paths, convert_one_patient)
    return


