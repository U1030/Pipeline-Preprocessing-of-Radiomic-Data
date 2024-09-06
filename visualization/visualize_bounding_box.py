from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np


# Plotting
def plot_with_overlay(image, mask, slice_index, title='Overlay'):
    plt.imshow(image[slice_index], cmap='gray')
    plt.imshow(mask[slice_index], cmap='jet', alpha=0.5)
    plt.title(title)
    plt.colorbar()
    plt.show()

def plot_with_bb(image, bb, slice_index, title='Bounding Box'):
    """
    for bb with size dependant on mask
    """
    fig, ax = plt.subplots(1)
    ax.imshow(image[slice_index], cmap='gray')    
    # Extract bounding box coordinates
    x_start, y_start, z_start, x_end, y_end, z_end = bb    
    # Coordinates for rectangle in 2D slice
    rect_x = x_start
    rect_y = y_start
    rect_width = x_end - x_start
    rect_height = y_end - y_start    
    # Create the rectangle patch
    rect = patches.Rectangle((rect_x, rect_y), rect_width, rect_height, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)    
    plt.title(title)
    plt.show()

def plot_bb_region(image, bb, title='BB Region'):
    # Extract the region within the bounding box
    x_start, y_start, z_start, x_end, y_end, z_end = bb
    region = image[z_start:z_end+1, y_start:y_end+1, x_start:x_end+1]
    
    # Find the middle slice of the extracted region for visualization
    mid_slice = region.shape[0] // 2
    plt.imshow(region[mid_slice], cmap='gray')
    plt.title(title)
    plt.colorbar()
    plt.show()

def plot_bb_region_with_mask(image, mask, bb, title='BB Region and overlayed mask'):
    # Extract the region within the bounding box
    x_start, y_start, z_start, x_end, y_end, z_end = bb
    
    # Extract image and mask regions
    image_region = image[z_start:z_end+1, y_start:y_end+1, x_start:x_end+1]
    mask_region = mask[z_start:z_end+1, y_start:y_end+1, x_start:x_end+1]
    
    # Find the middle slice of the extracted region for visualization
    mid_slice = image_region.shape[0] // 2
    
    # Plot the image region
    plt.imshow(image_region[mid_slice], cmap='gray')
    
    # Overlay the mask on the same slice
    plt.imshow(mask_region[mid_slice], cmap='jet', alpha=0.5)
    
    plt.title(title)
    plt.colorbar()
    plt.show()


def plot_with_image_bb_mask(image, mask, bb, slice_index, title='Bounding Box'):
    fig, ax = plt.subplots(1)
    
    # Plot the image slice
    ax.imshow(image[slice_index], cmap='gray')
    
    # Overlay the mask on the image slice
    ax.imshow(mask[slice_index], cmap='jet', alpha=0.5)
    
    # Extract bounding box coordinates
    x_start, y_start, z_start, x_end, y_end, z_end = bb
    
    # Coordinates for rectangle in 2D slice
    rect_x = x_start
    rect_y = y_start
    rect_width = x_end - x_start
    rect_height = y_end - y_start
    
    # Create the rectangle patch
    rect = patches.Rectangle((rect_x, rect_y), rect_width, rect_height, linewidth=1, edgecolor='r', facecolor='none')
    ax.add_patch(rect)
    
    plt.title(title)
    plt.show()


def plot_bounding_box_on_image(image_array, start_index, end_index, slice_index=None, title="Bounding Box on Image"):
    if image_array.ndim != 3:
        raise ValueError("Image array must be 3D for visualization.")

    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)

    # Plot the specified slice or the middle slice if slice_index is not provided
    if slice_index is None:
        slice_index = image_array.shape[2] // 2

    # Extract the specified slice from the image
    image_slice = image_array[:, :, slice_index]
    
    # Plot the image slice
    ax.imshow(image_slice, cmap='gray')

    # Calculate bounding box coordinates for the specified slice
    x_min, y_min, z_min = start_index
    x_max, y_max, z_max = end_index
    
    # Bounding box coordinates for the 2D slice
    box_coords = [
        (x_min, y_min),
        (x_max, y_min),
        (x_max, y_max),
        (x_min, y_max),
        (x_min, y_min)
    ]
    
    # Plot the bounding box on the image slice
    box_coords = np.array(box_coords)
    ax.plot(box_coords[:, 0], box_coords[:, 1], color='red', linewidth=2)
    
    ax.set_title(title)
    ax.axis('off')
    plt.show()

def plot_images(original_image_array, cropped_image_array, title_original="Original Image", title_cropped="Cropped Image"):
    fig, axes = plt.subplots(1, 2, figsize=(12, 6))
    
    # Plot the original image (center slice)
    mid_slice = original_image_array.shape[2] // 2
    axes[0].imshow(original_image_array[:, :, mid_slice], cmap='gray')
    axes[0].set_title(title_original)
    axes[0].axis('off')
    
    # Plot the cropped image (center slice)
    mid_slice_cropped = cropped_image_array.shape[2] // 2
    axes[1].imshow(cropped_image_array[:, :, mid_slice_cropped], cmap='gray')
    axes[1].set_title(title_cropped)
    axes[1].axis('off')
    
    plt.show()


def plot_tumor_and_bounding_box(mask_tumor, start_index, end_index, title="Tumor and Bounding Box Visualization"):
    if mask_tumor.ndim != 3:
        raise ValueError("Mask array must be 3D for visualization.")
    
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    # Get the tumor voxel coordinates
    tumor_voxels = np.where(mask_tumor == 1)
    
    # Plot the tumor voxels
    ax.scatter(tumor_voxels[0], tumor_voxels[1], tumor_voxels[2], c='red', marker='o', label='Tumor Mask')
    
    # Define the 8 vertices of the bounding box
    vertices = np.array([
        [start_index[0], start_index[1], start_index[2]],
        [end_index[0], start_index[1], start_index[2]],
        [end_index[0], end_index[1], start_index[2]],
        [start_index[0], end_index[1], start_index[2]],
        [start_index[0], start_index[1], end_index[2]],
        [end_index[0], start_index[1], end_index[2]],
        [end_index[0], end_index[1], end_index[2]],
        [start_index[0], end_index[1], end_index[2]]
    ])

    # Define the 12 triangles composing the bounding box
    faces = [
        [vertices[0], vertices[1], vertices[2], vertices[3]],
        [vertices[4], vertices[5], vertices[6], vertices[7]],
        [vertices[0], vertices[1], vertices[5], vertices[4]],
        [vertices[2], vertices[3], vertices[7], vertices[6]],
        [vertices[0], vertices[3], vertices[7], vertices[4]],
        [vertices[1], vertices[2], vertices[6], vertices[5]]
    ]

    # Plot the bounding box
    poly3d = Poly3DCollection(faces, linewidths=1, edgecolors='k', alpha=0.3, facecolors='blue')
    ax.add_collection3d(poly3d)

    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_zlabel('Z-axis')
    ax.set_title(title)
    ax.legend()
    plt.show()