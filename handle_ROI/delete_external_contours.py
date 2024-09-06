import os

import sys
#sys.path.append("")


from handle_paths import explore_folders_to_find_a_type_of_file as find


def main(nifti_path):
    paths_nifti_folders = find.extract_folders_path(nifti_path,type='nifti')

    files_to_delete = []

    for folder_path in paths_nifti_folders:
        for file in os.listdir(folder_path):
            if 'External' in file:
                files_to_delete.append(os.path.join(folder_path,file))
                
    for file in files_to_delete:
        file_to_delete_path = os.path.join(folder_path, file)
        os.remove(file_to_delete_path)
        print(f"Deleted: {file_to_delete_path}")


path = ''
main(path)