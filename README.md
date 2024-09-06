# Radiomic Data Pre-Processing Pipeline

<p> First step :

Add the pipeline path to sys.path so that your python compilator find all the modules of the pipeline : go to module handle_paths execute comand in terminal 

```
python add_pipeline_path.py /home/user/my_project/pipeline
```

### handle folder architecture : 

#### define_architecture_patients.py

It is good to start by organizing your files and standardize the architecture across patients

Patient_ID --> 
              Time --> 
                      Serie ID  

NOTE : assumes data is arranged in folder by patient

```
process_all_patients(root_path,depth)
```

```
process_patient(path)
```

inputs :

path : path to folder containing your patient data 
depth : depth at which you find patient folder
if your folder directly leads to patient folders then the depth is 1 if your folder contain fodlers per center for example, and then your patient folders, your depth is 2


#### handle_folder_and_files.py

delete,move,copy a file or a folder

#### tidy_series_folders_by_type_of_file.py

if you have nifti, dicom : ct and rtstruct in serie folder, organize them further into three separate folder

```
process_all_patients(root_path,depth)
```

```
process_patient(path)
```

inputs :

path : path to folder containing your patient data 
depth : depth at which you find patient folder

### conversion

#### convert_dicom_nifti.py

For the convertion of DICOM files into nifti format I use a pipeline developed by Alexandre Carre<sup>123</sup> 

https://github.com/U1030/DS2nii.git 

Please follow the installation steps described on the deposit and activate the environment before using the Step_3.py
```
1. U1030 Radiothérapie Moléculaire, Université Paris-Sud, Gustave Roussy, Inserm, Université Paris-Saclay, 94800, Villejuif, France
2. Université Paris Sud, Université Paris-Saclay, F-94270 Le Kremlin-Bicêtre, France
3. Gustave Roussy, Université Paris-Saclay, Department of Medical Physics, F-94805, Villejuif, France
```
run the following comand (before executing this step) 

```
conda activate DS2nii 
```

NOTE :  possible to use for one folder or several processed in parralel

```
convert_one_patient(patient_path)
```
```
process_all_patients(path, depth,direct)
```


path : path to folder containing your patient data 
depth : depth at which you find patient folder
direct : bool, if your patient folders can be found direclty is path then True else False

output : the nifti files 

once you are done with the conversion don't forget to deactivate the environment

```
conda deactivate DS2nii 
```

#### convert_dicom_nrrd.py
#### export_to_nifti_solution_artefact



- preprocess, convert and analyze DICOM (CT and RTSTRUCT) database 
- check ring masks
- create ring masks 
- check and correct ring masks

The aim of this pipeline is to assess if RTSTRUCT contours are correct in a scenario where you have a tumor and a ring around the tumor. We define correct by the following standards :
- the ring englobes the tumor
- the ring overlaps with tumor :
  
--> 2mm inside the tumor's border

--> 2mm outside the tumor's border

if the tumor is too small ( diameter <= 2mm ) the ring mask completelly overlaps with the tumor : contains no hole. 

<p align="center"><img src="images/tumor_correct_overlap.png" align="middle" width="750" title="Correct Overlap Example" /></p>


The code detect the 2 scenarios outside of correct overlap as previously defined :
- complete overlap : the tumor is large enough (diameter>2mm) but has no hole
- no overlap : the ring doesn't overlap with the tumor 


## Preprocess, convert and analyze DICOM (CT and RTSTRUCT) files 




Produces a txt file with the list of CT series with no corresponding RTSTRUCT file

input : path to patient data

output : no_RTSTRUCT_file_series_list.txt a list of path to series with no corresponding RTSTRUCT


### Step 3 : Convert dicom to nifties 
   
run the following comand (before executing this step) 

```
conda activate DS2nii 
```

NOTE :  possible to use for one folder or several processed in parralel

input : folder path

output : the nifti files 

```
conda deactivate DS2nii 
```


### Step 4 : Further tidy the files within the serie folder to create 4 folders :

Optional step : Deleting external contours nifti files

input: yes/no

    - CT
    - RTSTRUCT
    - NIFTI
   

### Step 5 : Resample the nifti files to 1*1*1m³ pixel spacing 

NOTE : possible to use for one folder or several processed in parralel

input : folder path

output : the nifti files resampled with "RESAMPLED" added in the original filename


### delete_external_contours:

If you wish to delete nifti mask of external contours 

input : 

path to your data

depth : if the data path doesn't imediatly lead to patient folder provide the depth to reach patient folders for example if your data is organized in the following way :
Data folder/ center/ patient folders the depth would be 2

direct : bool  if True it means the data folder immediatly lead to patient folders

### rename_tx

If your nifti masks contain TX instead of T0 or T1 this allows to automatically rename them 


input : 

path to your data

depth : if the data path doesn't imediatly lead to patient folder provide the depth to reach patient folders for example if your data is organized in the following way :
Data folder/ center/ patient folders the depth would be 2

direct : bool  if True it means the data folder immediatly lead to patient folders

### check_number_off_components

This script allow to check the number of components of each mask in nifti format

input : 

path to your data

path of output file 

depth : if the data path doesn't imediatly lead to patient folder provide the depth to reach patient folders for example if your data is organized in the following way :
Data folder/ center/ patient folders the depth would be 2

direct : bool  if True it means the data folder immediatly lead to patient folders


```

more specific example usage :

```
# Step 1 with default settings
python main.py --path /data/patient_images --step 1

# Step 2 with specified output path
python main.py --path /data/patient_images --step 2 --output_path /data/output

# Generate report with all optional paths specified
python main.py --path /data/patient_images --step generate_report --output_path /data/output --complete_overlap_mask_path /data/masks/complete --no_overlap_mask_path /data/masks/no_overlap --same_size_mask_path /data/masks/same_size --check_ring_results_path /data/results/ring_checks

# Check number of components with default depth and direct settings
python main.py --path /data/patient_images --step check_number_off_components --output_path /data/output
```

## Check ring masks

This code allows to go over your masks (in the nifti format) and check if the overlap is correct between the ring and the tumor. 

input : 
path to your data, path for the output files
depth : if the data path doesn't imediatly lead to patient folder provide the depth to reach patient folders for example if your data is organized in the following way :
Data folder/ center/ patient folders the depth would be 2

direct : bool  if True it means the data folder immediatly lead to patient folders

outputs : in txt format at the desired path

- list of masks with no overlap  
- list of masks with complete overlap 
- list of masks where tumor and ring are the same size

WARNING : assumes your nifti files contain GTV in filename for tumor and ring in filename for ring

```
python3 check_rings_v2.py all_patients /path/to/input /path/to/output

```


NOTE : possible to use for one folder or several processed in parralel

input : folder path

outputs :
- list of masks with no overlap
- list of masks with complete overlap
- list of masks where tumor and ring are the same size
(the lists also will be printed in terminal)


```

python3 check_rings_v2.py folder /path/to/folder

```

## Create ring masks 

This code allows to go over your tumor masks and construct a ring mask file in nifti format with a correct overlap.

input : 
path to your data
depth : if the data path doesn't imediatly lead to patient folder provide the depth to reach patient folders for example if your data is organized in the following way :
Data folder/ center/ patient folders the depth would be 2
direct : bool  if True it means the data folder immediatly lead to patient folders

output : ring files with same name as tumor files replacing GTV with ring and adding "CREATED" in the filename 

function : process_all_patient(patient_path, depth, direct )

WARNING : assumes your data's architecture is the one defined in main.py


NOTE : if you have your own data architecture you can use the following command line to create ring masks  within a folder

input : folder path

outputs : nifti ring masks file with "GTV" replaced by ring and the addition of "CREATED" in filename 

function : process_patient(patient_path)

If you want to vizualize the created ring mask and compare with the original ring mask you can use the script "vizualize_created_masks.py" in utils.
inputs :
- original ring mask path
- created ring mask path
- image path 
- tumor mask path

```
python3 vizualize_created_masks.py <original_mask_path> <created_mask_path> <image_path> <tumor_path>

```

<p align="center"><img src="images/compare created and original mask.png" align="middle" width="750" title="Vizualize on scans" /></p>

<p align="center"><img src="images/compare zoomed in original and created masks.png" align="middle" width="750" title="Vizualize zoomed in on pixels of a slice" /></p>


## Check and correct ring masks

this code allows to go over your nifti files, evaluate if overlap between mask and tumor is correct and create a new ring mask nifti file if not. 

input : 
path to your data
depth : if the data path doesn't imediatly lead to patient folder provide the depth to reach patient folders for example if your data is organized in the following way :
Data folder/ center/ patient folders the depth would be 2
direct : bool  if True it means the data folder immediatly lead to patient folders

output : ring files with same name as tumor files replacing GTV with ring and adding "CREATED" in the filename 

function : process_all_patient(patient_path, depth, direct )

WARNING : assumes your data's architecture is the one defined in main.py

NOTE : if you have your own data architecture you can use the following command line to create ring masks when overlap is incorrect within a folder

input : folder path

outputs : nifti ring masks file with "GTV" replaced by ring and the addition of "CREATED" in filename 

function : process_patient(patient_path)


## Notes 

If you encounter import problems (a folder within the pipeline isn't recognized by python compiler) it means that the path to the pipeline isn't in the path used by your python compiler. You can fix that with the following code : (add it before the import that aren't working)

```
import sys 
sys.path.append("local path of cloned pipeline")
```

to facilitate this if you need to apply it to all the files in the pipeline you can run the following commands :

```
cd utils
python3 add_pipeline_path.py path/of/pipeline/folder/on/your/computer path/of/pipeline/folder/on/your/computer
```

