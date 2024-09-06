import os

def find_matching_nifti_files(directory):   
    mask_tumor_files = []
    mask_ring_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".nii.gz"):            
            if "GTV" in filename:                          
                ring_filename = filename.replace("GTV", "ring" ) 
                if ring_filename in os.listdir(directory):
                    mask_tumor_files.append(filename)  
                    mask_ring_files.append(ring_filename)                
    return mask_tumor_files, mask_ring_files


def find_matching_nifti_files_resampled(directory):   
    mask_tumor_files = []
    mask_ring_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".nii.gz"):
            if "RESAMPLED" in filename : 
                    if "CREATED" not in filename and "processed" not in filename :            
                        if "GTV" in filename:                                        
                            ring_filename = filename.replace("GTV", "ring" ) 
                            if ring_filename in os.listdir(directory):
                                mask_tumor_files.append(filename)  
                                mask_ring_files.append(ring_filename)                            
    return mask_tumor_files, mask_ring_files


def find_matching_nifti_files_not_resampled(directory):   
    mask_tumor_files = []
    mask_ring_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".nii.gz"):
            if "RESAMPLED" not in filename : 
                    if "CREATED" not in filename and "processed" not in filename :            
                        if "GTV" in filename:                                        
                            ring_filename = filename.replace("GTV", "ring" ) 
                            if ring_filename in os.listdir(directory):
                                mask_tumor_files.append(filename)  
                                mask_ring_files.append(ring_filename)                            
    return mask_tumor_files, mask_ring_files

def find_GTV_files(directory):   
  mask_tumor_files = []    
  for filename in os.listdir(directory):
      if filename.endswith(".nii.gz"):            
          if "GTV" in filename:
              if "RESAMPLED" in filename : 
                  if "CREATED" not in filename and "processed" not in filename :
                    mask_tumor_files.append(filename)                
  return mask_tumor_files