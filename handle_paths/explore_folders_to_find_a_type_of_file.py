import os
import pydicom

def get_modality(file_path):   
  if file_path.endswith(".dcm"):
    dcm_data = pydicom.dcmread(file_path) 
    try :   
      modality = dcm_data.Modality       
      return modality
    except :      
      if "CT" in file_path :
        return "CT"
      elif "RS" or "RTSTRUCT" in file_path :
        return "RTSTRUCT"
      
def get_RTSTRUCT_filenames(folder_path):
  filenames = []
  for file in os.listdir(folder_path):      
      modality = get_modality(os.path.join(folder_path,file)) 
      if modality == "RTSTRUCT" :
          filenames.append(file) 
  return filenames

def get_CT_filenames(folder_path):
  filenames = []
  for file in os.listdir(folder_path):      
      modality = get_modality(os.path.join(folder_path,file)) 
      if modality == "CT" :
          filenames.append(file) 
  return filenames

def get_folder_modality(folder_path):
  CT = False
  RTSTRUCT = False
  for file in os.listdir(folder_path):      
    modality = get_modality(os.path.join(folder_path,file)) 
    if modality == "CT":
       CT = True
    elif modality == "RTSTRUCT" :
       RTSTRUCT = True
  return CT, RTSTRUCT  

def explore_folders(folder_path, folder_paths, type): 
    if type == "nifti" or type == "NIFTI" :
        if any(file.endswith(".nii.gz") for file in os.listdir(folder_path)): 
            folder_paths.append(folder_path)             
            return
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)
            if os.path.isdir(subfolder_path):
                explore_folders(subfolder_path, folder_paths,type)
    elif type == "dicom" or type == "DICOM":
        if any(file.endswith(".dcm") for file in os.listdir(folder_path)): 
            folder_paths.append(folder_path)             
            return
        for subfolder in os.listdir(folder_path):
            subfolder_path = os.path.join(folder_path, subfolder)
            if os.path.isdir(subfolder_path):
                explore_folders(subfolder_path, folder_paths,type)


def extract_folders_path(data_path,type):
    folder_paths = []       
    for patient in os.listdir(data_path):
        patient_path = os.path.join(data_path, patient)        
        if os.path.isdir(patient_path):                       
            explore_folders(patient_path, folder_paths,type)
    return folder_paths

