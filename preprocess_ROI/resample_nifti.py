import SimpleITK as sitk
import numpy as np
import os
from tqdm import tqdm

import sys
#sys.path.append("")

from visualization import visualize as vz
from handle_paths import explore_folders_to_find_a_type_of_file as find
from handle_paths import find_matching_ring_and_tumor_nifti_files as match
from handle_paths import extract_paths

def new_file_path_resampling(original_file_path):    
    path = original_file_path.split(".nii.gz")
    extansion = ".nii.gz"
    file = path[0]      
    new_filename = file + "_RESAMPLED"    
    resampled_path =  new_filename + extansion
    return resampled_path


def resample_pixel_spacing_image(file_path):
    print("=> Resampling")
    new_spacing = [1, 1, 1]
    pad_distance = 10  # Extra padding for large sigma valued LoG filtered images
    image = sitk.ReadImage(file_path)
    
    original_spacing = image.GetSpacing()
    pad_filter = sitk.ConstantPadImageFilter()
    pad_filter.SetPadLowerBound([pad_distance] * 3)
    pad_filter.SetPadUpperBound([pad_distance] * 3)
    pad_filter.SetConstant(0)
    padded_image = pad_filter.Execute(image)    
    resample = sitk.ResampleImageFilter()
    resample.SetInterpolator(sitk.sitkBSpline)
    resample.SetDefaultPixelValue(0)
    resample.SetOutputSpacing(new_spacing)
    resample.SetOutputOrigin(padded_image.GetOrigin())
    resample.SetOutputDirection(padded_image.GetDirection())    
    padded_size = padded_image.GetSize()
    size = [
        int(np.round(padded_size[0] * (original_spacing[0] / new_spacing[0]))),
        int(np.round(padded_size[1] * (original_spacing[1] / new_spacing[1]))),
        int(np.round(padded_size[2] * (original_spacing[2] / new_spacing[2])))
    ]
    resample.SetSize(size)
    resampled_image = resample.Execute(padded_image) 
    output_path = new_file_path_resampling(file_path)
    sitk.WriteImage(resampled_image,output_path)     
    return resampled_image


def resample_pixel_spacing_binary_mask(file_path):
    print("=> Resampling")
    new_spacing = [1, 1, 1]
    pad_distance = 10  # Extra padding for large sigma valued LoG filtered images
    image = sitk.ReadImage(file_path)
    
    original_spacing = image.GetSpacing()
    pad_filter = sitk.ConstantPadImageFilter()
    pad_filter.SetPadLowerBound([pad_distance] * 3)
    pad_filter.SetPadUpperBound([pad_distance] * 3)
    pad_filter.SetConstant(0)
    padded_image = pad_filter.Execute(image)    
    resample = sitk.ResampleImageFilter()
    resample.SetInterpolator(sitk.sitkNearestNeighbor)
    resample.SetDefaultPixelValue(0)
    resample.SetOutputSpacing(new_spacing)
    resample.SetOutputOrigin(padded_image.GetOrigin())
    resample.SetOutputDirection(padded_image.GetDirection())    
    padded_size = padded_image.GetSize()
    size = [
        int(np.round(padded_size[0] * (original_spacing[0] / new_spacing[0]))),
        int(np.round(padded_size[1] * (original_spacing[1] / new_spacing[1]))),
        int(np.round(padded_size[2] * (original_spacing[2] / new_spacing[2])))
    ]
    resample.SetSize(size)
    resampled_image = resample.Execute(padded_image) 
    output_path = new_file_path_resampling(file_path)
    sitk.WriteImage(resampled_image,output_path)   
    return resampled_image



def resample_patient(patient_path):         
    nifti_folder =  find.extract_folders_path(patient_path,type='nifti')
   
    for folder_path in nifti_folder :
        image = [file for file in os.listdir(folder_path) if 'mask' not in file] 
        image_path = os.path.join(folder_path,image[0])
        resample_pixel_spacing_image(image_path)
        mask_tumor_files, mask_ring_files = match.find_matching_nifti_files(folder_path)    
        for tumor, ring in zip(mask_tumor_files, mask_ring_files): 
            tumor_path = os.path.join(folder_path, tumor)                
            resample_pixel_spacing_binary_mask(tumor_path)           
            ring_path = os.path.join(folder_path, ring)                   
            resample_pixel_spacing_binary_mask(ring_path)                                      
    return

def resample_all_patients(path, depth = 2, direct =True):
    if direct :
        subfolders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
        patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
        patients_paths = extract_paths.get_folders_at_depth(path, depth)
    for patient_path in tqdm(patients_paths):     
        resample_patient(patient_path)


path = '' 

resample_all_patients(path)