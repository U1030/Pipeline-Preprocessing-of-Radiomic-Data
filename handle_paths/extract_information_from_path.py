import re

def extract_patient_from_path(path,patients):
    patient = [id for id in patients if id in path ]
    if len(patient) != 0:
        return patient[0]
    else :
        return None

def extract_patient_id_from_path_when_folder_name_different_from_texture_session(path,id_patient_position_in_path):
    path = path.replace("\\","/")   
    id = path.split(sep="/")[id_patient_position_in_path]
    return id

def extract_mask_name(file):
    mask_splited = file.split(sep='_')[:6]
    mask_name = '_'.join(mask_splited) 
    return mask_name 


def extract_date_from_path(input_string):    
    pattern = r'E\d+'   
    match = re.search(pattern, input_string) 
    pattern2 = r'T\d+'   
    match2 = re.search(pattern2, input_string)    
    if match:
        return match.group()
    elif match2:
        return match2.group()
    else:        
        return None
    

def find_location(path):
    # Split the path on underscores
    parts = path.split('_')
    # The potential location part
    part2 = parts[2]

    # Check for specific location cases
    if part2 in ["ring", "tum", "GTV"]:
        location = parts[3]
    else:
        location = part2

    # Remove any digits from the location
    location = re.sub(r'\d+', '', location)

    return location


def find_VOInum(path):
    # Split the path on underscores
    parts = path.split('_')
    location_index = 2

    # Check if location is special case
    if parts[2] in ["ring", "tum", "GTV"]:
        location_index = 3
    
    # Next part after the location
    next_part_index = location_index + 1
    next_part = parts[next_part_index]

    # Check if the next part is a number
    if any(char.isdigit() for char in next_part):
        return next_part
    
    elif next_part == 'tum' or next_part == 'ring' or next_part =='GTV' or next_part == 'RING':
        next_part = parts[next_part_index+1]
        if any(char.isdigit() for char in next_part):
            return next_part
    else:
        # If not a number, check if there is a number in the location itself
        location = parts[location_index]
        num_in_location = re.search(r'\d+', location)
        if num_in_location:
            return num_in_location.group()        
    
    # If neither scenario applies, return 0
    return '0'

def find_date(input_string):    
    pattern = r'E\d+'   
    match = re.search(pattern, input_string) 
    pattern2 = r'T\d+'   
    match2 = re.search(pattern2, input_string)    
    if match:
        return match.group()
    elif match2:
        return match2.group()
    else:        
        return None
    
def find_voi_type(string):
    if '_tum_' in string or "_GTV_" in string:
        return 'tum'
    elif '_ring_' in string or '_RING_' in string:
        return 'ring'

def extract_metadata(data_cleaned):
    data_cleaned['date'] = data_cleaned["roiname"].apply(lambda x : find_date(x))
    data_cleaned['location'] = data_cleaned["roiname"].apply(lambda x : find_location(x))
    data_cleaned['VOInum'] = data_cleaned["roiname"].apply(lambda x : find_VOInum(x))
    return data_cleaned

def extract_metadata_with_voi_type(data_cleaned):
    data_cleaned['date'] = data_cleaned["roiname"].apply(lambda x : find_date(x))
    data_cleaned['location'] = data_cleaned["roiname"].apply(lambda x : find_location(x))
    data_cleaned['VOInum'] = data_cleaned["roiname"].apply(lambda x : find_VOInum(x))
    data_cleaned['VOItype'] = data_cleaned["roiname"].apply(lambda x : find_voi_type(x))
    return data_cleaned

