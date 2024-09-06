import SimpleITK as sitk
import numpy as np 

def rescaling_mask(image, mask, lower_bound=-1000, upper_bound=3000):
    # Convert SimpleITK images to numpy arrays
    image_array = sitk.GetArrayFromImage(image)
    mask_array = sitk.GetArrayFromImage(mask)    
    # Update mask based on intensity values in image
    mask_array[(mask_array == 1) & ((image_array < lower_bound) | (image_array > upper_bound))] = 0    
    # Convert numpy arrays back to SimpleITK images
    updated_mask = sitk.GetImageFromArray(mask_array)    
    # Copy the metadata from the original mask
    updated_mask.CopyInformation(mask)    
    return updated_mask

def rescaling_image(image, mask, lower_bound=-1000, upper_bound=3000):
    # Convert SimpleITK images to numpy arrays
    image_array = sitk.GetArrayFromImage(image).astype(np.float32) 
    mask_array = sitk.GetArrayFromImage(mask)    
    # Set image values to NaN where mask is 0
    #image_array[mask_array == 0] = 0
    image_array[(image_array < lower_bound) | (image_array > upper_bound)] = 0
    # Convert numpy array back to SimpleITK image
    updated_image = sitk.GetImageFromArray(image_array)    
    # Copy the metadata from the original image
    updated_image.CopyInformation(image)    
    return updated_image