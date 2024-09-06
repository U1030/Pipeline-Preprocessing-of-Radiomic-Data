import os
import argparse



def add_import_to_files( path):   
    import_statement =  'import sys\nsys.path.append("' + path + '")'
    for dirpath, _, filenames in os.walk(path):        
        for filename in filenames:
            if filename.endswith('.py'):                
                filepath = os.path.join(dirpath, filename)                
                with open(filepath, 'r') as file:
                    content = file.readlines()               
                content.insert(0, import_statement + '\n')              
                with open(filepath, 'w') as file:
                    file.writelines(content)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add import statement to Python files.")    
    parser.add_argument("pipeline_path", type=str, help="Path to the cloned pipeline")
    args = parser.parse_args()
    add_import_to_files(args.pipeline_path)

