import os
from tqdm import tqdm

import sys
#sys.path.append("")

from handle_ROI import determine_voi_size_in_number_of_pixels
from handle_paths import explore_folders_to_find_a_type_of_file as extract
from utils import handle_lists


def main(path,tumor_accronym):
    nifti_folders = extract.extract_folders_path(path, type='nifti')
    for folder_path in tqdm(nifti_folders):
        # Create a set of all files in the folder with lowercase names for case-insensitive search
        files_in_folder = {file.lower(): file for file in os.listdir(folder_path)}        
        for file_name in os.listdir(folder_path):
            file_name_lower = file_name.lower()
            file_path = os.path.join(folder_path, file_name)           
            if 'ring' in file_name_lower:
                    if tumor_accronym == 'gtv' or tumor_accronym == 'GTV':
                        # Replace 'gtv' with 'ring'
                        search_name = file_name_lower.replace('ring', 'gtv')
                    elif tumor_accronym == 'tum' or tumor_accronym == 'TUM':
                        # Replace 'tum' with 'ring'
                        search_name = file_name_lower.replace('ring', 'tum')
            else:
                continue            
            # Search for the corresponding file in the folder
            if search_name in files_in_folder:
                matched_file = files_in_folder[search_name]
                search_path = os.path.join(folder_path, matched_file)            
            else:
                print(f"No corresponding file found for {file_path}")
                os.remove(file_path)



path = '' 
tumor_accronym = 'gtv'

main(path,tumor_accronym=tumor_accronym)