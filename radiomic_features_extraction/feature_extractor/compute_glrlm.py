import numpy as np
import SimpleITK as sitk
import preprocessing 
from numba import njit
import time 
import bounding_box

angles = np.array([
    1, 0, 0,  # x-direction
    0, 1, 0,  # y-direction
    0, 0, 1,  # z-direction
    1, 1, 0,  # xy-plane diagonal
    -1, 1, 0, # xy-plane diagonal
    1, 0, 1,  # xz-plane diagonal
    -1, 0, 1, # xz-plane diagonal
    0, 1, 1,  # yz-plane diagonal
    0, -1, 1, # yz-plane diagonal
    1, 1, 1,  # Main diagonal
    -1, -1, 1,# Main diagonal
    1, -1, 1, # Diagonal planes perpendicular to main diagonal
    -1, 1, 1  # Diagonal planes perpendicular to main diagonal
])

@njit
def calculate_glrlm(image, mask, size, bb, strides, Na, Nd, Ng, Nr,angles=angles):
    # Allocate space for the GLRLM
    glrlm = np.zeros((Ng, Nr, Na))

    # Calculate size of image array, and calculate index of lower bound of bounding box (`start_i`)
    Ni = size[0]
    start_i = bb[0] * strides[0]
    for d in range(1, Nd):
        start_i += bb[d] * strides[d]
        Ni *= size[d]   

    for a in range(Na):  # Iterate over angles to get the neighbours
        print('current angle :', angles[a],angles[a+1], angles[a+2])
        multiElement = 0
        # Lookup and count the number of dimensions where the angle != 0 (i.e. "Moving dimensions")
        # Moreover, check if we need to start at 0 (angle > 0) or at the end (size[d] - 1, angle < 0)
        cnt_mDim = 0
        mDims = []
        mDim_start = []
        for d in range(Nd):
            if angles[a * Nd + d] != 0:
                if angles[a * Nd + d] > 0:
                    mDim_start.append(bb[d])
                else:
                    mDim_start.append(bb[Nd + d])
                mDims.append(d)
                cnt_mDim += 1       

        # Iterate over the image (with the goal of getting all "start positions", i.e. from where we start the run)
        i = start_i
        while i < Ni:
           
            # Calculate the current index in each dimension and ensure it is within the bounding box.
            # (except dimension 0, handled below)
            for d in range(Nd-1, 0, -1):  # Iterate in reverse direction to handle strides from small to large
                cur_idx = (i % strides[d-1]) // strides[d]
                
                if cur_idx > bb[Nd + d]:
                    # Set i to the lower bound of the bounding box
                    i += (size[d] - cur_idx + bb[d]) * strides[d]
                elif cur_idx < bb[d]:
                    i += (bb[d] - cur_idx) * strides[d]

            cur_idx = i // strides[0]
           
            if cur_idx > bb[Nd]:  # No need to check < bb[d], as initialization sets this at bb[d]
                break  # Out-of-range in first dimension: end of bounding box reached
            
            # loop over moving dimensions to check if the current voxel is a valid starting voxel
            start_voxel_valid = False
            for md in range(cnt_mDim):
                d = mDims[md]
                if d == 0:
                    cur_idx = i // strides[d]
                else:
                    cur_idx = (i % strides[d-1]) // strides[d]

                if cur_idx == mDim_start[md]:
                    start_voxel_valid = True
                    break  # No need to check the rest, the voxel is valid

            if not start_voxel_valid:
                
                # Current voxel is not a starting position for any of the moving dimensions!
                # Skip to a valid index by ensuring the fastest changing moving dimension is set to a valid start position.
                md = cnt_mDim - 1
                d = mDims[md]  # Get the last moving dimension (i.e. the moving dimension with the smallest stride)
                # Advance i in the last moving dimension to a valid start position.
                cur_idx = (i % strides[d-1]) // strides[d]
                i += ((mDim_start[md] - cur_idx + size[d]) % size[d]) * strides[d]  # Skip the rest of the voxels in this moving dimension
                if d > 1:
                    d -= 1
                    for d in range(d, 0, -1):
                        cur_idx = (i % strides[d-1]) // strides[d]
                        if cur_idx > bb[Nd + d]:
                            i += (size[d] - cur_idx + bb[d]) * strides[d]
                        elif cur_idx < bb[d]:
                            i += (bb[d] - cur_idx) * strides[d]
                if i // strides[0] > bb[Nd]:
                    break  # Out-of-range in first dimension: end of bounding box reached

            # Run Forest, Run! Start at the current index and advance using the angle until exiting the image.
            j = i
            gl = -1
            rl = 0
            elements = 0           
            
            while True:
                x = i // strides[0]
                y = (i % strides[1-1]) // strides[1]
                z = (i % strides[2-1]) // strides[2]
                print('current position :',x,",",y,",",z)
                
                # Check if j belongs to the mask (i.e. part of some run)
                if mask[j]:
                    elements += 1  # count the number of voxels in this run
                    if gl == -1:  # No run initialized, start a new one
                        gl = image[j]
                    elif image[j] == gl:  # j is part of the current run, increase the length
                        rl += 1
                    else:  # j is not part of the run, end current run and start new one
                        glrlm_idx = a + rl * Na + (gl - 1) * Na * Nr
                        if gl > 0 or glrlm_idx < Ng * Nr * Na:                            
                            glrlm[gl - 1, rl, a] += 1
                        gl = image[j]
                        rl = 0
                elif gl > -1:  # end current run
                    glrlm_idx = a + rl * Na + (gl - 1) * Na * Nr
                    if gl > 0 or glrlm_idx < Ng * Nr * Na:                       
                        glrlm[gl - 1, rl, a] += 1
                    gl = -1
                    rl = 0

                # Advance to the next voxel
                for md in range(cnt_mDim):
                    d = mDims[md]
                    if d == 0:
                        cur_idx = j // strides[d]
                    else:
                        cur_idx = (j % strides[d-1]) // strides[d]
                    if cur_idx + angles[a * Nd + d] < bb[d] or cur_idx + angles[a * Nd + d] > bb[Nd + d]:
                        j = i  # Set j to i to signal the while loop to exit too.
                        break  # Out of range! Run is done, so exit the loop
                    j += angles[a * Nd + d] * strides[d]
                    
                if j == i:
                    break

            if gl > -1:  # end current run (this is the case when the last voxel of the run was included in the mask)
                glrlm_idx = a + rl * Na + (gl - 1) * Na * Nr
                if gl > 0 or glrlm_idx < Ng * Nr * Na:
                    glrlm[gl - 1, rl, a] += 1

            if elements > 1:  # multiple elements found in this run. Ensure multiElement is set to true;
                multiElement = 1
            
            # Ensure i is incremented
            i += 1            

        if not multiElement:  # Segmentation is 2D for this angle, remove it.
            for glrlm_idx in range(Ng):
                glrlm[glrlm_idx, 0, a] = 0

    return glrlm

"""

Inputs

    image: A 1D array of integers representing the image data. Each element in the array corresponds to a voxel (a pixel in 3D).
    
    mask: A 1D array of the same size as image, where each element is a boolean indicating whether the corresponding voxel is 
    part of the region of interest (ROI).
    
    size: A list of integers representing the dimensions of the image array (e.g., [width, height, depth]).
    
    bb: A list of integers representing the bounding box for the region of interest. It contains two values for each dimension: 
    the starting index and the ending index (e.g., [start_x, start_y, start_z, end_x, end_y, end_z]).
    
    strides: A list of integers representing the strides for each dimension. The stride is the step size to move from one element 
    to the next along each dimension.
    
    angles: A list of integers representing the directions (angles) to consider when calculating the GLRLM. Each angle is specified 
    by an offset for each dimension.
    
    Na: An integer representing the number of angles.
    
    Nd: An integer representing the number of dimensions.
   
    Ng: An integer representing the number of gray levels in the image.
    
    Nr: An integer representing the maximum run length.
"""


def process_image_mask(image_path, mask_path):
    start = time.time()
    discretized_image, rescaled_mask = preprocessing.preprocess_image(image_path=image_path, mask_path=mask_path, filter_type="original", filter_param=None)
    end = time.time()
    print(f'Preprocessing time : {end-start}s')

    final_mask_arr = sitk.GetArrayFromImage(rescaled_mask)
    final_image_arr = sitk.GetArrayFromImage(discretized_image)

    # Find the indices where the mask value is 1
    indices = np.argwhere(final_mask_arr == 1)
    print("number of voxels in mask :", len(indices))

    # Get the minimum and maximum indices for each dimension
    min_indices = indices.min(axis=0)
    max_indices = indices.max(axis=0)

    # Create the bounding box list: [start_x, start_y, start_z, end_x, end_y, end_z]
    bb = np.array([min_indices[2], min_indices[1], min_indices[0], max_indices[2], max_indices[1], max_indices[0]])

    # Print or return the bounding box
    print("Bounding Box:", bb)

    # Find a slice with the mask
    slice_index = np.unique(indices[:, 0])[0]  # Taking the first slice where the mask is present
    bounding_box.plot_with_image_bb_mask(image=final_image_arr, mask=final_mask_arr, bb=bb,slice_index=slice_index)
    bounding_box.plot_bb_region_with_mask(image=final_image_arr, mask=final_mask_arr, bb=bb)

    size = final_image_arr.shape

    print("size : ", size)

    flattened_image = final_image_arr.ravel()
    flattened_mask = final_mask_arr.ravel()

    print("image :", flattened_image)
    print("mask :", flattened_mask)

    stride_x = size[1]*size[2]
    stride_y = size[2]
    stride_z = 1

    strides = np.array([stride_x,stride_y,stride_z])

    print("strides :", strides)

    Na = len(angles) // 3

    Nd = len(size)

    Ng = len(np.unique(flattened_image))

    Nr = max(size)

    print('Na :', Na)
    print("Nd :", Nd)
    print('Ng :', Ng)
    print("Nr :", Nr)

    glrlm = calculate_glrlm(flattened_image, flattened_mask, size, bb, strides, Na, Nd, Ng, Nr)

    return glrlm

   

# Fixed 3D image array (4x4x4)
image_array = np.array([
    [[1, 2, 3, 4], [1, 1, 1, 2], [2, 3, 4, 1], [4, 4, 2, 1]],
    [[2, 3, 1, 4], [1, 2, 3, 1], [1, 1, 1, 4], [2, 3, 4, 1]],
    [[3, 1, 2, 4], [1, 3, 4, 2], [4, 4, 1, 1], [2, 2, 3, 4]],
    [[4, 2, 1, 3], [4, 4, 1, 2], [3, 2, 1, 4], [1, 1, 2, 3]]
])

# Fixed 3D mask array (4x4x4)
mask_array = np.array([
    [[1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 0], [1, 1, 0, 0]],
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]],
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 0, 0], [1, 1, 1, 1]],
    [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]]
])

# Calculate bounding box
indices = np.argwhere(mask_array == 1)
min_indices = indices.min(axis=0)
max_indices = indices.max(axis=0)
bb = np.array([min_indices[2], min_indices[1], min_indices[0], max_indices[2], max_indices[1], max_indices[0]])

# Print the bounding box
print("Bounding Box:", bb)

size = image_array.shape
flattened_image = image_array.ravel()
flattened_mask = mask_array.ravel()

stride_x = size[1] * size[2]
stride_y = size[2]
stride_z = 1
strides = np.array([stride_x, stride_y, stride_z])

# Angles and dimensions

Na = len(angles) // 3
Nd = len(size)
Ng = len(np.unique(flattened_image))
Nr = max(size)

print("Na:", Na)
print("Nd:", Nd)
print("Ng:", Ng)
print("Nr:", Nr)


# Calculate GLRLM
glrlm = calculate_glrlm(flattened_image, flattened_mask, size, bb, strides, Na, Nd, Ng, Nr)

# Print the resulting GLRLM
print("GLRLM Matrix:")
print(glrlm)


