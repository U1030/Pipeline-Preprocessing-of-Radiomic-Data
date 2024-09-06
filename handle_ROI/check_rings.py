import numpy as np
import os
from scipy import ndimage
import SimpleITK as sitk
import argparse


import sys
#sys.path.append("")

from visualization  import visualize as vz
from parralelize  import parallelize_v2 as par
from handle_ROI  import determine_nifti_mask_smallest_diameter as sd
from handle_paths import explore_folders_to_find_a_type_of_file as find
from handle_paths import extract_paths
from utils import handle_lists
from handle_paths import find_matching_ring_and_tumor_nifti_files as find_match



"""
to check the masks in a folder containing the masks:
process_folder(folder_path)

to check the masks in all patients folders contained in input folder path :
process_all_patients(folder_path, output_path)

"""


def overlap_complete(mask_tumor,mask_ring, tumor_path):
  ind_tumor = np.where(mask_tumor == 1)
  ind_ring = np.where(mask_ring == 1)
  values_ring = mask_ring[ind_tumor]
  values_ring_flat = values_ring.ravel() 
  center_of_mass, boundary_points, closest_boundary_point, smallest_radius, smallest_diameter = sd.calculate_smallest_diameter_and_points(tumor_path)
  if smallest_diameter < 5 :
     print("tumor too small, no hole visible in the mask :", tumor_path)
     return False
  else :
    if np.all(values_ring_flat == 1) :
      return True
    else :
      return False
    
def same_size(mask_tumor,mask_ring):
    ind_tumor = np.where(mask_tumor == 1)
    ind_ring = np.where(mask_ring == 1)
    if len(ind_tumor[0]) == len(ind_ring[0]) :
       return True
    else :
       return False   


def check_ring_overlap(mask_tumor, mask_ring, erosion_iterations=1, min_overlap = 0.70):    
  eroded_tumor = ndimage.binary_erosion(mask_tumor, iterations=erosion_iterations)  
  tumor_boundary = np.logical_xor(mask_tumor, eroded_tumor)  
  non_zero_boundary = np.where(tumor_boundary != 0)
  overlapping_pixels = np.count_nonzero(mask_ring[non_zero_boundary]) 
  total_boundary_pixels = np.count_nonzero(tumor_boundary)
  overlap_percentage = overlapping_pixels / total_boundary_pixels  
  return overlap_percentage >= min_overlap


def process_masks(mask_tumor,mask_ring, tumor_path, visualize):
  no = []
  complete = []
  same_size_list = []
  complete_overlap = overlap_complete(mask_tumor,mask_ring, tumor_path)  
  overlap = check_ring_overlap(mask_tumor, mask_ring)
  same_size_masks = same_size(mask_tumor,mask_ring)
  if same_size_masks:
    if visualize :   
        vz.visualize_masks(mask_tumor, mask_ring, title=" masks have same size")     
    same_size_list.append(("same size masks ",tumor_path))  
    #print("same size tumor and ring :",tumor_path) 
  elif complete_overlap :      
    if visualize :   
        vz.visualize_masks(mask_tumor, mask_ring, title="complete overlap of masks")     
    complete.append(("complete overlap ",tumor_path))
    #print("complete overlap NOT SAME SIZE :", tumor_path)
  else:
    if overlap == False : 
      if visualize :   
        vz.visualize_masks(mask_tumor, mask_ring, title="no overlap between masks")      
      no.append(("no overlap ",tumor_path))
      #print("no overlap between masks :", tumor_path) 
  return no,complete, same_size_list

def compute_results_for_folder(folder_path, visualize = True):
    complete_overlap_lesions = []
    no_overlap_lesions = []
    same_size_lesions =[]
    nifti_paths = find.extract_folders_path(folder_path,type='nifti')
    
    if nifti_paths:
      for folder_path_nifti in nifti_paths:
        mask_tumor_files, mask_ring_files = find_match.find_matching_nifti_files_resampled(folder_path_nifti) 
        for tumor, ring in zip(mask_tumor_files, mask_ring_files):  
            print('tumor :', tumor)
            print('ring :', ring)          
            tumor_path = os.path.join(folder_path_nifti, tumor)                     
            img_tumor = sitk.ReadImage(tumor_path)
            arr_tumor = sitk.GetArrayFromImage(img_tumor)             
            ring_path = os.path.join(folder_path_nifti, ring)             
            img_ring = sitk.ReadImage(ring_path)
            arr_ring = sitk.GetArrayFromImage(img_ring)                                  
            no_overlap_temp, complete_overlap_temp,same_size_temp = process_masks(arr_tumor,arr_ring, tumor_path, visualize)  
            if len(complete_overlap_temp) != 0 :
                complete_overlap_lesions.append(complete_overlap_temp)
            if len(no_overlap_temp) != 0 :
                no_overlap_lesions.append(no_overlap_temp)
            if len(same_size_temp) != 0 :
               same_size_lesions.append(same_size_temp)
    
    else :
      mask_tumor_files, mask_ring_files = find_match.find_matching_nifti_files_resampled(folder_path)            
      for tumor, ring in zip(mask_tumor_files, mask_ring_files):  
              print('tumor :', tumor)
              print('ring :', ring)          
              tumor_path = os.path.join(folder_path, tumor)                     
              img_tumor = sitk.ReadImage(tumor_path)
              arr_tumor = sitk.GetArrayFromImage(img_tumor)             
              ring_path = os.path.join(folder_path, ring)             
              img_ring = sitk.ReadImage(ring_path)
              arr_ring = sitk.GetArrayFromImage(img_ring)                                  
              no_overlap_temp, complete_overlap_temp,same_size_temp = process_masks(arr_tumor,arr_ring, tumor_path, visualize)  
              if len(complete_overlap_temp) != 0 :
                  complete_overlap_lesions.append(complete_overlap_temp)
              if len(no_overlap_temp) != 0 :
                  no_overlap_lesions.append(no_overlap_temp)
              if len(same_size_temp) != 0 :
                same_size_lesions.append(same_size_temp)
    return no_overlap_lesions, complete_overlap_lesions, same_size_lesions

def process_folder(folder_path):  
  if not os.path.exists(folder_path):
    print(f"Error: Folder '{folder_path}' does not exist.")
    exit()  
  no_overlap_lesions, complete_overlap_lesions, same_size_lesions = compute_results_for_folder(folder_path, visualize=True)
  path_no = os.path.join(folder_path,"no overlap lesions recap")
  path_complete = os.path.join(folder_path,"complete overlap lesions recap")
  path_same_size = os.path.join(folder_path, "same size tumor and ring masks recap")
  handle_lists.write_list_to_file(no_overlap_lesions,path_no)
  handle_lists.write_list_to_file(complete_overlap_lesions,path_complete) 
  handle_lists.write_list_to_file(same_size_lesions, path_same_size) 
  print('no overlap :', no_overlap_lesions)
  print('complete overlap :', complete_overlap_lesions)
  print('same size lesions :', same_size_lesions)
  return no_overlap_lesions,complete_overlap_lesions, same_size_lesions

def process_patient(patient_path):  
  #print("processing patient :", patient_path)
  no_patient = []
  complete_patient = [] 
  same_size_patient = []
  folders = find.extract_folders_path(patient_path,type='nifti')
  for folder_path in folders:
    no,complete,same_size_list = process_folder(folder_path)
    no_patient.append(no)
    complete_patient.append(complete)
    same_size_patient.append(same_size_list)
  return handle_lists.flatten_list(no_patient), handle_lists.flatten_list(complete_patient), handle_lists.flatten_list(same_size_patient)


def extract_non_empty_lists(list_of_tuples):
    first_elements = []
    second_elements = []
    for tuple_item in list_of_tuples:
        if tuple_item[0]:
            first_elements.extend(tuple_item[0])
        if tuple_item[1]:
            second_elements.extend(tuple_item[1])
    return first_elements, second_elements


def process_all_patients(path, path_output,depth = 2, direct =True):    
    if direct :
      subfolders = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
      patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
      patients_paths = extract_paths.get_folders_at_depth(path, depth)   
    results = par.parralelize_for_patients(patients_paths, process_patient)
    if len(results) == 3:
      no, complete,same_size_list = extract_non_empty_lists(results)  
      no_path = os.path.join(path_output,"no overlap lesions recap.txt")
      path_complete = os.path.join(path_output,"complete overlap lesions recap.txt")
      path_same_size = os.path.join(path_output," same size ring and tumor lesions recap.txt")
      handle_lists.write_list_to_file(no,no_path)
      handle_lists.write_list_to_file(complete, path_complete)
      handle_lists.write_list_to_file(same_size_list, path_same_size)   
    elif len(results) == 0:
      print("no problematic masks detected .")
    else :
        final_results = []
        for i in range(len(results)):
          sub_results = results[i]
          final_results.append(sub_results)
        path =  os.path.join(path_output, "check ring results.txt")
        non_empty_final_results = [
        [sublist for sublist in item if sublist != []]
        for item in final_results
        if any(sublist for sublist in item if sublist != [])]
        handle_lists.write_list_to_file(handle_lists.flatten_list(non_empty_final_results), path)     
    return


"""

def main():
    parser = argparse.ArgumentParser(description="Process patient data or folder.")

    subparsers = parser.add_subparsers(dest="command", help="sub-command help")

    # Subparser for process_all_patients
    parser_all_patients = subparsers.add_parser("all_patients", help="Process all patients")
    parser_all_patients.add_argument("path", type=str, help="Input path for patient data")
    parser_all_patients.add_argument("path_output", type=str, help="Output path for processed data")

    # Subparser for process_folder
    parser_folder = subparsers.add_parser("folder", help="Process a folder")
    parser_folder.add_argument("folder_path", type=str, help="Path of the folder to process")

    args = parser.parse_args()

    if args.command == "all_patients":
        process_all_patients(args.path, args.path_output)
    elif args.command == "folder":
        process_folder(args.folder_path)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()


"""



comand = ''
path = ''

# optional : if in your architecture the path doesn't contain directly patient folders but for exemple folder per center then patient folder 
# you need to put direct to False and input the depth at which patient folders are 

depth = ""
direct = True


if comand == 'multiple_folders':
  process_all_patients(path,depth=depth,direct=direct)
elif comand  == "folder":
  process_folder(path)