import SimpleITK as sitk
import pywt

def apply_gaussian_filter(image,sigma):
    log_filter = sitk.LaplacianRecursiveGaussianImageFilter()
    log_filter.SetSigma(sigma)
    log_image = log_filter.Execute(image)
    log_image.CopyInformation(image)
    return log_image

def apply_wavelet_filter(image,wavelet_type):
    image_array = sitk.GetArrayFromImage(image)
    coeffs = pywt.wavedecn(image_array, wavelet_type)
    wavelet_image_array = pywt.waverecn(coeffs, wavelet_type)
    wavelet_image = sitk.GetImageFromArray(wavelet_image_array)
    wavelet_image.CopyInformation(image)
    return wavelet_image