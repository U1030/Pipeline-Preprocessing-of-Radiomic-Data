import os

import sys
#sys.path.append("")

from handle_ROI import determine_nifti_mask_smallest_diameter
from handle_paths import explore_folders_to_find_a_type_of_file as extract
from utils import handle_lists


def clean_up_small_lesions(nifti_folders):
    results = []
    for folder_path in nifti_folders:
        files_to_delete = set()
        all_files = os.listdir(folder_path)       
        for file in all_files:
            file_path = os.path.join(folder_path, file)            
            if file.endswith('.nii.gz') and 'mask' in file:
                center_of_mass, boundary_points, closest_boundary_point, smallest_radius, smallest_diameter = determine_nifti_mask_smallest_diameter.calculate_smallest_diameter_and_points(file_path)
                if smallest_diameter <= 5.5 :
                    files_to_delete.add(file)
                    print('smallest diameter deleted :', smallest_diameter)
        # Deleting the files that met the criteria
        results.append(files_to_delete)        
        for file in files_to_delete:
            file_to_delete_path = os.path.join(folder_path, file)
            os.remove(file_to_delete_path)
            print(f"Deleted: {file_to_delete_path}")
    handle_lists.write_list_to_file(results,'lesions_too_small.csv')
    return results


data_path = '' 

nifti_folders = extract.extract_folders_path(data_path, type='nifti')

clean_up_small_lesions(nifti_folders)
