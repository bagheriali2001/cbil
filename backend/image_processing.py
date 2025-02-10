import cv2
import numpy as np
import skimage.feature as skf
import skimage.color as skc
from skimage.filters import sobel
from skimage.transform import resize
import os
import pywt

from dotenv import load_dotenv
load_dotenv()
bin_count = int(os.getenv('BIN_COUNT'))
img_size_x = int(os.getenv('IMG_SIZE_X'))
img_size_y = int(os.getenv('IMG_SIZE_Y'))
img_size = {'x': img_size_x, 'y': img_size_y}

# Pre-processing Functions
def resize_image(image, size=(img_size['x'], img_size['y'])):
    return cv2.resize(image, size)

def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

def edge_detection(image):
    gray = convert_to_grayscale(image)
    return cv2.Canny(gray, 100, 200)

# Processing Functions

# 1. RGB Color Mean
def color_intensity_mean(image):
    b_mean, g_mean, r_mean = cv2.mean(image)[:3]
    gray = convert_to_grayscale(image)
    intensity_mean = np.mean(gray)
    return r_mean, g_mean, b_mean, intensity_mean

# 2. RGB Color Histogram
def color_intensity_histogram(image, bins=bin_count):
    blue_hist = cv2.calcHist([image], [0], None, [bins], [0, 256]).flatten()
    green_hist = cv2.calcHist([image], [1], None, [bins], [0, 256]).flatten()
    red_hist = cv2.calcHist([image], [2], None, [bins], [0, 256]).flatten()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    intensity_hist = cv2.calcHist([gray], [0], None, [bins], [0, 256]).flatten()
    
    blue_hist /= blue_hist.sum()
    green_hist /= green_hist.sum()
    red_hist /= red_hist.sum()
    intensity_hist /= intensity_hist.sum()
    
    return red_hist, green_hist, blue_hist, intensity_hist

# 3. GLCM Features
def glcm_features(image, dx, dy):
    gray = convert_to_grayscale(image)
    gray = (gray * 255).astype(np.uint8)
    glcm = skf.graycomatrix(gray, distances=[1], angles=[np.arctan2(dy, dx)], levels=256, symmetric=True, normed=True)
    features = {
        'energy': skf.graycoprops(glcm, 'energy')[0, 0],
        'contrast': skf.graycoprops(glcm, 'contrast')[0, 0],
        'entropy': -np.sum(glcm * np.log2(glcm + (glcm == 0))),
        'dissimilarity': skf.graycoprops(glcm, 'dissimilarity')[0, 0],
        'homogeneity': skf.graycoprops(glcm, 'homogeneity')[0, 0],
        'correlation': skf.graycoprops(glcm, 'correlation')[0, 0]
    }
    return features

def glcm_features_all_directions(image):
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]

    energy = []
    contrast = []
    entropy = []
    dissimilarity = []
    homogeneity = []
    correlation = []

    for dx, dy in directions:
        features = glcm_features(image, dx, dy)
        energy.append(features["energy"])
        contrast.append(features["contrast"])
        entropy.append(features["entropy"])
        dissimilarity.append(features["dissimilarity"])
        homogeneity.append(features["homogeneity"])
        correlation.append(features["correlation"])

    return {
        "energy": np.array(energy),
        "contrast": np.array(contrast),
        "entropy": np.array(entropy),
        "dissimilarity": np.array(dissimilarity),
        "homogeneity": np.array(homogeneity),
        "correlation": np.array(correlation)
    }

# 4. HOG
def compute_hog(image, pixel_per_cell=16, cell_per_block=2, orientations=6):
    gray = convert_to_grayscale(image)
    hog = skf.hog(gray, pixels_per_cell=(pixel_per_cell, pixel_per_cell), 
        cells_per_block=(cell_per_block, cell_per_block), 
        orientations=orientations, feature_vector=True)

    return hog

# 5. GIST Descriptor (Simplified using Sobel)
def compute_gist(image, size=(img_size['x']//4, img_size['y']//4)):
    resized = resize(image, size)
    gray = skc.rgb2gray(resized)
    edges = sobel(gray)
    return edges.flatten()

# 6. DCT Features
def extract_dct_features(image, block_size=16, num_coefficients=20):
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    image = np.float32(image) / 255.0
    
    dct_features = []

    height, width = image.shape
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            block = image[i:i+block_size, j:j+block_size]
            
            dct_block = cv2.dct(block)
            
            dct_features.extend(dct_block.flatten()[:num_coefficients])

    return np.array(dct_features)

# 7. Wavelet Features
def extract_wavelet_features(image, wavelet='db1', level=3):
    coeffs2 = pywt.dwt2(image, wavelet, level)
    
    cA, (cH, cV, cD) = coeffs2
    
    features = []
    
    for coeff in [cA, cH, cV, cD]:
        energy = np.sum(coeff**2)
        std_dev = np.std(coeff)
        mean = np.mean(coeff)
        
        features.extend([energy, std_dev, mean])
    
    return np.array(features)

# 8. Harris Corner Detector
def harris_corners(image, block_size=2, ksize=3, k=0.04, threshold=0.1):
    image2 = image.copy()
    image2 = resize_image(image2, (32, 32))

    gray = convert_to_grayscale(image2)
    gray = np.float32(gray)
    
    corners = cv2.cornerHarris(gray, block_size, ksize, k)
    corners = (corners > threshold * corners.max()).astype(np.uint8) * 255
    
    corners_1d = corners.flatten()
    
    return corners_1d
