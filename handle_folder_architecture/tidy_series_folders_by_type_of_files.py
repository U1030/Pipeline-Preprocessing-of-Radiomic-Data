import os
import shutil
import pydicom


def organize_dicom_files(dicom_folder):
    # Create folders for each type of DICOM files
    ct_folder = os.path.join(dicom_folder, "DICOMS")
    rtstruct_folder = os.path.join(dicom_folder, "RTSTRUCT")
    nifti_folder = os.path.join(dicom_folder, "NIFTI")
    for folder in [ct_folder, rtstruct_folder, nifti_folder]:
        os.makedirs(folder, exist_ok=True)
    files = [file for file in os.listdir(dicom_folder) if not os.path.isdir(os.path.join(dicom_folder, file))]   
    for file in files:
        file_path = os.path.join(dicom_folder, file)            
        if file.endswith(".dcm"):
            dcm_data = pydicom.dcmread(file_path)
            mod = dcm_data.Modality
            if mod == "CT":
                shutil.move(file_path, os.path.join(ct_folder, file))
            elif mod == "RTSTRUCT":
                shutil.move(file_path, os.path.join(rtstruct_folder, file))
            else : 
                print(mod)
        elif file.endswith(".nii") or file.endswith(".nii.gz"):
            shutil.move(file_path, os.path.join(nifti_folder, file))


def process_patient_folder(patient_path):
    if os.path.isdir(patient_path):
        sub_subfolders = [folder for folder in os.listdir(patient_path) if os.path.isdir(folder)]  
        for sub_time in sub_subfolders:        
            sub_time_path = os.path.join(patient_path,sub_time)   
            folders = os.listdir(sub_time_path)  
            test = any(file.endswith('.nii.gz') for file in folders) 
            sub_sub_subfolders = [folder for folder in os.listdir(sub_time_path) if os.path.isdir(folder)]
            if test :
                organize_dicom_files(sub_time_path)        
            else :
                for sub_loc in sub_sub_subfolders:                      
                    sub_loc_path = os.path.join(sub_time_path, sub_loc)
                    organize_dicom_files(sub_loc_path)   
        return        
