import numpy as np 
import SimpleITK as sitk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.patches as patches

import sys
#sys.path.append("")

import preprocess_ROI.rescaling as rescaling
import preprocess_ROI.resample_nifti as resample_nifti
import preprocess_ROI.spatial_filter as spatial_filter


def preprocess_image(image_path,mask_path, filter_type=None, filter_param=None, rescale_range=(-1000, 3000), desired_bin_width = 10 ):          

   # Resampling / interpolation
    print("=> Resampling mask and image")
    image = resample_nifti.resample_pixel_spacing_image(image_path) 
    mask = resample_nifti.resample_pixel_spacing_binary_mask(mask_path)   
    image_array = sitk.GetArrayFromImage(image)
    mask_array = sitk.GetArrayFromImage(mask)   
   
    print("=> Rounding ")
    # Round intensity values in the image to the closest integer
    rounded_image_array = np.rint(image_array).astype(int)
    # Apply thresholding to the mask: values < 0.5 -> 0, values >= 0.5 -> 1
    rounded_mask_array = (mask_array >= 0.5).astype(int)
    rounded_image = sitk.GetImageFromArray(rounded_image_array)
    rounded_mask = sitk.GetImageFromArray(rounded_mask_array)
    rounded_image.CopyInformation(image)
    rounded_mask.CopyInformation(mask)    

    # Rescaling
    print("=> Rescaling")
    rescaled_mask = rescaling.rescaling_mask(rounded_image,rounded_mask)
    rescaled_image = rescaling.rescaling_image(rounded_image,rescaled_mask)  
    #rescaled_image = rounded_image
    rescaled_image.CopyInformation(rounded_image)
    rescaled_mask.CopyInformation(rounded_mask) 
    rescaled_image_arr = sitk.GetArrayFromImage(rescaled_image)
    rescaled_mask_arr = sitk.GetArrayFromImage(rescaled_mask)
    
    # Filter
    print("=> Spatial filter ", filter_type)
    if filter_type == "gaussian" :
        filtered_image = spatial_filter.apply_gaussian_filter(rescaled_image,filter_param)
    elif filter_type == "wavelet" :
        filtered_image = spatial_filter.apply_wavelet_filter(rescaled_image,filter_param) 
    elif filter_type == "original":
        filtered_image = rescaled_image 
    filtered_image.CopyInformation(image)
    filtered_arr = sitk.GetArrayFromImage(filtered_image)
 
    # Discretizing the image  
    print("=> Intensity discretization")      
    range_start = rescale_range[0]
    range_end = rescale_range[1]
    bins = np.arange(range_start, range_end + desired_bin_width, desired_bin_width)    
    # index based discretization 
    discretized_array = (np.digitize(filtered_arr, bins) -1).astype(np.int32) 
    discretized_image = sitk.GetImageFromArray(discretized_array) 
    discretized_image_arr = sitk.GetArrayFromImage(discretized_image)  
    discretized_image.CopyInformation(image) 
    
    return discretized_image, rescaled_mask

