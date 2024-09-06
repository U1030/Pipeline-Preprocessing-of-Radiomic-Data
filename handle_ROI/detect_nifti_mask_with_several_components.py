from skimage.measure import label
import SimpleITK as sitk
import os
import numpy as np
import re
from tqdm import tqdm

import sys
#sys.path.append("")

from handle_paths import find_matching_ring_and_tumor_nifti_files as find_match_nifties
from handle_paths import explore_folders_to_find_a_type_of_file as find
from handle_paths import extract_paths
from utils import handle_lists
from visualization import visualize


def process_patient(patient_path):      
    several_components = [] 
    folders = find.extract_folders_path(patient_path, type='nifti')
    for folder_path in folders :  
        print(folder_path)             
        mask_tumor_files = find_match_nifties.find_GTV_files(folder_path)    
        for tumor in mask_tumor_files:
                if tumor != "":            
                    tumor_path = os.path.join(folder_path, tumor)                                                
                    img_tumor = sitk.ReadImage(tumor_path)                        
                    tumor_arr = sitk.GetArrayFromImage(img_tumor)  
                    labelled_img_array, num_components_tumor = label(tumor_arr, return_num=True)  
                    if num_components_tumor > 1:
                        several_components.append(tumor_path) 
                        print(tumor_path)
                        visualize.read_and_visualize_single_mask(tumor_path)  
    return several_components

def extract_mask_name(mask_path):
    # Find the sub-path starting with "mask"
    sub_path = ""
    components = mask_path.split(os.path.sep)
    for idx, component in enumerate(components):
        if component.startswith("mask"):
            sub_path = os.path.sep.join(components[idx:])
            break    
    # Extract mask name from the sub-path
    mask = os.path.basename(sub_path)
    mask_name = "_".join(mask.split(sep="_")[:6])
    return mask_name

def process_patient_new_version(patient_path):      
    several_components = [] 
    folders = find.extract_folders_path(patient_path,type='nifti')
    
    for folder_path in folders:  
        print(folder_path)             
        mask_tumor_files = find_match_nifties.find_GTV_files(folder_path)    
        
        for tumor in mask_tumor_files:
            if tumor != "":            
                tumor_path = os.path.join(folder_path, tumor)                                                
                img_tumor = sitk.ReadImage(tumor_path)                        
                tumor_arr = sitk.GetArrayFromImage(img_tumor)  
                
                # Label connected components in the mask
                labelled_img_array, num_components_tumor = label(tumor_arr, return_num=True)
                
                if num_components_tumor > 1:
                    several_components.append(tumor_path)
                    print(f"{tumor_path} has {num_components_tumor} components.")
                    
                    # Create and save individual masks for each component
                    for component_num in range(1, num_components_tumor + 1):
                        # Create a binary mask for the current component
                        component_mask = (labelled_img_array == component_num).astype(np.uint8)
                        
                        # Convert back to SimpleITK Image
                        component_img = sitk.GetImageFromArray(component_mask)
                        component_img.CopyInformation(img_tumor)  # Preserve the original image metadata
                        
                        # Create the new filename
                        base_name = tumor.replace('.nii.gz', '')
                        new_file_name = f"{base_name}_component_{component_num}.nii.gz"
                        new_file_path = os.path.join(folder_path, new_file_name)
                        
                        # Save the new NIfTI file
                        sitk.WriteImage(component_img, new_file_path)
                        print(f"Saved: {new_file_path}")
                        
                        # Optionally visualize
                        #visualize.read_and_visualize_single_mask(new_file_path)
    
    return several_components


def clean_up_nifti_folders(nifti_folders):
    for folder_path in nifti_folders:
        files_to_delete = set()
        all_files = os.listdir(folder_path)
        file_set = set(all_files)

        for file in all_files:
            file_path = os.path.join(folder_path, file)

            # Extract the base name without .nii.gz extension
            if file.endswith('.nii.gz'):
                base_name = file[:-7]  # Removes '.nii.gz'
            else:
                base_name, _ = os.path.splitext(file)

            # Regular expression to match any file with the format <base_name>_component_<integer>.nii.gz
            component_pattern = re.compile(rf"{re.escape(base_name)}_component_\d+\.nii\.gz")
            
            # Check if any complement file exists
            if any(component_pattern.fullmatch(f) for f in file_set):
                files_to_delete.add(file)
                continue            

        # Deleting the files that met the criteria
        for file in files_to_delete:
            file_to_delete_path = os.path.join(folder_path, file)
            os.remove(file_to_delete_path)
            print(f"Deleted: {file_to_delete_path}")


def process_all_patients(path, path_output,depth = 2, direct =True):    
    if direct :
      subfolders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
      patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
      patients_paths = extract_paths.get_folders_at_depth(path, depth) 
    results = []
   
    for path in tqdm(patients_paths, desc="Processing Patients"):
        res = process_patient_new_version(path) 
        res_processed = [extract_mask_name(path) for path in res]         
        if res_processed != []:
            results.append(res_processed)
    filename = os.path.join(path_output, "masks with several components.txt")
    handle_lists.write_list_to_file(handle_lists.flatten_list(results),filename)
    nifti_folders = find.extract_folders_path(path, type='nifti')
    clean_up_nifti_folders(nifti_folders)
    return filename


path = '' 
output_path = '' 

process_all_patients(path, output_path)


nifti_folders = find.extract_folders_path(path, type='nifti')
clean_up_nifti_folders(nifti_folders)