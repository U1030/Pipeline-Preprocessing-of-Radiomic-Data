import os
import numpy as np
import SimpleITK as sitk
import pandas as pd
from tqdm import tqdm

import sys
#sys.path.append("")

from conversion import export_to_nifti_solution_artefacts as convert
from handle_paths import explore_folders_to_find_a_type_of_file as find_paths

"""
Check if intensity range of nifti corresponds to the original intensity range in the corresponding dicom
If not file is deleted and dicom is translated into nifti again with correct intensity

"""

def get_intensity_range(path_image):
    image = sitk.ReadImage(path_image)
    image_array = sitk.GetArrayFromImage(image)
    min_intensity = np.min(image_array)
    max_intensity = np.max(image_array)    
    return [min_intensity,max_intensity]

def find_all_nifti_paths(data_path):
    print("=> Extracting folder path")
    folder_paths = find_paths.extract_folders_path(data_path,type="nifti")
    data_rows = []    
    for path in tqdm(folder_paths, total=len(folder_paths), desc='Processing nifti files'):     
        image_path = None        
        for file in os.listdir(path):
            if file.endswith("nii.gz"):
                if "mask" not in file:
                    image_path = os.path.join(path, file)         
        if image_path :
            range_intensities = get_intensity_range(image_path)           
            max_value = range_intensities[1]
            min_value = range_intensities[0]
            data_rows.append({                        
                "image_path": image_path,
                "max_nifti": max_value,
                "min_nifti" : min_value
            
            })    
    return pd.DataFrame(data_rows)

def get_intensity_range_dicom(image_data):   
    min_intensity = np.min(image_data)
    max_intensity = np.max(image_data)    
    return min_intensity, max_intensity

def load_dicom_series(directory):  
    try :   
        reader = sitk.ImageSeriesReader()
        dicom_series = reader.GetGDCMSeriesFileNames(directory)
        reader.SetFileNames(dicom_series)
        image = reader.Execute()       
        image_data = sitk.GetArrayFromImage(image)
        min_value, max_value = get_intensity_range_dicom(image_data)         
        return min_value, max_value 
    except Exception as e: 
        if "RTSTRUCT" not in directory :
            print("error :",e)
            print(directory)
        return None    

def remove_last_n_elements_from_path(path, n):
    path = path.strip()  
    path_parts = path.split(os.sep)    
    if path_parts[0] == '':
        path_parts = path_parts[1:]    
    new_path_parts = path_parts[:-n]
    new_path = os.sep + os.sep.join(new_path_parts) if path.startswith(os.sep) else os.sep.join(new_path_parts)    
    return new_path

def compute_intensity_range(data_path):
    data_nifti = find_all_nifti_paths(data_path)
    for index,data in tqdm(data_nifti.iterrows(), total=len(data_nifti), desc="Processing dicom files"):
        image_path = data["image_path"]
        folder_path = remove_last_n_elements_from_path(image_path,n=2)
        dicom_path = find_paths.extract_folders_path(folder_path, type="DICOM")    
        if dicom_path :
            for path in dicom_path:
                if not os.path.exists(path) :
                    print('the path doesn t exists', path)
                try :
                    min_value,max_value = load_dicom_series(path)                
                    data_nifti.at[index, "max_dicom"] = max_value
                    data_nifti.at[index, "min_dicom"] = min_value
                    data_nifti.at[index, "dicom_path"] = path
                except :                
                    continue
    return data_nifti
   
def get_incorrect_nifti_path(df):
    # Filter rows where max_nifti or min_nifti differs from max_dicom or min_dicom
    filtered_df = df[
        (df['max_nifti'] != df['max_dicom']) |
        (df['min_nifti'] != df['min_dicom'])
    ][['image_path', 'dicom_path']]  # Select image_path and dicom_path columns    
    # Convert filtered DataFrame to a list of tuples
    incorrect_paths = list(filtered_df.itertuples(index=False, name=None))    
    return incorrect_paths

def delete_file(path):    
    try:
        os.remove(path)
        print(f"Deleted file: {path}")
    except OSError as e:
        print(f"Error deleting file: {path} - {e}")

def main(data_path):
    df = compute_intensity_range(data_path)
    print(df)
    list_path = get_incorrect_nifti_path(df)
    print("nifti with intesity range that don't correspond to dicom intensity range :",list_path)
    for path in list_path :
        nifti_path,dicom_path = path
        delete_file(nifti_path)
        nifti_folder_path = remove_last_n_elements_from_path(nifti_path,n=1)
        image = convert.GetImage(dicom_path,nifti_folder_path)
    return


