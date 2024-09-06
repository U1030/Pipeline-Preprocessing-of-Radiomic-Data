import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import SimpleITK as sitk


def visualize_single_mask(mask, title="Mask Visualization"):
    if mask.ndim != 3 :
        raise ValueError("Mask array must be 3D for visualization.")
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')   
    mask_voxels = np.where(mask == 1)        
    ax.scatter(mask_voxels[0], mask_voxels[1], mask_voxels[2], c='red', marker='s', label=' Mask')     
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title(title)
    ax.legend()
    plt.show()
    return


def visualize_masks(mask_tumor, mask_ring, title="Masks Visualization"):
    if mask_tumor.ndim != 3 or mask_ring.ndim != 3:
        raise ValueError("Mask arrays must be 3D for visualization.")
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')   
    tumor_voxels = np.where(mask_tumor == 1)  
    ring_voxels = np.where(mask_ring == 1)    
    ax.scatter(tumor_voxels[0], tumor_voxels[1], tumor_voxels[2], c='red', marker='s', label='Tumor Mask')  
    ax.scatter(ring_voxels[0], ring_voxels[1], ring_voxels[2], c='blue', marker='o', label='Ring Mask')
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title(title)
    ax.legend()
    plt.show()
    return


def read_and_visualize_single_mask(path):
    itk_image = sitk.ReadImage(path)
    array = sitk.GetArrayFromImage(itk_image)
    size_mask = itk_image.GetSize()
    pixel_mask = itk_image.GetSpacing()
    print("size and pixel spacing", size_mask, pixel_mask) 
    visualize_single_mask(array, title=path)
    return 


def plot_with_overlay(image_arr, mask_arr, slice_index, title='Overlay'):
    plt.imshow(image_arr[slice_index], cmap='gray')
    plt.imshow(mask_arr[slice_index], cmap='jet', alpha=0.5)
    plt.title(title)
    plt.colorbar()
    plt.show()
