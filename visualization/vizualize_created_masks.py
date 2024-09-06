import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt
import argparse

def visualize_slice(image, title='', slice_index=None):
    arr_image = sitk.GetArrayViewFromImage(image)
    if slice_index is None:
        slice_index = arr_image.shape[0] // 2
    plt.imshow(arr_image[slice_index], cmap='gray')
    plt.title(f'{title} - Slice {slice_index}')
    plt.show()

def find_mask_slice_old_version(mask):
    arr_mask = sitk.GetArrayViewFromImage(mask)
    non_empty_slices = np.where(arr_mask.any(axis=(1, 2)))[0]
    if len(non_empty_slices) == 0:
        return None  # Mask is empty
    center_slice = non_empty_slices[len(non_empty_slices) // 2]
    return center_slice

def find_mask_slice(mask):
    arr_mask = sitk.GetArrayViewFromImage(mask)
    for i in range(arr_mask.shape[0]):
        if np.any(arr_mask[i]):
            return i
    return None


def plot_masks_on_image(image, original_mask, created_mask, slice_index):
    arr_image = sitk.GetArrayViewFromImage(image)
    arr_original_mask = sitk.GetArrayViewFromImage(original_mask)
    arr_created_mask = sitk.GetArrayViewFromImage(created_mask)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    ax.imshow(arr_image[slice_index], cmap='gray')

    # Overlay the original mask in red
    original_mask_overlay = np.ma.masked_where(arr_original_mask[slice_index] == 0, arr_original_mask[slice_index])
    ax.imshow(original_mask_overlay, cmap='Reds', alpha=0.5)

    # Overlay the created mask in green
    created_mask_overlay = np.ma.masked_where(arr_created_mask[slice_index] == 0, arr_created_mask[slice_index])
    ax.imshow(created_mask_overlay, cmap='Greens', alpha=0.5)

    plt.title(f'Slice {slice_index}')
    plt.show()

def plot_masks_side_by_side(image, original_mask, created_mask, original_mask_slice_index,created_mask_slice_index):
    arr_image = sitk.GetArrayViewFromImage(image)
    arr_original_mask = sitk.GetArrayViewFromImage(original_mask)
    arr_created_mask = sitk.GetArrayViewFromImage(created_mask)

    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Plot image with original mask
    axes[0].imshow(arr_image[original_mask_slice_index], cmap='gray')
    red_mask = np.zeros_like(arr_image[original_mask_slice_index])
    red_mask[arr_original_mask[original_mask_slice_index] > 0] = 1
    red_overlay = np.zeros((arr_image.shape[1], arr_image.shape[2], 3))
    red_overlay[..., 0] = red_mask  # Red channel
    axes[0].imshow(red_overlay, alpha=0.5)
    axes[0].set_title(f'Original Mask - Slice {original_mask_slice_index}')

    # Plot image with created mask
    axes[1].imshow(arr_image[created_mask_slice_index], cmap='gray')
    green_mask = np.zeros_like(arr_image[created_mask_slice_index])
    green_mask[arr_created_mask[created_mask_slice_index] > 0] = 1
    green_overlay = np.zeros((arr_image.shape[1], arr_image.shape[2], 3))
    green_overlay[..., 1] = green_mask  # Green channel
    axes[1].imshow(green_overlay, alpha=0.5)
    axes[1].set_title(f'Created Mask - Slice {created_mask_slice_index}')

    plt.show()

def find_bounding_box(mask):
    arr_mask = sitk.GetArrayFromImage(mask)
    non_zero_coords = np.argwhere(arr_mask)
    min_coords = non_zero_coords.min(axis=0)
    max_coords = non_zero_coords.max(axis=0)
    return min_coords, max_coords

def plot_zoomed_masks_side_by_side(original_mask, created_mask,original_mask_slice_index,created_mask_slice_index):
    arr_original_mask = sitk.GetArrayViewFromImage(original_mask)
    arr_created_mask = sitk.GetArrayViewFromImage(created_mask)  

    # Find the bounding box for the original mask
    min_coords_original, max_coords_original = find_bounding_box(original_mask)
    min_coords_created, max_coords_created = find_bounding_box(created_mask)

    # Create subplots
    fig, axes = plt.subplots(1, 2, figsize=(20, 10))

    # Zoom into the region of interest
    min_z_original, min_y_original, min_x_original = min_coords_original
    max_z_original, max_y_original, max_x_original = max_coords_original
    min_z_created, min_y_created, min_x_created = min_coords_created
    max_z_created, max_y_created, max_x_created = max_coords_created

    # Plot original mask zoomed in
    zoomed_original = arr_original_mask[original_mask_slice_index, min_y_original:max_y_original+1, min_x_original:max_x_original+1]
    axes[0].imshow(zoomed_original, cmap='Reds', alpha=0.5)
    axes[0].set_title('Zoomed Original Mask')
    axes[0].axis('off')

    # Plot created mask zoomed in
    zoomed_created = arr_created_mask[created_mask_slice_index, min_y_created:max_y_created+1, min_x_created:max_x_created+1]
    axes[1].imshow(zoomed_created, cmap='Greens', alpha=0.5)
    axes[1].set_title('Zoomed Created Mask')
    axes[1].axis('off')

    plt.show()


def plot_zoomed_masks_side_by_side_v2(original_mask, created_mask, tumor_mask, original_mask_slice_index, created_mask_slice_index, tumor_mask_index):
    arr_original_mask = sitk.GetArrayViewFromImage(original_mask)
    arr_created_mask = sitk.GetArrayViewFromImage(created_mask)
    arr_tumor_mask = sitk.GetArrayViewFromImage(tumor_mask)

    # Find the bounding box for the original mask
    min_coords_original, max_coords_original = find_bounding_box(original_mask)
    min_coords_created, max_coords_created = find_bounding_box(created_mask)
    min_coords_tumor, max_coords_tumor = find_bounding_box(tumor_mask)

    # Create subplots
    fig, axes = plt.subplots(1, 3, figsize=(30, 10))

    # Zoom into the region of interest for original mask
    min_z_original, min_y_original, min_x_original = min_coords_original
    max_z_original, max_y_original, max_x_original = max_coords_original

    # Plot original mask zoomed in
    zoomed_original = arr_original_mask[original_mask_slice_index, min_y_original:max_y_original+1, min_x_original:max_x_original+1]
    axes[0].imshow(zoomed_original, cmap='Reds', alpha=0.5)
    axes[0].set_title('Zoomed Original Mask')
    axes[0].axis('off')

    # Zoom into the region of interest for created mask
    min_z_created, min_y_created, min_x_created = min_coords_created
    max_z_created, max_y_created, max_x_created = max_coords_created

    # Plot created mask zoomed in
    zoomed_created = arr_created_mask[created_mask_slice_index, min_y_created:max_y_created+1, min_x_created:max_x_created+1]
    axes[1].imshow(zoomed_created, cmap='Greens', alpha=0.5)
    axes[1].set_title('Zoomed Created Mask')
    axes[1].axis('off')

    # Zoom into the region of interest for tumor mask
    min_z_tumor, min_y_tumor, min_x_tumor = min_coords_tumor
    max_z_tumor, max_y_tumor, max_x_tumor = max_coords_tumor

    # Plot tumor mask zoomed in
    zoomed_tumor = arr_tumor_mask[tumor_mask_index, min_y_tumor:max_y_tumor+1, min_x_tumor:max_x_tumor+1]
    axes[2].imshow(zoomed_tumor, cmap='Blues', alpha=0.5)
    axes[2].set_title('Zoomed Tumor Mask')
    axes[2].axis('off')

    plt.show()


def main(original_mask_path, created_mask_path, resampled_image_path,tumor_path):
    
    # Load the images and masks
    original_mask = sitk.ReadImage(original_mask_path)
    created_mask = sitk.ReadImage(created_mask_path)
    resampled_image = sitk.ReadImage(resampled_image_path)
    tumor_mask = sitk.ReadImage(tumor_path)

    original_mask_slice_index = find_mask_slice(original_mask)
    created_mask_slice_index = find_mask_slice(created_mask)
    tumor_index = find_mask_slice(tumor_mask)
    if original_mask_slice_index != created_mask_slice_index :
        print("WARNING the created mask and the original mask aren't on the same slice !")
        print("original :",original_mask_slice_index)
        print("created :", created_mask_slice_index)  
        print("tumor :", tumor_index)  
    
    if original_mask_slice_index is not None and created_mask_slice_index is not None:
        plot_masks_on_image(resampled_image, original_mask, created_mask, original_mask_slice_index)
        plot_masks_side_by_side(resampled_image, original_mask, created_mask, original_mask_slice_index,created_mask_slice_index)
        #plot_zoomed_masks_side_by_side(original_mask, created_mask, original_mask_slice_index,created_mask_slice_index)
        if tumor_index is not None :
            plot_zoomed_masks_side_by_side_v2(original_mask, created_mask,tumor_mask, original_mask_slice_index,created_mask_slice_index, tumor_index)
    else:
        print("Original mask is empty.")
    return



