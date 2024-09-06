import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import distance

import sys
#sys.path.append("")

from handle_ROI import determine_nifti_mask_boundary_points as bp
from handle_ROI import determine_nifti_mask_center_of_mass as com


def calculate_smallest_diameter_and_points(mask_path):
    img_mask = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayFromImage(img_mask)
    
    center_of_mass = com.calculate_center_of_mass(mask_path)
    boundary_points = bp.calculate_boundary_points(mask_path)
    
    spacing = img_mask.GetSpacing()
    boundary_points_physical = boundary_points * spacing
    
    distances = distance.cdist([center_of_mass * spacing], boundary_points_physical)[0]
    
    smallest_radius = np.min(distances)
    smallest_diameter = 2 * smallest_radius
    closest_boundary_point = boundary_points[np.argmin(distances)]
    
    #print("smallest diameter :", smallest_diameter)

    return center_of_mass, boundary_points, closest_boundary_point, smallest_radius, smallest_diameter

def visualize_mask_and_boundaries(mask_path):
    img_mask = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayFromImage(img_mask)

    center_of_mass, boundary_points, closest_boundary_point, smallest_radius, smallest_diameter = calculate_smallest_diameter_and_points(mask_path)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    mask_voxels = np.where(arr_mask == 1)
    ax.scatter(mask_voxels[2], mask_voxels[1], mask_voxels[0], c='red', marker='s', label='Mask')

    ax.scatter(boundary_points[:, 2], boundary_points[:, 1], boundary_points[:, 0], c='blue', marker='o', label='Boundary Points')

    ax.plot([center_of_mass[2]], [center_of_mass[1]], [center_of_mass[0]], marker='x', color='green', markersize=10, label='Center of Mass')

    ax.plot([center_of_mass[2], closest_boundary_point[2]], 
            [center_of_mass[1], closest_boundary_point[1]], 
            [center_of_mass[0], closest_boundary_point[0]], 
            color='purple', linestyle='--', label=f'Smallest radius: {smallest_radius:.2f}')

    ax.set_xlabel('Z-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('X-axis')
    ax.set_title(f"smallest diameter :{smallest_diameter:.2f}")
    ax.legend()

    plt.show()
