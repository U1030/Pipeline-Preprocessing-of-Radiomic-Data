import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance
import time 

import sys
#sys.path.append("")


from visualization import find_slices_where_nifti_mask_is as find


def calculate_boundary_points(mask_path):
    start = time.time()
    mask_image = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayFromImage(mask_image)
    eroded_mask_image = sitk.BinaryErode(mask_image, [1, 1, 1])
    eroded_mask = sitk.GetArrayFromImage(eroded_mask_image)
    boundary_mask = arr_mask - eroded_mask
    boundary_points = np.argwhere(boundary_mask)
    end = time.time()
    #print("execution time to calculate boundary points :", end-start)
    return boundary_points


def plot_mask_and_boundary(mask_path, zoom_factor=1.2):
    # Read the mask image
    img_mask = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayFromImage(img_mask)

    # Find the relevant slices
    center_slice_axial, center_slice_coronal, center_slice_sagittal = find.find_mask_slice(mask_path)
    
    # Calculate the boundary points
    boundary_points = calculate_boundary_points(mask_path)

    # Create 3D scatter plot
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Plot mask voxels
    mask_voxels = np.where(arr_mask == 1)
    ax.scatter(mask_voxels[2], mask_voxels[1], mask_voxels[0], c='red', marker='s', label='Mask')

    # Plot boundary points
    ax.scatter(boundary_points[:, 2], boundary_points[:, 1], boundary_points[:, 0], c='blue', marker='o', label='Boundary Points')

    # Set labels and title
    ax.set_xlabel('Z-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('X-axis')
    ax.set_title("boundaries of mask")
    ax.legend()

    plt.show()

