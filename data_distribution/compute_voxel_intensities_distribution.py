import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import SimpleITK as sitk

import sys
#sys.path.append("")

import handle_paths.explore_folders_to_find_a_type_of_file as find_paths

def get_intensity_range(path_image):
    image = sitk.ReadImage(path_image)
    image_array = sitk.GetArrayFromImage(image)
    min_intensity = np.min(image_array)
    max_intensity = np.max(image_array)    
    return [min_intensity,max_intensity]


def find_all_nifti_paths(data_path):
    print("=> Extracting folder path")
    folder_paths = find_paths.extract_folders_path(data_path,type='nifti')
    data_rows = []    
    for path in folder_paths:     
        image_path = None        
        for file in os.listdir(path):
            if file.endswith("nii.gz"):
                if "mask" not in file:
                    image_path = os.path.join(path, file)                  
        
        if image_path :
            range_intensities = get_intensity_range(image_path)
            print(range_intensities)
            data_rows.append({                        
                "image_path": image_path,
                "range": range_intensities
            
            })    
    return pd.DataFrame(data_rows)

def plot_intensity_distribution(min_array, max_array, title):
    # Plot the intensity distribution of the filtered image
    plt.figure(figsize=(10, 6))
    plt.hist(min_array, bins=30, color='blue', alpha=0.5, label='Min Intensity', density=True)
    plt.hist(max_array, bins=30, color='red', alpha=0.5, label='Max Intensity', density=True)
    plt.title(title)
    plt.xlabel('Intensity')
    plt.ylabel('Normalized Frequency')
    plt.legend()
    plt.show()

def main(path):   
    df = find_all_nifti_paths(path)
    min_values = []
    max_values = []
    for value in df['range']:
        min = value[0]
        max = value[1]
        min_values.append(min)
        max_values.append(max)
    plot_intensity_distribution(min_values,max_values,"voxel intensity range distribution")