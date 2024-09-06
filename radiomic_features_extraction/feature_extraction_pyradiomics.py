import radiomics.featureextractor
import pandas as pd
import os
import time
import argparse

import sys
#sys.path.append("")


import handle_paths.explore_folders_to_find_a_type_of_file as find_paths 
import handle_paths.extract_information_from_path as get_from_path
import parralelize.parallelize_v2 as par 
import handle_ROI.check_voxel_intensities as check_voxel

# Parameters
# Define the parameters with specific features
params = {
    'imageType': {
        'Original': {},
        'LoG': {
            'sigma': [1.0, 2.0, 3.0, 4.0, 5.0]
        },
        'Wavelet': {}
    },
    'featureClass': {        
        'glrlm': [
            'ShortRunHighGrayLevelEmphasis',  #SRHGLE
            'LowGrayLevelRunEmphasis', #LGLRE
            'ShortRunLowGrayLevelEmphasis', #SRLGLE
            'LongRunLowGrayLevelEmphasis' #LRLGLE
        ],       
    },
    'setting': {
        'interpolator': 'sitkBSpline',
        'resampledPixelSpacing': [1, 1, 1],
        'padDistance': 10,
        'binWidth': 10,
        'resegmentRange': [-1000, 3000],
        'voxelArrayShift': 1000
    }
}


def process_mask_and_image(image_filepath, mask_filepath):        
    extractor = radiomics.featureextractor.RadiomicsFeatureExtractor(params)       
    label = 1  # Example label, change as needed
    label_channel = None  # For single-channel masks      
    result_extraction = pd.Series(extractor.execute(image_filepath, mask_filepath, label=label, label_channel=label_channel))      
    feature_vector = pd.DataFrame([result_extraction])            
    return feature_vector


def find_all_nifti_paths(data_path,id_patient_position_in_path):    
    print("=> Extracting folder path")    
    folder_paths = find_paths.extract_folders_path(data_path,type="nifti")
    data_rows = []    
    for path in folder_paths:        
        patient = get_from_path.extract_patient_id_from_path_when_folder_name_different_from_texture_session(path, id_patient_position_in_path)        
        masks = []
        image_path = None        
        for file in os.listdir(path):
            if file.endswith("nii.gz"):
                if "mask" in file:
                    mask_name = get_from_path.extract_mask_name(file)              
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


def extract_features(row):
    _, row_data = row
    path_im = row_data['image_path']
    path_mask = row_data['mask_path']    
    if path_im and path_mask:     
        try:            
            feature_vector_df = process_mask_and_image(path_im, path_mask)                      
            for feature in row_data.index:                
                feature_vector_df[feature] = row_data[feature]   
            print(feature_vector_df)         
            return feature_vector_df
        except Exception as e:
            print(f"Warning: couldn't extract feature for: {path_mask} due to {e}")
            check_voxel.get_intensity_range(path_im)
            return row_data.to_frame().T
    else:
        return row_data.to_frame().T



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

    start = time.time()
    results = par.parallelize(df.iterrows(), extract_features)
    end = time.time()
    
    final_df = pd.concat(results, ignore_index=True)
    print(f"Feature extraction completed in {end - start} seconds.")
    final_df.dropna(how='all', inplace=True)
    final_df.to_csv(os.path.join(output_csv_path,"feature_extraction_results.csv"), index=False)
    print(f"Data saved to {output_csv_path}")

