import os
import SimpleITK as sitk

import sys
#sys.path.append("")

from parralelize import parallelize_v2 as par
from handle_paths import extract_paths, explore_folders_to_find_a_type_of_file


def convert_dicom2nrrd(path_folder): 
  output_folder = "NRRD"
  output_folder_path = os.path.join(path_folder, output_folder)
  if not os.path.exists(output_folder_path):
      os.makedirs(output_folder_path)                                       
                                
  reader = sitk.ImageSeriesReader()
  dicomReader = reader.GetGDCMSeriesFileNames(path_folder)
  reader.SetFileNames(dicomReader)
  dicoms = reader.Execute()
  fileName = os.path.join(output_folder_path,"output.nrrd")
  sitk.WriteImage(dicoms, fileName)                 
  return


def convert_one_patient(patient_path):            
    dicom_paths = explore_folders_to_find_a_type_of_file.extract_folders_path(patient_path,type='dicom') 
    for path in dicom_paths:    
      convert_dicom2nrrd(path)
    return

def process_all_patients(path,depth = 2, direct =True):    
    if direct :
      subfolders = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
      patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
      patients_paths = extract_paths.get_folders_at_depth(path, depth)   
    results = par.parralelize_for_patients(patients_paths, convert_one_patient)
    return