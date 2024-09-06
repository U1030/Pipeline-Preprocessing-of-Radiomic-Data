import SimpleITK as sitk


def print_roi_properties(nifti_path):
    # Load the NIfTI image
    image = sitk.ReadImage(nifti_path)
    # Get the origin and spacing information
    origin = image.GetOrigin()
    spacing = image.GetSpacing()
    size = image.GetSize()
    direction = image.GetDirection()
    # Compute the bounds of the ROI
    lower_bound = (origin[0], origin[1], origin[2])
    upper_bound = (
        origin[0] + size[0] * spacing[0],
        origin[1] + size[1] * spacing[1],
        origin[2] + size[2] * spacing[2]
    )
    # Print the ROI bounds
    print("ROI bounds (x, y, z image coordinate space):")
    print(f"Lower bound: {lower_bound}")
    print(f"Upper bound: {upper_bound}")
    print("size :", size)
    print('origin :', origin)
    print('spacing :', spacing)
    print('direction :', direction)
    return 
