import numpy as np
from scipy import ndimage
import SimpleITK as sitk
import time
import matplotlib.pyplot as plt


import sys
#sys.path.append("")


from visualization import find_slices_where_nifti_mask_is as find



def get_center_of_mask_spicy(input_image):
    
    # Check if the input is a string (file path) or a SimpleITK image
    if isinstance(input_image, str):
        img_mask = sitk.ReadImage(input_image)
    else:
        img_mask = input_image
    
    # Convert the SimpleITK image to a numpy array
    arr_mask = sitk.GetArrayFromImage(img_mask)
    
    # Calculate the center of mass
    center = ndimage.measurements.center_of_mass(arr_mask)    
   
    return center

def calculate_center_of_mass(mask_path):
    start = time.time()
    img_mask = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayFromImage(img_mask)
    indices = np.argwhere(arr_mask)
    center_of_mass = np.mean(indices, axis=0) 
    end = time.time()
    #print("execution time to calculate center of mass :", end - start)  
    return center_of_mass


def plot_mask_and_center(mask_path):
    # Read the mask image
    img_mask = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayFromImage(img_mask)  
      
    center_of_mass = calculate_center_of_mass(mask_path)    
    # Convert center of mass to integer indices
    center_of_mass = tuple(map(int, center_of_mass))
    
    # Find the relevant slices
    center_slice_axial, center_slice_coronal, center_slice_sagittal = find.find_mask_slice(mask_path)

    # Plot the relevant slice of each dimension
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    # Axial view (slice where the mask is present)
    axes[0].imshow(arr_mask[center_slice_axial, :, :], cmap='gray')
    axes[0].scatter(center_of_mass[2], center_of_mass[1], color='red', marker='x')
    axes[0].set_title('Axial view')
    axes[0].set_xlabel('X-axis')
    axes[0].set_ylabel('Y-axis')
    
    # Coronal view (slice where the mask is present)
    axes[1].imshow(arr_mask[:, center_slice_coronal, :], cmap='gray')
    axes[1].scatter(center_of_mass[2], center_of_mass[0], color='red', marker='x')
    axes[1].set_title('Coronal view')
    axes[1].set_xlabel('X-axis')
    axes[1].set_ylabel('Z-axis')
    
    # Sagittal view (slice where the mask is present)
    axes[2].imshow(arr_mask[:, :, center_slice_sagittal], cmap='gray')
    axes[2].scatter(center_of_mass[1], center_of_mass[0], color='red', marker='x')
    axes[2].set_title('Sagittal view')
    axes[2].set_xlabel('Y-axis')
    axes[2].set_ylabel('Z-axis')
    
    plt.show()

