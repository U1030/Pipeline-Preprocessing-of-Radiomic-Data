import os


def get_folders_at_depth(root_path, max_depth):
    folders = []
    current_folders = os.listdir(root_path)
    current_folder_paths = [os.path.join(root_path, folder) for folder in current_folders if os.path.isdir(os.path.join(root_path, folder))]
    
    folders.extend(current_folder_paths)
    
    for _ in range(max_depth -1):
        next_level_folders = []      
        for path in current_folder_paths:
            try:
                sub_folders = [os.path.join(path, folder) for folder in os.listdir(path) if os.path.isdir(os.path.join(path, folder))]
                next_level_folders.extend(sub_folders)
            except PermissionError:
                continue  
        
        if not next_level_folders:
            break  # No more folders to process
        folders = [] # empty the list to retrieve only final depth paths
        folders.extend(next_level_folders)
        current_folder_paths = next_level_folders      

    return folders




