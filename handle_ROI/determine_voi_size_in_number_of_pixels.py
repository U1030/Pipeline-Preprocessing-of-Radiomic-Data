import nibabel as nib
import numpy as np
import os
from tqdm import tqdm
import pandas as pd

import sys
#sys.path.append("")

from handle_paths import explore_folders_to_find_a_type_of_file as find
from handle_paths import extract_information_from_path as extract



def get_size_of_roi(nifti_path):
    nifti_data = nib.load(nifti_path)   
    mask_data = nifti_data.get_fdata()    
    voxel_count = np.sum(mask_data == 1)      
    return voxel_count

def extract_and_modify_filename(file_path):   
    filename_with_extension = os.path.basename(file_path)      
    if filename_with_extension.endswith('.nii.gz'):
        filename_without_extension = filename_with_extension[:-7]  
    else:
        filename_without_extension = filename_with_extension    
    return filename_without_extension

def extract_nifti_data(cohort_path):
    nifti_paths = find.extract_folders_path(data_path=cohort_path, type="nifti")
    nifti_infos = []
    for path in tqdm(nifti_paths, total=(len(nifti_paths))):        
        for file in os.listdir(path):
            filepath = os.path.join(path,file)
            if 'mask' in filepath:     
                size = get_size_of_roi(filepath)          
                nifti_infos.append({"mask_path":filepath,"volume":size})
    nifti_df = pd.DataFrame(nifti_infos)   
    nifti_df['roiname'] = nifti_df['mask_path'].apply(lambda x : extract_and_modify_filename(x))
    nifti_df_cleaned = extract.extract_metadata_with_voi_type(nifti_df)
    nifti_df_cleaned.to_csv("lesions_volume_in_voxels.csv")
    return nifti_df_cleaned





