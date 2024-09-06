import numpy as np
import os
from scipy import ndimage
import SimpleITK as sitk
import time
import matplotlib.pyplot as plt
from tqdm import tqdm

import sys
#sys.path.append("")

from visualization import visualize as vz
from handle_paths import explore_folders_to_find_a_type_of_file as find
from handle_paths import extract_paths


"""

process_patient(patient_folder_path)

process_all_patients(cohort_folder_path)


"""

def ring_mask_name(tumor_path):  
    tumor_path = tumor_path.replace("GTV", "ring")  
    #return tumor_path.replace("mask_", "CREATED_mask_") 
    return tumor_path

def dilatation(img_tumor, dilation_radius_px, visualize_3D):
    dilation_filter = sitk.BinaryDilateImageFilter()
    dilation_filter.SetKernelRadius(dilation_radius_px)
    img_dilated = dilation_filter.Execute(img_tumor)
    arr_dilated = sitk.GetArrayFromImage(img_dilated)
    if visualize_3D:
        vz.visualize_single_mask(arr_dilated, title="dilated")
    return arr_dilated

def erosion(img_tumor, erosion_radius_px, arr_tumor,percentile, visualize_3D):
    
    try :
        erosion_filter = sitk.BinaryErodeImageFilter()
        erosion_filter.SetKernelRadius(erosion_radius_px)
        img_eroded = erosion_filter.Execute(img_tumor)
    except :
        print("Could not erode mask " )
    arr_eroded = sitk.GetArrayFromImage(img_eroded)
    if not np.any(arr_eroded):        
        distance_map = ndimage.distance_transform_edt(arr_tumor)      
        distance_map_flat = distance_map.flatten()
        distance_map_flat_non_zero = distance_map_flat[np.where(distance_map_flat != 0)]
        if np.all(distance_map_flat_non_zero == 1):
            print("really small tumor can't use erosion or euclidian transform : mask full") 
        else :            
            threshold = np.percentile(distance_map_flat[distance_map_flat > 0], percentile)                 
            arr_eroded = distance_map > threshold    
            if visualize_3D :
                vz.visualize_single_mask(arr_eroded, title="Euclidian distance calculated inner tumor")            
    return arr_eroded 

def construct_mask(arr_tumor, arr_eroded, arr_dilated, visualize_3D):    
    ring_mask_inside = np.logical_xor(arr_tumor,arr_eroded)
    if visualize_3D:
        vz.visualize_single_mask(ring_mask_inside,title="inside ring ")
    ring_mask_outside = np.logical_xor(arr_tumor,arr_dilated)
    if visualize_3D :
        vz.visualize_single_mask(ring_mask_outside, title="outside ring")
    arr_ring = np.logical_or( ring_mask_inside, ring_mask_outside) 
    if visualize_3D : 
        vz.visualize_masks(arr_tumor,arr_ring, title="ring constructed and tumor ")    
    arr_ring = arr_ring.astype(np.uint8)  
    return arr_ring

def is_all_zeros(array):  
    flat_array = array.flatten()    
    return np.all(flat_array == 0)

def find_mask_slice(arr_mask):    
    for i in range(arr_mask.shape[0]):
        if np.any(arr_mask[i]):
            return i
    return None

def plot_sitk_image(img_array, slice_index=None):   
    if slice_index is None:
        if img_array.ndim == 3:
            slice_index = img_array.shape[0] // 2
        else:
            slice_index = 0      
    if img_array.ndim == 3:
        img_slice = img_array[slice_index, :, :]
    else:
        img_slice = img_array    
    plt.imshow(img_slice, cmap='gray')
    plt.title(f'Image Slice {slice_index}')
    plt.axis('off')
    plt.show()

def save_mask(arr_ring, tumor_path):
    # check if constructed mask is empty 
    if is_all_zeros(arr_ring):
        print("the constructed mask is empty")
    slice_index = find_mask_slice(arr_ring)
    #plot_sitk_image(arr_ring,slice_index)
    # Read the original tumor mask to get origin and spacing information
    tumor = sitk.ReadImage(tumor_path)
    # Create a SimpleITK image from the mask array
    img_ring = sitk.GetImageFromArray(arr_ring.astype(np.uint8))
    # Copy the origin and spacing information from the original tumor mask
    img_ring.SetOrigin(tumor.GetOrigin())
    img_ring.SetSpacing(tumor.GetSpacing())
    # Write the mask image to file
    new_mask_ring_filename = ring_mask_name(tumor_path)
    # Check if the file already exists
    if os.path.exists(new_mask_ring_filename):
        # Delete the file if it exists
        os.remove(new_mask_ring_filename)
    sitk.WriteImage(img_ring, new_mask_ring_filename)
    print("created mask saved as : ",new_mask_ring_filename)
    return

def construct_ring_mask(tumor_path, percentile=90, visualize_3D=False):
    start = time.time()
    img_tumor = sitk.ReadImage(tumor_path)
    arr_tumor = sitk.GetArrayFromImage(img_tumor)
    # Convert mm to pixel spacing for erosion/dilation
    # not necessary since resampled to 1*1*1mm³ 
    image_spacing = img_tumor.GetSpacing()
    if image_spacing == (1.0,1.0,1.0):   
        erosion_radius_px = [2,2,2]
        dilation_radius_px = [2,2,2]
        start1 = time.time()
        arr_eroded = erosion(img_tumor,erosion_radius_px,arr_tumor,percentile,visualize_3D=visualize_3D)
        end1 = time.time()
        print('Erosion : %s sec' % (end1 - start1)) 
        start2 = time.time()
        arr_dilated = dilatation(img_tumor, dilation_radius_px, visualize_3D=False)
        end2 = time.time()
        print('Dilation : %s sec' % (end2 - start2))
        start3 = time.time()
        arr_ring = construct_mask(arr_tumor,arr_eroded,arr_dilated, visualize_3D=visualize_3D)  
        end3 = time.time()
        print('Construction : %s sec' % (end3 - start3))      
        save_mask(arr_ring, tumor_path)                
    else : 
        print("ERROR file hasn't been resampled", tumor_path)
    end = time.time()
    #print('Mask constructed in : %s sec' % (end - start)) 
    return

def find_missing_nifti_ring_files(folder_path,tumor_accronym):
    results = []
    files_in_folder = {file.lower(): file for file in os.listdir(folder_path)}        
    for file_name in os.listdir(folder_path):
        file_name_lower = file_name.lower()
        file_path = os.path.join(folder_path, file_name)           
        if tumor_accronym in file_name_lower:               
            search_name = file_name_lower.replace(tumor_accronym, 'ring')                
        else:
            continue            
        # Search for the corresponding file in the folder
        if search_name in files_in_folder:
            continue          
        else:
            results.append(file_path)
    return results

def process_patient(patient_path,tumor_accronym):    
    folders = find.extract_folders_path(patient_path,type='nifti')
    for folder_path in folders :
        print(folder_path)
        mask_tumor_files= find_missing_nifti_ring_files(folder_path,tumor_accronym=tumor_accronym)   
        for tumor in tqdm(mask_tumor_files):    
                print('tumor :', tumor)        
                tumor_path = os.path.join(folder_path, tumor)
                construct_ring_mask(tumor_path, percentile=90, visualize_3D= False)
    return

def process_all_patients(path, tumor_accronym,depth = 2, direct =True):
    if direct :
        subfolders = [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
        patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
        patients_paths = extract_paths.get_folders_at_depth(path, depth)
    for patient_path in patients_paths:     
        process_patient(patient_path,tumor_accronym=tumor_accronym)


comand = 'multiple_folders'
path = '' 

# optional : if in your architecture the path doesn't contain directly patient folders but for exemple folder per center then patient folder 
# you need to put direct to False and input the depth at which patient folders are 

depth = ""
direct = True
#tumor_accronym = 'gtv' or 'tum'

if comand == 'multiple_folders':
  process_all_patients(path,tumor_accronym = 'gtv',depth=depth,direct=direct)
elif comand  == "folder":
  process_patient(path, tumor_accronym='gtv')