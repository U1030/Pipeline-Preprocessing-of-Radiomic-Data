import pydicom as dcm 
import os 
import numpy as np
import SimpleITK as sitk

"""
author Kilian Sambourg
"""


def GetImage(dicom_path,output_path,save=True):
    """
    Read Image from the folder with the dicoms files and can save it in nifti
    """
    print("--> ordering slices")
    # Order Dicom Slices
    im_list = os.listdir(dicom_path)
    slices_list = []
    for i in im_list:
        im_path = os.path.join(dicom_path,i)
        ds = dcm.dcmread(im_path,force=True)
        data_position = ds.ImagePositionPatient
        data_orientation = ds.ImageOrientationPatient
        xAxis = np.array([data_orientation[0], data_orientation[1], data_orientation[2]])
        yAxis = np.array([data_orientation[3], data_orientation[4], data_orientation[5]])
        zAxis = np.cross(xAxis, yAxis)
        vector_position = np.array([data_position[0], data_position[1], data_position[2]])
        data_z_position = np.dot(zAxis, vector_position)
        slices_list.append((data_z_position,i))
    sorted_slices_list = sorted(slices_list)
    print("--> create array")
    # Create Array
    dcm_array = []
    dcm_list = [j[1] for j in sorted_slices_list]
    for dicom in dcm_list:
        dcm_path = os.path.join(dicom_path,dicom)
        ds_tmp = dcm.dcmread(dcm_path)
        if ds_tmp.Modality.lower() == 'ct':
            dcm_array.append(ds_tmp.pixel_array*float(ds_tmp.RescaleSlope)+float(ds_tmp.RescaleIntercept))
        else:
            dcm_array.append(ds_tmp.pixel_array)
    dcm_array = np.array(dcm_array)
    print("--> create image")
    # Create Image
    ds0 = dcm.dcmread(os.path.join(dicom_path,dcm_list[0]))
    ds1 = dcm.dcmread(os.path.join(dicom_path,dcm_list[1]))
    img = sitk.GetImageFromArray(dcm_array)
    img.SetDirection([ds0.ImageOrientationPatient[0],ds0.ImageOrientationPatient[3],zAxis[0],
                      ds0.ImageOrientationPatient[1],ds0.ImageOrientationPatient[4],zAxis[1],
                      ds0.ImageOrientationPatient[2],ds0.ImageOrientationPatient[5],zAxis[2]])
    img.SetOrigin((ds0.ImagePositionPatient[0],ds0.ImagePositionPatient[1],ds0.ImagePositionPatient[2]))
    img.SetSpacing((ds0.PixelSpacing[0],ds0.PixelSpacing[1],ds1.ImagePositionPatient[2]-ds0.ImagePositionPatient[2]))
    print("--> save image")
    # Save Image
    if save == True:
        ID = str(ds.PatientID)
        date = ds.StudyDate
        modality = ds.Modality
        series = ds.SeriesInstanceUID
        output = os.path.join(output_path,ID,modality,date+'_'+series)        
        file_name = "image"+'_'+ID+'_'+date+'_'+series+'.nii.gz'
        sitk.WriteImage(img, os.path.join(output_path,file_name))    
    return img




