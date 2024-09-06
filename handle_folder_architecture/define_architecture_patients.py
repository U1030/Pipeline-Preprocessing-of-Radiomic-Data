import pydicom
import os 
from datetime import datetime
import shutil
from collections import Counter

import sys
#sys.path.append("")


from handle_paths import extract_RTSTRUCT_and_CT_filenames as get_dicom_filenames
from handle_folder_architecture import handle_folder_and_files as handle


def sort_dates(dates):
    if len(dates) > 1 :
        date_objects = [datetime.strptime(date, '%Y%m%d') for date in dates]
        sorted_dates = sorted(date_objects)
        sorted_dates_strings = [date.strftime('%Y%m%d') for date in sorted_dates] 
        return sorted_dates_strings
    else : 
        return dates

def get_dates(patient_folder_path):  
    series_folders = [folder for folder in os.listdir(patient_folder_path) if os.path.isdir(os.path.join(patient_folder_path, folder))]    
    aquisition_date =  []  
    for folder in series_folders: 
        folder_path = os.path.join(patient_folder_path,folder)
        filenames = get_dicom_filenames.get_CT_filenames(folder_path)       
        file = filenames[0] 
        file_path = os.path.join(folder_path, file)    
        dcm_data = pydicom.dcmread(file_path)   
        aquisition_date.append(dcm_data[0x008, 0x022].value)              
    unique_dates = set(aquisition_date)       
    sorted_dates = sort_dates(unique_dates)     
    return list(sorted_dates)

def get_RT_dates(patient_folder_path): 
    times =  [] 
    filenames = get_dicom_filenames.get_RTSTRUCT_filenames(patient_folder_path) 
    for file in filenames :      
        file_path = os.path.join(patient_folder_path, file)    
        dcm_data = pydicom.dcmread(file_path)   
        time = dcm_data.StructureSetROISequence[0].ROIName       
        time = time[:2]        
        times.append(time)          
    return times

def separate_by_series_id(folder_path):
    filenames = get_dicom_filenames.get_CT_filenames(folder_path)
    id = []
    for filename in filenames:  
        file_path = os.path.join(folder_path, filename)    
        dcm_data = pydicom.dcmread(file_path)     
        id.append(dcm_data[0x020,0x00e].value) 
         
    unique_id = set(id)  
    id_paths = []
    for i in unique_id: 
        try:
            folder_name = i
            id_path = os.path.join(folder_path,folder_name)
            id_paths.append(id_path)
            os.makedirs(id_path)                
        except FileExistsError:
            print(f"Folder {folder_name} already exist")  

   
    for filename in filenames:  
        file_path = os.path.join(folder_path, filename)
        dcm_data = pydicom.dcmread(file_path)             
        for folder_name in unique_id:
            if dcm_data[0x020,0x00e].value == folder_name:                    
                new_path = os.path.join(folder_path,folder_name)
                shutil.move(file_path,new_path)
    return 


def find_matches_CT_RTSTRUCT(folder_path):
    RT_files = get_dicom_filenames.get_RTSTRUCT_filenames(folder_path)
    series_folders = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]   
    for folder in series_folders:
        serie_folder_path = os.path.join(folder_path,folder)               
        for RT_file in RT_files:
            RT_path = os.path.join(folder_path,RT_file)
            RT_data = pydicom.dcmread(RT_path)
            RT_id = RT_data.ReferencedFrameOfReferenceSequence[0].RTReferencedStudySequence[0].RTReferencedSeriesSequence[0].SeriesInstanceUID 
            if folder == RT_id:                
                handle.copy_file(RT_path,serie_folder_path)
    for RT_file in RT_files:
        RT_path = os.path.join(folder_path,RT_file)
        handle.delete_file(RT_path)
    return


def separate_by_time(patient_folder_path, sorted_dates, RT_times):        
    RT_times_count = Counter(RT_times)    
    series_folders = [folder for folder in os.listdir(patient_folder_path) if os.path.isdir(os.path.join(patient_folder_path, folder))] 
    nb_dates = len(sorted_dates)    
    if nb_dates > 2 :
        if "T0" in RT_times_count:
            baseline_dates = sorted_dates[:RT_times_count["T0"]]
            evaluation_dates = sorted_dates[RT_times_count["T0"]:]        
        else : # "TX"
            baseline_dates = sorted_dates[0]
            evaluation_dates = sorted_dates[1:] 
    else :
            baseline_dates = sorted_dates[0]
            evaluation_dates = sorted_dates[1:]                
    try:            
        base_path = os.path.join(patient_folder_path,"Baseline")            
        os.makedirs(base_path)          
    except FileExistsError:
        print("Folder Baseline already exist")          
            
    try:            
        eval_path = os.path.join(patient_folder_path,"Evaluation")           
        os.makedirs(eval_path)          
    except FileExistsError:
        print("Folder Evaluation already exist")    
    for folder in series_folders:  
        folder_path = os.path.join(patient_folder_path, folder)
        filenames =  get_dicom_filenames.get_CT_filenames(folder_path)
        file = filenames[0] 
        file_path = os.path.join(folder_path,file)
        dcm_data = pydicom.dcmread(file_path)             
        if dcm_data[0x008, 0x022].value in baseline_dates:                           
            date_folder = "Baseline"
            directory = os.path.join(patient_folder_path,date_folder)                     
            handle.move_folder(folder_path,directory)         
        elif dcm_data[0x008, 0x022].value in evaluation_dates:                
                date_folder = "Evaluation"
                directory = os.path.join(patient_folder_path,date_folder)           
                handle.move_folder(folder_path,directory)
        else : 
            print("error file data not lists")
    return


def process_patient_folder(patient_folder_path):
    baseline_path = os.path.join(patient_folder_path,'Baseline')
    evaluation_path = os.path.join(patient_folder_path,'Evaluation')
    if os.path.exists(baseline_path) and os.path.exists(evaluation_path):
        separate_by_series_id(baseline_path)
        separate_by_series_id(evaluation_path)
        find_matches_CT_RTSTRUCT(baseline_path)
        find_matches_CT_RTSTRUCT(evaluation_path)
    else : 
        RT_dates = get_RT_dates(patient_folder_path)
        separate_by_series_id(patient_folder_path)
        CT_dates = get_dates(patient_folder_path)
        find_matches_CT_RTSTRUCT(patient_folder_path)
        separate_by_time(patient_folder_path,CT_dates,RT_dates)
    return

