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