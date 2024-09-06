import SimpleITK as sitk
import numpy as np


def find_mask_slice(mask_path):

    mask = sitk.ReadImage(mask_path)
    arr_mask = sitk.GetArrayViewFromImage(mask)
    non_empty_slices_axial = np.where(arr_mask.any(axis=(1, 2)))[0]
    non_empty_slices_coronal = np.where(arr_mask.any(axis=(0, 2)))[0]
    non_empty_slices_sagittal = np.where(arr_mask.any(axis=(0, 1)))[0]

    if len(non_empty_slices_axial) == 0 or len(non_empty_slices_coronal) == 0 or len(non_empty_slices_sagittal) == 0:
        return None, None, None  # Mask is empty

    center_slice_axial = non_empty_slices_axial[len(non_empty_slices_axial) // 2]
    center_slice_coronal = non_empty_slices_coronal[len(non_empty_slices_coronal) // 2]
    center_slice_sagittal = non_empty_slices_sagittal[len(non_empty_slices_sagittal) // 2]  
   

    return center_slice_axial, center_slice_coronal, center_slice_sagittal


