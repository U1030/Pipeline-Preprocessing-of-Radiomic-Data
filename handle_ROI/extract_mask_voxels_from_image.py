import SimpleITK as sitk


def extract_masked_voxels(image, mask):
    """
    Reads a NIfTI image and its corresponding mask, and extracts the 3D array of voxels where the mask == 1.
    
    Parameters:
        image_file (str): Path to the NIfTI image file.
        mask_file (str): Path to the NIfTI mask file.
    
    Returns:
        np.ndarray: 3D array of the masked voxels from the image.
    """    
    # Get the data from the image and mask
    image_data = sitk.GetArrayFromImage(image)
    mask_data = sitk.GetArrayFromImage(mask)  
    # Ensure the mask is binary (i.e., contains only 0s and 1s)
    mask_data = mask_data > 0    
    # Apply the mask to the image data
    masked_image_data = image_data * mask_data  
    image_roi = sitk.GetImageFromArray(masked_image_data)  
    return image_roi
   

