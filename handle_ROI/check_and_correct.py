import os
import SimpleITK as sitk
import argparse

import sys
#sys.path.append("")


import handle_ROI.check_rings as check_ring
import handle_ROI.create_rings as construct_ring
from handle_paths import explore_folders_to_find_a_type_of_file as find
from handle_paths import extract_paths
from handle_paths import find_matching_ring_and_tumor_nifti_files as find_match_nifties

def output_mask_state(tumor_path, ring_path):             
  img_tumor = sitk.ReadImage(tumor_path)  
  img_ring = sitk.ReadImage(ring_path) 
  mask_tumor = sitk.GetArrayFromImage(img_tumor)  
  mask_ring = sitk.GetArrayFromImage(img_ring) 
  complete_overlap = check_ring.overlap_complete(mask_tumor,mask_ring, tumor_path)  
  overlap = check_ring.check_ring_overlap(mask_tumor, mask_ring)
  same_size = check_ring.same_size(mask_tumor, mask_ring)
  no_overlap = False
  if complete_overlap :    
    no_overlap = False 
  else:
    if overlap == False:      
      no_overlap = True       
  return complete_overlap, no_overlap , same_size

def process_masks_correction(ring_path, tumor_path, visualize, percentile):            
    complete_overlap, no_overlap, same_size = output_mask_state(tumor_path,ring_path)
    if complete_overlap or no_overlap or same_size:      
        construct_ring.construct_ring_mask(tumor_path,percentile,visualize)   
    return

def process_patient(patient_path):
    folders = find.extract_folders_path(patient_path,type='nifti')
    for folder_path in folders :
        mask_tumor_files, mask_ring_files = find_match_nifties.find_matching_nifti_files_resampled(folder_path)    
        for tumor, ring in zip(mask_tumor_files, mask_ring_files):            
                tumor_path = os.path.join(folder_path, tumor)
                ring_path = os.path.join(folder_path, ring)       
                process_masks_correction(ring_path,tumor_path, visualize= False, percentile=90)
    return

def process_all_patients(path, depth = 2, direct =True):
    if direct :
        subfolders = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
        patients_paths = [os.path.join(path, patient_folder) for patient_folder in subfolders]
    else :
        patients_paths = extract_paths.get_folders_at_depth(path, depth)
    for patient_path in patients_paths:     
        process_patient(patient_path)



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
        process_patient(args.folder_path)
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
  process_patient(path)