import os
import shutil

  
def delete_file(file_path):  
  try:
    os.remove(file_path)
    #print(f"File deleted successfully: {file_path}")
  except FileNotFoundError:
    print(f"Error: File not found: {file_path}")
  except PermissionError:
    print(f"Error: Insufficient permissions to delete {file_path}")
  except Exception as e:  
    print(f"Error deleting file: {e}")
  return


def copy_file(source_path, destination_path): 
  try:
    shutil.copy2(source_path, destination_path)
    #print(f"File copied successfully: {source_path} -> {destination_path}")
  except FileNotFoundError:
    print(f"Error: Source file not found: {source_path}")
  except Exception as e:  
    print(f"Error copying file: {e}")
  return   


def move_folder(source_path, destination_path):
  try:
    shutil.move(source_path, destination_path)
    #print(f"Folder moved successfully: {source_path} -> {destination_path}")
  except FileNotFoundError:
    print(f"Error: Source folder not found: {source_path}")
  except Exception as e:
    print(f"Error moving folder: {e}")


def delete_folder(folder_path):  
  try:    
    if os.path.exists(folder_path):      
      shutil.rmtree(folder_path)
      #print(f"Folder deleted: {folder_path}")
    else:
      print(f"Folder not found: {folder_path}")
  except OSError as e:
    print(f"Error deleting folder: {folder_path} - {e}")