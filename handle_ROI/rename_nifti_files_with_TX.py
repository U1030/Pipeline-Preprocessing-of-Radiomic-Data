import os

import sys
#sys.path.append("")


from handle_paths import explore_folders_to_find_a_type_of_file as find
from parralelize import parallelize_v2 as par 
from handle_paths import extract_paths

def flatten_list(list_of_lists):
  return [item for sublist in list_of_lists for item in sublist]


def extract_mask_name(filename):
  mask_index = filename.find("mask")
  id_index = filename.find("id")    
  return filename[mask_index:id_index + 4]   


def rename_TX(patient_path):
    folders = find.extract_folders_path(patient_path, type='nifti')
    renamed_files = []
    for folder_path in folders :
        if "Baseline" in folder_path or "T0" in folder_path or "E0" in folder_path: 
            files = os.listdir(folder_path)    
            for filename in files :         
                if "TX" in filename: 
                    original_file_path = os.path.join(folder_path,filename)              
                    new_filename = filename.replace("TX", "T0")  
                    new_file_path = os.path.join(folder_path, new_filename)            
                    os.rename(original_file_path, new_file_path)
                    renamed_files.append((original_file_path," --> ",new_file_path))
        elif "Evaluation" in folder_path or "T1" in folder_path or "E1" in folder_path: 
            files = os.listdir(folder_path)    
            for filename in files :         
                if "TX" in filename: 
                    original_file_path = os.path.join(folder_path,filename)              
                    new_filename = filename.replace("TX", "T1")  
                    new_file_path = os.path.join(folder_path, new_filename)            
                    os.rename(original_file_path, new_file_path) 
                    renamed_files.append((original_file_path," --> ",new_file_path))  
    return

def process_all_patients(path,depth = 2, direct =True):    
    if direct :
      subfolders = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
      patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
      patients_paths = extract_paths.get_folders_at_depth(path, depth)   
    results = par.parralelize_for_patients(patients_paths, rename_TX)
    return