import numpy as np

def calculate_glrlm_features(glrlm_matrix, filter_name):
    """
    Calculate the GLRLM features SRHGE, LGRE, SRLGE, and LRHGE.
    
    Parameters:
        glrlm_matrix (numpy.ndarray): 3D GLRLM matrix with shape (Ng, Nr, Na).
        filter_name (str): Filter name to be appended to the feature keys.
    
    Returns:
        dict: Dictionary containing the calculated feature values.
    """
    srhge_values = []
    lgre_values = []
    srlge_values = []
    lrlge_values = []

    Ng, Nr, Na = glrlm_matrix.shape
    print("values in glrlm matrix :",np.unique(glrlm_matrix))

    for a in range(Na):
        glrlm = glrlm_matrix[:, :, a]    
        H = np.sum(glrlm)  # Total number of homogeneous runs in the VOI
        print("number of runs for this angle :", H)

        if H == 0:
            continue  # Skip this angle if there are no runs

        srhge = 0
        lgre = 0
        srlge = 0
        lrlge = 0

        for i in range(Ng):
            for j in range(Nr):
                value = glrlm[i, j]
                if value != 0:
                    srhge += (value * ((i + 1) ** 2)) / ((j + 1) ** 2)
                    lgre += value / ((i + 1) ** 2)
                    srlge += value / (((i + 1) ** 2) * ((j + 1) ** 2))
                    lrlge += (value * ((j + 1) ** 2)) / ((i + 1) ** 2)

        # normalization
        srhge_values.append(srhge / H)
        lgre_values.append(lgre / H)
        srlge_values.append(srlge / H)
        lrlge_values.append(lrlge / H)
        print("srhge :", srhge)

    features = {
        "SRHGE_" + filter_name: np.mean(srhge_values) if srhge_values else 0,
        "LGRE_" + filter_name: np.mean(lgre_values) if lgre_values else 0,
        "SRLGE_" + filter_name: np.mean(srlge_values) if srlge_values else 0,
        "LRLGE_" + filter_name: np.mean(lrlge_values) if lrlge_values else 0
    }
    
    return features

