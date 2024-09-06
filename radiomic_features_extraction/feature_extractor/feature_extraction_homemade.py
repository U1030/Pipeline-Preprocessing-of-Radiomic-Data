import numpy as np 
import matplotlib.pyplot as plt
import SimpleITK as sitk
import time
from tqdm import tqdm
import pandas as pd 
import compute_glrlm
import calculate_features
import resample_nifti
import preprocessing
import sys
import os
import argparse
sys.path.append("/home/utilisateur/Bureau/CD8_RS_Pipeline")
import utils.explore_folders_to_find_a_type_of_file as find_paths
import utils.extract_information_from_path as extract
import utils.parallele_processing as par


def process_mask_and_image(image_path,mask_path,filter_type,filter_param):
    filter_name = filter_type + '_' + str(filter_param) 
    
    start = time.time()
    glrlm =  compute_glrlm.process_image_mask(image_path,mask_path)
    end = time.time()
    print("execution time compute glrlm :", end - start)

    start = time.time()
    features = calculate_features.calculate_glrlm_features(glrlm, filter_name)  
    end = time.time()
    print("execution time compute features :", end - start)
    
    return features


def find_all_nifti_paths(data_path,id_patient_position_in_path):    
    print("=> Extracting folder path")    
    folder_paths = find_paths.extract_folders_path(data_path,type="nifti")
    data_rows = []    
    for path in folder_paths:        
        patient = extract.extract_patient_id_from_path_when_folder_name_different_from_texture_session(path, id_patient_position_in_path)        
        masks = []
        image_path = None        
        for file in os.listdir(path):
            if file.endswith("nii.gz"):
                if "mask" in file:
                    mask_name = extract.extract_mask_name(file)              
                    masks.append((mask_name, os.path.join(path, file)))                   
                else:
                    image_path = os.path.join(path, file)        
        for mask_name, mask_path in masks:
            data_rows.append({
                "patient_id": patient,
                "roiname": mask_name,
                "image_path": image_path,
                "mask_path": mask_path
            })    
    return pd.DataFrame(data_rows)


def extract_features(row,filter_type,filter_param):
    _, row_data = row
    path_im = row_data['image_path']
    path_mask = row_data['mask_path']    
    if path_im and path_mask:     
        try:            
            feature_vector_df = process_mask_and_image(path_im, path_mask,filter_type,filter_param)                      
            for feature in row_data.index:                
                feature_vector_df[feature] = row_data[feature]   
            print(feature_vector_df)         
            return feature_vector_df
        except Exception as e:
            print(f"Warning: couldn't extract feature for: {path_mask} due to {e}")            
            return row_data.to_frame().T
    else:
        return row_data.to_frame().T
    
def flatten_list(list_of_lists):
  return [item for sublist in list_of_lists for item in sublist]
    
if __name__ == "__main__":
    # Initialiser le parser
    parser = argparse.ArgumentParser(description="Extract features from NIfTI files and save results to CSV.")

    # Ajouter des arguments
    parser.add_argument('--path', type=str, help="Path to the directory containing NIfTI files.")
    parser.add_argument('--index', type=int, default=7, help="Position of patient ID in the path.")
    parser.add_argument('--output_path', type=str, default="extraction_results.csv", help="Path to save the output CSV file.")

    # Parser les arguments
    args = parser.parse_args()

    # Utiliser les arguments
    path = args.path
    id_patient_position_in_path = args.index
    output_csv_path = args.output_path

    df = find_all_nifti_paths(path, id_patient_position_in_path=id_patient_position_in_path)

    print("=> Extracting radiomic features")

    wavelet_types = [ "haar" , "db2", "sym2", "coif1", "bior2.2", "rbio1.1"]
    #filter_types =  ["gaussian","gaussian","gaussian","gaussian","gaussian",   "original",     "wavelet" ]
    #filter_params = [   1.0,        2.0,       3.0,       4.0,      5.0         ,"None",     wavelet_types[3]]
    filter_types =  ["original" ]
    filter_params = ["_"]

    results_per_filter = []
    for filter_type,filter_param in zip(filter_types, filter_params):
        print("=> Filter :", filter_type, filter_param)
        start = time.time()
        results = par.parallelize(df.iterrows(), extract_features,filter_type,filter_param)
        end = time.time()
        results_per_filter.append(results)
    results_flatten = flatten_list(results_per_filter)
    final_df = pd.concat(results_flatten, ignore_index=True)
    print(f"Feature extraction completed in {end - start} seconds.")
    final_df.dropna(how='all', inplace=True)
    final_df.to_csv(os.path.join(output_csv_path,"feature_extraction_results.csv"), index=False)
    print(f"Data saved to {output_csv_path}")



"""
id_patient_position_in_path = 7

nifti_data = find_all_nifti_paths(path, id_patient_position_in_path=id_patient_position_in_path)

wavelet_types = [ "haar" , "db2", "sym2", "coif1", "bior2.2", "rbio1.1"]
#filter_types =  ["gaussian","gaussian","gaussian","gaussian","gaussian",   "original",     "wavelet" ]
#filter_params = [   1.0,        2.0,       3.0,       4.0,      5.0         ,"None",     wavelet_types[3]]
filter_types =  ["original" ]
filter_params = ["_"]

start = time.time()
rows = []
# Iterate through each row in nifti_data
for index, row in nifti_data.iterrows():
    id = row['patient_id']
    roi = row["roiname"]
    image_path = row["image_path"]
    mask_path = row["mask_path"]
    print("=> Processing patient ", id, " and roi ", roi)    
    features = []
    for filter_type, param in zip(filter_types, filter_params):
        extraction_results = process_mask_and_image(image_path, mask_path, filter_type, param)
        features.append(extraction_results)  
    suffix = ""
    if "tum" in mask_path or "gtv" in mask_path or "GTV" in mask_path:        
        suffix = "_tum"
    elif "ring" in mask_path or "ring" in mask_path or "RING" in mask_path:
        suffix = "_ring"  
    # Update keys in the feature dictionaries with the suffix
    updated_features = []
    for feature in features:
        updated_feature = {f"{key}{suffix}": value for key, value in feature.items()}
        updated_features.append(updated_feature)    
    # Flatten updated_features dictionaries into a single dictionary
    feature_dict = {}
    for feature in updated_features:
        feature_dict.update(feature)
    combined_data = {"patient_id": id, "roiname": roi, "image_path": image_path, "mask_path": mask_path}
    combined_data.update(feature_dict) 
    print(combined_data)    
    rows.append(combined_data)
new_nifti_data = pd.DataFrame(rows)
new_nifti_data.to_csv('radiomic_features_extraction_homemade_ACSES.csv', index=False)
print("nifti_data saved to CSV successfully.")
end = time.time()
print("execution time for cohort extraction :", end-start,"sec")
"""