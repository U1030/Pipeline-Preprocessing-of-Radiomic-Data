import os
from tqdm import tqdm

import sys
#sys.path.append("")

from handle_ROI import determine_voi_size_in_number_of_pixels
from handle_paths import explore_folders_to_find_a_type_of_file as extract
from utils import handle_lists


def clean_up_small_lesions(nifti_folders):
    results = []
    for folder_path in tqdm(nifti_folders):
        files_to_delete = set()
        all_files = os.listdir(folder_path)       
        for file in all_files:
            file_path = os.path.join(folder_path, file)            
            if file.endswith('.nii.gz') and 'mask' in file:
                size  = determine_voi_size_in_number_of_pixels.get_size_of_roi(file_path)
                if size <= 64 :
                    files_to_delete.add(file)
                    print('lesion :',file,'size:', size)
        # Deleting the files that met the criteria
        results.append(files_to_delete)        
        for file in files_to_delete:
            file_to_delete_path = os.path.join(folder_path, file)
            os.remove(file_to_delete_path)            
    handle_lists.write_list_to_file(results,'lesions_too_small.csv')
    return results

def clean_up_small_components(nifti_folders):
    results = []
    for folder_path in tqdm(nifti_folders):
        files_to_delete = set()
        all_files = os.listdir(folder_path)       
        for file in all_files:
            file_path = os.path.join(folder_path, file)            
            if file.endswith('.nii.gz') and 'mask' in file and 'component' in file:
                size  = determine_voi_size_in_number_of_pixels.get_size_of_roi(file_path)
                if size <= 64 :
                    files_to_delete.add(file)
                    print('lesion ',file,'size:', size)
        # Deleting the files that met the criteria
        results.append(files_to_delete)        
        for file in files_to_delete:
            file_to_delete_path = os.path.join(folder_path, file)
            os.remove(file_to_delete_path)            
    handle_lists.write_list_to_file(handle_lists.flatten_list(results),'lesions_too_small.csv')
    return results


data_path = '' 

nifti_folders = extract.extract_folders_path(data_path, type='nifti')

clean_up_small_lesions(nifti_folders)
