import numpy as np
from numba import njit
import time
from tqdm import tqdm
import SimpleITK as sitk

# Define the 13 directions as (dx, dy, dz) tuples
directions = np.array([
    (1, 0, 0),   # x-direction
    (0, 1, 0),   # y-direction
    (0, 0, 1),   # z-direction
    (1, 1, 0),   # xy-plane diagonal
    (-1, 1, 0),  # xy-plane diagonal
    (1, 0, 1),   # xz-plane diagonal
    (-1, 0, 1),  # xz-plane diagonal
    (0, 1, 1),   # yz-plane diagonal
    (0, -1, 1),  # yz-plane diagonal
    (1, 1, 1),   # Main diagonal
    (-1, -1, 1), # Main diagonal
    (1, -1, 1),  # Diagonal planes perpendicular to main diagonal
    (-1, 1, 1)   # Diagonal planes perpendicular to main diagonal
])

def is_valid_index(x, y, z, shape):
    """Check if the given index is valid within the 3D array shape."""
    return 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]

def iterate_3d_array_by_directions(array):
    shape = array.shape
    for direction in directions:
        dx, dy, dz = direction
        print(f"Direction {direction}:")
        for z in range(shape[2]):
            for y in range(shape[1]):
                for x in range(shape[0]):
                    nx, ny, nz = x, y, z
                    start_value = array[nx, ny, nz]
                    run_length = 0
                    run = []
                    while is_valid_index(nx, ny, nz, shape):
                        current_value = array[nx, ny, nz]
                        if current_value == start_value:
                            run_length += 1
                        run.append((nx, ny, nz, current_value))
                        # Move to the next voxel in the given direction
                        nx += dx
                        ny += dy
                        nz += dz
                    # Print the path for the current direction and voxel
                    if len(run) > 1:  # Only print if the run contains more than one voxel
                        print(f"Starting at voxel ({x}, {y}, {z}) with value {start_value}: ")                        
                        for next in range(len(run)):
                            position = run[next][0], run[next][1], run[next][2]
                            value_at_position = run[next][3]                        
                            print(f"-- next position {position} -> : {value_at_position}")
                        print(f"Run length: {run_length}")
                        
def compute_glrlm(array):
    shape = array.shape
    max_intensity = array.max()
    max_run_length = max(shape)  # Maximum possible run length
    print("max i :", max_intensity)
    print("max j :",max_run_length)

    # Initialize GLRLM for each direction
    glrlms = []

    for direction in tqdm(directions, total=len(directions)):
        dx, dy, dz = direction
        # Initialize the GLRLM matrix for the current direction
        glrlm = np.zeros((max_intensity + 1, max_run_length), dtype=int)
        #print(f"Direction {direction}:")
        
        for z in range(shape[2]):
            for y in range(shape[1]):
                for x in range(shape[0]):
                    nx, ny, nz = x, y, z
                    start_value = array[nx, ny, nz]
                    run_length = 0
                    run = []
                    
                    while is_valid_index(nx, ny, nz, shape):
                        current_value = array[nx, ny, nz]
                        if current_value == start_value:
                            run_length += 1
                        else:
                            # We break the run here, update the GLRLM
                            if run_length > 0:
                                if run_length > max_run_length :
                                    print("warning : run length excedes maximum ")
                                glrlm[start_value, run_length - 1] += 1
                            break
                        run.append((nx, ny, nz, current_value))
                        # Move to the next voxel in the given direction
                        nx += dx
                        ny += dy
                        nz += dz

                    # If run reaches the boundary, update the GLRLM
                    if run_length > 0:
                        glrlm[start_value, run_length - 1] += 1

                    # Print the path for the current direction and voxel
                    if len(run) > 1:  # Only print if the run contains more than one voxel
                        #print(f"Starting at voxel ({x}, {y}, {z}) with value {start_value}: ")
                        for next in range(len(run)):
                            position = run[next][0], run[next][1], run[next][2]
                            value_at_position = run[next][3]
                            #print(f"-- next position {position} -> : {value_at_position}")
                        #print(f"Run length: {run_length}")

        # Append the GLRLM for the current direction to the list
        glrlms.append(glrlm)

    # Print the GLRLMs for each direction
    #for i, glrlm in enumerate(glrlms):
        #print(f"\nGLRLM for direction {directions[i]}:")
        #print(glrlm)

    return glrlms

@njit
def is_valid_index_numba(x, y, z, shape):
    """Check if the given index is valid within the 3D array shape."""
    return 0 <= x < shape[0] and 0 <= y < shape[1] and 0 <= z < shape[2]

@njit(nopython=True, parallel=True)
def compute_glrlm_numba(array):
    shape = array.shape
    max_intensity = array.max()
    max_run_length = max(shape)  # Maximum possible run length

    # Initialize GLRLM for each direction
    glrlms = np.zeros((len(directions), max_intensity + 1, max_run_length), dtype=np.int32)

    for dir_index, (dx, dy, dz) in enumerate(directions):
        # Initialize the GLRLM matrix for the current direction
        glrlm = glrlms[dir_index]
        
        for z in range(shape[2]):
            for y in range(shape[1]):
                for x in range(shape[0]):
                    nx, ny, nz = x, y, z
                    start_value = array[nx, ny, nz]
                    run_length = 0
                    
                    while is_valid_index_numba(nx, ny, nz, shape):
                        current_value = array[nx, ny, nz]
                        if current_value == start_value:
                            run_length += 1
                        else:
                            # We break the run here, update the GLRLM
                            if run_length > 0:
                                glrlm[start_value, run_length - 1] += 1
                            break
                        # Move to the next voxel in the given direction
                        nx += dx
                        ny += dy
                        nz += dz

                    # If run reaches the boundary, update the GLRLM
                    if run_length > 0:
                        glrlm[start_value, run_length - 1] += 1

    return glrlms

# Example 3D array dimensions
array_shape = (100, 100, 56)
np.random.seed(42)  # Set seed for reproducibility
array_3d = np.random.randint(0, 5, size=array_shape)


start = time.time()
matrix = compute_glrlm(array_3d)
end = time.time()
print("time :", end-start)

start = time.time()
matrix = compute_glrlm_numba(array_3d)
end = time.time()
print("time numba :", end-start)