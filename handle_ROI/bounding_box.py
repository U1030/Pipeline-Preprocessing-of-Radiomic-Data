import numpy as np 
import SimpleITK as sitk
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


import sys
#sys.path.append("")

from preprocess_ROI import preprocessing
from handle_ROI import determine_nifti_mask_center_of_mass

def compute_bb(mask_path):
    """
    size of bow depends on mask size
    """    
    mask_im = sitk.ReadImage(mask_path)
    mask_arr = sitk.GetArrayFromImage(mask_im)   

    # Find the indices where the mask value is 1
    indices = np.argwhere(mask_arr == 1)
    
    # Get the minimum and maximum indices for each dimension
    min_indices = indices.min(axis=0)
    max_indices = indices.max(axis=0)

    # Create the bounding box list: [start_x, start_y, start_z, end_x, end_y, end_z]
    bb = np.array([min_indices[2], min_indices[1], min_indices[0], max_indices[2], max_indices[1], max_indices[0]])  

    # Find a slice with the mask
    slice_index = np.unique(indices[:, 0])[0]  # Taking the first slice where the mask is present
    return bb, slice_index


def extract_bounding_box_on_image(image, mask, center, box_size_mm, spacing):
    """
    size of box is fixed , box around center of mass of mask
    """
    # Convert box size from mm to voxels
    box_size_voxels = [int(size / space) for size, space in zip(box_size_mm, spacing)]
    box_half_size = [size // 2 for size in box_size_voxels]

    # Extract the region around the center of mass
    start_index = [max(0, int(center[i] - box_half_size[i])) for i in range(3)]
    end_index = [start_index[i] + box_size_voxels[i] for i in range(3)]
    region = tuple(slice(start, end) for start, end in zip(start_index, end_index))
    
    # Crop the image and mask
    cropped_image = image[region]
    cropped_mask = mask[region]
    return cropped_image, cropped_mask

def compute_bb_fixed_size(image_path, mask_path, box_size_mm, need_preprocessing=False):
    
    if need_preprocessing:
        # output sitk images
        mask_img, image_img = preprocessing.preprocess_image(image_path,mask_path)
    else :
        mask_img = sitk.ReadImage(mask_path)
        image_img = sitk.ReadImage(image_path)

    center_of_mass = determine_nifti_mask_center_of_mass.get_center_of_mask_spicy(mask_img)
    spacing = image_img.GetSpacing()
    index_center_of_mass = [int(coord) for coord in center_of_mass]  

    # Convert box size from mm to voxels
    box_size_voxels = [int(size / space) for size, space in zip(box_size_mm, spacing)]
    box_half_size = [size // 2 for size in box_size_voxels]

    # Extract the region around the center of mass
    start_index = [max(0, int(index_center_of_mass[i] - box_half_size[i])) for i in range(3)]
    end_index = [start_index[i] + box_size_voxels[i] for i in range(3)]
    region = tuple(slice(start, end) for start, end in zip(start_index, end_index))
    return region 



mask_path = ''
image_path = ''

box_size_mm = [40, 40, 20]

bb_fixed = compute_bb_fixed_size(image_path, mask_path, box_size_mm)
bb = compute_bb(mask_path)

