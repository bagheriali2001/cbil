import cv2
import numpy as np
import os
from elasticsearch import Elasticsearch
from image_processing import resize_image, denoise_image, color_intensity_mean, color_intensity_histogram, glcm_features_all_directions, compute_hog, compute_gist, extract_dct_features, extract_wavelet_features, harris_corners

from dotenv import load_dotenv
load_dotenv()
ELASTIC_URL = os.getenv('ELASTIC_URL')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_INDEX = os.getenv('ELASTIC_INDEX')
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', 'images')

print("ELASTIC_URL:", ELASTIC_URL)
print("ELASTIC_USERNAME:", ELASTIC_USERNAME)
print("ELASTIC_PASSWORD:", ELASTIC_PASSWORD)
print("ELASTIC_INDEX:", ELASTIC_INDEX)
print("IMAGE_FOLDER:", IMAGE_FOLDER)

es = Elasticsearch(ELASTIC_URL,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)
es.info()

def index_feature_to_elasticsearch(feature_dict):
    file_name = feature_dict['file']
    es.options(request_timeout=30).index(index=ELASTIC_INDEX, id=file_name, body=feature_dict)

def get_features (image, image_path):
    image = resize_image(image)
    image = denoise_image(image)

    r_mean, g_mean, b_mean, i_mean = color_intensity_mean(image)
    r_hist, g_hist, b_hist, i_hist = color_intensity_histogram(image)
    features = glcm_features_all_directions(image)
    hog = compute_hog(image)
    gist = compute_gist(image)
    dct = extract_dct_features(image)
    wavelet = extract_wavelet_features(image)
    corners = harris_corners(image)

    feature = {
        'file': image_path,
        'r_mean': r_mean,
        'g_mean': g_mean,
        'b_mean': b_mean,
        'i_mean': i_mean,
        'r_hist': r_hist,
        'g_hist': g_hist,
        'b_hist': b_hist,
        'i_hist': i_hist,
        'energy': features['energy'],
        'contrast': features['contrast'],
        'entropy': features['entropy'],
        'dissimilarity': features['dissimilarity'],
        'homogeneity': features['homogeneity'],
        'correlation': features['correlation'],
        'hog': hog,
        'gist': gist,
        'dct': dct,
        'wavelet': wavelet,
        'corners': corners,
    }

    return feature


def process_images_in_folder_to_elastic(folder_path):
    i = 1
    process_files = False
    start_from = 0
    files = os.listdir(folder_path)
    files.sort()

    for filename in files:
        print(f"{i} {process_files} - File to Process: {filename}               ", end="\r")
        if (process_files):
            if filename.lower().endswith(('png', 'jpg', 'jpeg', 'bmp')):
                image_path = os.path.join(folder_path, filename)
                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                feature = get_features(image, filename)

                index_feature_to_elasticsearch(feature)
        elif i == start_from:
            process_files = True
            
        i += 1

process_images_in_folder_to_elastic(IMAGE_FOLDER)