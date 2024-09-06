import os 
from collections import defaultdict
import pydicom

import sys
#sys.path.append("")

from handle_paths import explore_folders_to_find_a_type_of_file as find


def get_series_instance_uid(file_path):
    """
    Extracts the Series Instance UID from a DICOM file.
    """
    dcm_data = pydicom.dcmread(file_path)
    return dcm_data.SeriesInstanceUID

def get_rtstruct_series_instance_uid(file_path):
    """
    Extracts the Series Instance UID from an RTSTRUCT file.
    """
    dcm_data = pydicom.dcmread(file_path)
    return dcm_data.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID

def check_rtstruct_for_ct_series(folder_paths):
    """
    Checks that every CT series has a corresponding RTSTRUCT file.
    """
    series_dict = {}

    for folder in folder_paths:
        # List files in the folder
        files = [f for f in os.listdir(folder) if f.endswith('.dcm')]

        if not files:
            continue

        # Check modality of the first file
        first_file_path = os.path.join(folder, files[0])
        modality = pydicom.dcmread(first_file_path).Modality

        if modality == 'CT':
            # Extract Series Instance UID for CT
            series_uid = get_series_instance_uid(first_file_path)
            series_dict[series_uid] = {'ct_folder': folder, 'rtstruct_found': False}

        elif modality == 'RTSTRUCT':
            # Extract Series Instance UID for RTSTRUCT
            series_uid = get_rtstruct_series_instance_uid(first_file_path)
            if series_uid in series_dict:
                series_dict[series_uid]['rtstruct_found'] = True
            else:
                series_dict[series_uid] = {'ct_folder': None, 'rtstruct_found': True}

    # Report missing RTSTRUCT for any CT series
    missing_rtstruct = []
    for series_uid, data in series_dict.items():
        if not data['rtstruct_found']:
            missing_rtstruct.append(data['ct_folder'])

    return missing_rtstruct


def main(path):
  dicom_folder_path = find.extract_folders_path(path, type='dicom')
  missing_rtstruct = check_rtstruct_for_ct_series(dicom_folder_path)
  if missing_rtstruct:
      print("The following CT series are missing a corresponding RTSTRUCT:")
      for folder in missing_rtstruct:
          print(folder)
  else:
      print("All CT series have a corresponding RTSTRUCT.")



path =  ""
main(path)