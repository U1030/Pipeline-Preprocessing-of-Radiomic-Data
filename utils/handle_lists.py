


def flatten_list(list_of_lists):
  return [item for sublist in list_of_lists for item in sublist]


def write_list_to_file(data_list, filename):  
  if data_list != []:
    with open(filename, 'w') as f:
      for element in data_list:
        f.write(f"{element}\n")     
  return 


def read_file_to_list(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            # Optionally, strip newline characters
            lines = [line.strip() for line in lines]
        return lines
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except IOError as e:
        print(f"Error: Could not read file '{file_path}'. {e}")
        return []