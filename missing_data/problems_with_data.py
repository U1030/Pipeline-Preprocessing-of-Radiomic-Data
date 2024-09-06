import pydicom
import os
import pandas as pd
import SimpleITK as sitk
import re
from radiomics import featureextractor
from tqdm import tqdm
from collections import Counter
from unidecode import unidecode
from collections import defaultdict

import sys
#sys.path.append("")

import handle_paths.explore_folders_to_find_a_type_of_file as find_paths
import handle_paths.extract_information_from_path as extract
import utils.handle_lists as handle_list



def extract_dicom_info(dicom_paths):
    infos_ct = []
    infos_rtstruct = []

    dicom_path_unique = set(dicom_paths)
    print("check dicom paths have no duplicates :", len(dicom_paths)==len(dicom_path_unique))

    for path in dicom_paths:
        files = [file for file in os.listdir(path) if file.endswith(".dcm")]
        if not files:
            continue
        # Pick the first file from the list (one file per series)
        file = files[0]
        filepath = os.path.join(path, file)
        ds = pydicom.dcmread(filepath)
        modality = ds.Modality
        patient_id = ds.PatientID

        if modality == "CT":
            serie_iud_dicom = ds.SeriesInstanceUID           
            infos_ct.append({
                "patient_id": patient_id,
                "serie_iud": serie_iud_dicom,           
                "path": filepath
            })
        elif modality == "RTSTRUCT":
            roi_names = [roi.ROIName for roi in ds.StructureSetROISequence]
            serie_iud_rtstruct = ds.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID
            infos_rtstruct.append({
                "patient_id": patient_id,
                "roiname": roi_names,
                "serie_iud": serie_iud_rtstruct,
                "path": filepath
            })

    ct_df = pd.DataFrame(infos_ct)
    rt_df = pd.DataFrame(infos_rtstruct)

    return ct_df, rt_df

def preprocess_path(path):
    # Remove the last two elements from the path
    parts = path.split(os.sep)
    if len(parts) > 2:
        return os.sep.join(parts[:-2])
    return path

def merge_dataframes(ct_df, rt_df):
    # Create common identifiers for merging by removing the last two elements of the path
    ct_df['preprocessed_path'] = ct_df['path'].apply(preprocess_path)
    rt_df['preprocessed_path'] = rt_df['path'].apply(preprocess_path)

    # Merge the DataFrames on 'preprocessed_path' and 'serie_iud'
    merged_df = pd.merge(ct_df, rt_df, how='inner', left_on=['preprocessed_path', 'serie_iud', 'patient_id'], right_on=['preprocessed_path', 'serie_iud', 'patient_id'])
    
    return merged_df

    
def find_image_nifti(path):
    files = os.listdir(path)
    filename = None
    for file in files:
        if file.endswith(".nii.gz") and "mask" not in file:
            filename = file
            break  # Exit the loop once a suitable file is found
    return os.path.join(path,filename)

def extract_and_modify_filename(file_path):
    # Extract the last element from the path
    filename_with_extension = os.path.basename(file_path)    
    # Remove the ".nii.gz" extension if it exists
    if filename_with_extension.endswith('.nii.gz'):
        filename_without_extension = filename_with_extension[:-7]  # Remove the last 7 characters
    else:
        filename_without_extension = filename_with_extension    
    return filename_without_extension


def explode_roinames(df):
    """
    Explodes the 'roinames' column of the DataFrame, creating a new row for each item in the list,
    while preserving other column data.

    Parameters:
    df (pd.DataFrame): The input DataFrame with a 'roinames' column containing lists.

    Returns:
    pd.DataFrame: The resulting DataFrame with exploded 'roinames' values.
    """
    # Check if 'roinames' is a valid column and contains lists
    if 'roiname' in df.columns:
        # Use explode() to create a row for each element in the 'roinames' lists
        exploded_df = df.explode('roiname').reset_index(drop=True)
    else:
        raise ValueError("The DataFrame does not contain a 'roinames' column.")
    
    return exploded_df

def transform_roinames(value):
    """
    Transforms the input value by:
    1. Keeping only the part starting with the pattern r'E\d+'.
    2. Splitting by '_', keeping only the first four parts, and prefixing with 'mask_'.

    Parameters:
    value (str): The input string to transform.

    Returns:
    str: The transformed string.
    """
    # Define the regular expression pattern
    pattern = r'E\d+'
    
    # Search for the pattern in the string
    match = re.search(pattern, value)
    
    if match:
        # Extract the substring starting from the pattern
        value = value[match.start():]
        
        # Split the substring by '_'
        parts = value.split('_')
        
        # Keep only the first four parts
        parts = parts[:4]
        
        # Join the parts with '_', prefix with 'mask_', and return
        return 'mask_' + '_'.join(parts)
    else:
        # Return an empty string if the pattern is not found
        return value

def extract_ct_data(cohort_path):
    dicom_paths = find_paths.extract_folders_path(data_path=cohort_path, type="dicom")
    ct_df, rt_df = extract_dicom_info(dicom_paths)
    dicom_df = merge_dataframes(ct_df, rt_df)
    dicom_df_per_mask = explode_roinames(dicom_df)
    dicom_df_per_mask = dicom_df_per_mask.rename(columns={
        'preprocessed_path': 'directory_path',
        'path_x': 'ct_file_path',
        'path_y': 'rtstruct_file_path'
    })
    dicom_df_per_mask['roiname'] = dicom_df_per_mask['roiname'].apply(transform_roinames)
    return dicom_df_per_mask

def extract_nifti_data(cohort_path):
    nifti_paths = find_paths.extract_folders_path(data_path=cohort_path, type="nifti")
    nifti_infos = []
    for path in tqdm(nifti_paths, total=(len(nifti_paths))):
        image_path = find_image_nifti(path)
        for file in os.listdir(path):
            filepath = os.path.join(path,file)
            if filepath != image_path:               
                nifti_infos.append({"image_path":image_path,"mask_path":filepath})
    nifti_df = pd.DataFrame(nifti_infos)   
    nifti_df['roiname'] = nifti_df['mask_path'].apply(lambda x : extract_and_modify_filename(x))
    return nifti_df

def extract_patient_id(mask_path, patient_ids):
    mask_path_lower = mask_path.lower()
    for patient_id in patient_ids:
        if patient_id.lower() in mask_path_lower:
            return patient_id
    return None

def remove_accents(text):
    return unidecode(text)

def write_list_to_file(data_list, filename):  
  if data_list != []:
    with open(filename, 'w') as f:
      for element in data_list:
        f.write(f"{element}\n")     
  return 


def compute_metadata(dicom_path, nifti_path,output_path):
    
    dicom_df = extract_ct_data(dicom_path)
    dicom_df = dicom_df[dicom_df['roiname'] != 'External']    
    dicom_df.reset_index(drop=True, inplace=True)
    dicom_df['roiname'] = dicom_df['roiname'].apply(lambda x: x if x.startswith('mask_') else 'mask_' + x)
    dicom_df_cleaned = extract.extract_metadata_with_voi_type(dicom_df)

    dicom_df.to_csv('dicom_data.csv',index=False)

    nifti_df = extract_nifti_data(nifti_path)
    patient_ids_list = list(dicom_df_cleaned['patient_id'].values)
    nifti_df["patient_id"] = nifti_df["mask_path"].apply(lambda x: extract_patient_id(x, patient_ids_list))
    nifti_df_cleaned = extract.extract_metadata_with_voi_type(nifti_df)

    nifti_df_cleaned = nifti_df_cleaned.drop('roiname', axis=1)
    nifti_df_cleaned.to_csv('nifti_data.csv',index=False)

    nifti_df_cleaned['location'] = nifti_df_cleaned["location"].apply(lambda x : remove_accents(x))
    dicom_df_cleaned['location'] = dicom_df_cleaned["location"].apply(lambda x : remove_accents(x))

    index_nifti = list(nifti_df_cleaned.patient_id.astype(str) + '_' + nifti_df_cleaned.date.astype(str) + '_' + nifti_df_cleaned.location.astype(str) + '_' + nifti_df_cleaned.VOInum.astype(str) + '_' + nifti_df_cleaned.VOItype.astype(str) )
    index_dicom = list(dicom_df_cleaned.patient_id.astype(str) + '_' + dicom_df_cleaned.date.astype(str) + '_' + dicom_df_cleaned.location.astype(str) + '_' + dicom_df_cleaned.VOInum.astype(str) + '_' + dicom_df_cleaned.VOItype.astype(str) )

    nifti_df_cleaned = nifti_df_cleaned.copy()
    dicom_df_cleaned = dicom_df_cleaned.copy()

    nifti_df_cleaned['index'] = nifti_df_cleaned.patient_id.astype(str) + '_' + nifti_df_cleaned.date.astype(str) + '_' + nifti_df_cleaned.location.astype(str) + '_' + nifti_df_cleaned.VOInum.astype(str) + '_' + nifti_df_cleaned.VOItype.astype(str) 
    dicom_df_cleaned['index'] = dicom_df_cleaned.patient_id.astype(str) + '_' + dicom_df_cleaned.date.astype(str) + '_' + dicom_df_cleaned.location.astype(str) + '_' + dicom_df_cleaned.VOInum.astype(str) + '_' + dicom_df_cleaned.VOItype.astype(str) 
    print("nifti size :", len(nifti_df_cleaned))
    print("dicom size :", len(dicom_df_cleaned))

    # Drop duplicates based on the 'index' column
    nifti_df_cleaned = nifti_df_cleaned.drop_duplicates(subset='index')
    dicom_df_cleaned = dicom_df_cleaned.drop_duplicates(subset='index')
    print("nifti after drop :", len(nifti_df_cleaned))
    print("dicom after drop :", len(dicom_df_cleaned))

    # Merge on the components of the index
    merge_columns = ['patient_id', 'date', 'location', 'VOInum', 'VOItype']
    # Ensure the necessary columns are in both dataframes
    for col in merge_columns:
        assert col in dicom_df_cleaned.columns, f"Column '{col}' not in dicom_df_cleaned"
        assert col in nifti_df_cleaned.columns, f"Column '{col}' not in nifti_df_cleaned"

    # Perform the merge
    merged_df = pd.merge(dicom_df_cleaned, nifti_df_cleaned, on=merge_columns, how='inner')
    merged_df = merged_df.drop('index_x', axis=1)
    merged_df.rename(columns={'index_y': 'index'}, inplace=True) 

    print("metadata :", len(merged_df))

    in_dicom_not_nifti = set(index_dicom) - set(index_nifti)
    
    return merged_df, index_dicom, index_nifti, in_dicom_not_nifti


def find_duplicates(index_list):    
        counter = Counter(index_list)
        duplicates = [item for item, count in counter.items() if count > 1]
        return duplicates

def extract_unique_patient_ids(index_list):
    patient_ids = set([index.split('_')[0] for index in index_list])
    return patient_ids


def compute_missing_roi(index_list):
    split_indices = [index.split('_') for index in index_list]

    # Dictionaries to hold grouped data
    date_groups = defaultdict(list)
    roi_groups = defaultdict(list)

    # Group by patientID_location_voinum_voitype for date comparison
    for parts in split_indices:
        key_date = f"{parts[0]}_{parts[2]}_{parts[3]}_{parts[4]}"
        date_groups[key_date].append(parts[1])

    # Group by patientID_date_location_voinum for VOI type comparison
    for parts in split_indices:
        key_roi = f"{parts[0]}_{parts[1]}_{parts[2]}_{parts[3]}"
        roi_groups[key_roi].append(parts[4])

    # Compute missing dates
    missing_dates = []
    for key, dates in date_groups.items():
        if len(dates) == 1:
            missing_dates.append(f"{key}_{dates[0]}")

    # Compute missing ROIs
    missing_roi = []
    for key, rois in roi_groups.items():
        if len(rois) == 1:
            missing_roi.append(f"{key}_{rois[0]}")

    # Output results
    print("Missing Dates:", len(missing_dates))
    print("Missing ROIs:", len(missing_roi))
    return missing_dates, missing_roi



def main(dicom_path, nifti_path, output_path):

    merged_df, index_dicom, index_nifti, missing_nifti = compute_metadata(dicom_path, nifti_path,os.path.join(output_path,"metadata.csv"))

    missing_dates, missing_roi = compute_missing_roi(index_nifti)
    duplicates = find_duplicates(index_nifti)

    handle_list.write_list_to_file(missing_dates, os.path.join(output_path,"missing_dates.txt"))
    handle_list.write_list_to_file(missing_roi, os.path.join(output_path,"missing_roi.txt"))
    handle_list.write_list_to_file(duplicates, os.path.join(output_path,"duplicates.txt"))
    handle_list.write_list_to_file(list(missing_nifti), os.path.join(output_path,"missing_nifti_present_in_dicom.txt"))
    return



output_path = ""
dicom_path = ""
nifti_path = ""

main(dicom_path, nifti_path, output_path)