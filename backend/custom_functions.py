import os
import cv2
import numpy as np
import skimage.feature as skf
import skimage.color as skc
from skimage.filters import sobel
from skimage.transform import resize
from sklearn.decomposition import PCA
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

load_dotenv()

ELASTIC_URL = os.getenv('ELASTIC_URL')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_INDEX = os.getenv('ELASTIC_INDEX')

print("ELASTIC_URL:", os.getenv("ELASTIC_URL"))
print("ELASTIC_USERNAME:", os.getenv("ELASTIC_USERNAME"))
print("ELASTIC_PASSWORD:", os.getenv("ELASTIC_PASSWORD"))
print("ELASTIC_INDEX:", os.getenv("ELASTIC_INDEX"))

# Initialize Elasticsearch client
es = Elasticsearch(ELASTIC_URL,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)
es.info()

# Define image size dictionary
img_size = {'x': 128, 'y': 128}
bin_count = 8

# Function to add feature to Elasticsearch
def index_feature_to_elasticsearch(feature_dict):
    file_name = feature_dict['file']
    es.index(index=ELASTIC_INDEX, id=file_name, body=feature_dict)

def set_default(obj):
    if isinstance(obj, set):  # Convert sets to lists
        return list(obj)
    if isinstance(obj, np.ndarray):  # Convert NumPy arrays to lists
        return obj.tolist()
    if isinstance(obj, np.generic):  # Handle NumPy scalar types (e.g., np.float32, np.int32)
        return obj.item()
    if isinstance(obj, cv2.KeyPoint):  # Convert KeyPoint to a dictionary
        return {
            "x": obj.pt[0],   # X coordinate
            "y": obj.pt[1],   # Y coordinate
            "size": obj.size, # Size of the keypoint
            "angle": obj.angle,  # Angle of orientation
            "response": obj.response,  # Strength of keypoint
            "octave": obj.octave,  # Pyramid layer
            "class_id": obj.class_id  # Object class ID
        }
    raise TypeError(f"Type {type(obj)} not serializable")

# Pre-processing Functions
def resize_image(image, size=(img_size['x'], img_size['y'])):
    return cv2.resize(image, size)

def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def normalize_image(image):
    return (image / 255.0).astype(np.float32)

def histogram_equalization(image):
    gray = convert_to_grayscale(image)
    return cv2.equalizeHist(gray)

def denoise_image(image):
    return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)

def edge_detection(image):
    gray = convert_to_grayscale(image)
    return cv2.Canny(gray, 100, 200)

# 1. Color and Intensity Mean
def color_intensity_mean(image):
    b_mean, g_mean, r_mean = cv2.mean(image)[:3]  # Extract RGB mean values
    gray = convert_to_grayscale(image)
    intensity_mean = np.mean(gray)
    return r_mean, g_mean, b_mean, intensity_mean

# 2. Color and Intensity Histogram
def color_intensity_histogram(image, bins=bin_count):
    histograms = [cv2.calcHist([image], [i], None, [bins], [0, 256]).flatten() for i in range(3)]
    gray = convert_to_grayscale(image)
    intensity_hist = cv2.calcHist([gray], [0], None, [bins], [0, 256]).flatten()
    
    # Normalize histograms
    histograms = [hist / hist.sum() for hist in histograms]
    intensity_hist = intensity_hist / intensity_hist.sum()
    
    return histograms, intensity_hist

# 3. Opponent Color Axes Mean
def opponent_color_mean(image):
    R, G, B = cv2.split(image)
    RG = np.mean(R - G)
    B_RG = np.mean(2 * B - R - G)
    RGB = np.mean(R + G + B)
    return RG, B_RG, RGB

# 4. Opponent Color Histogram
def opponent_color_histogram(image, bins=bin_count):
    R, G, B = cv2.split(image)
    RG_hist = np.histogram(R - G, bins=bins, range=(-255, 255))[0]
    B_RG_hist = np.histogram(2 * B - R - G, bins=bins, range=(-255, 255))[0]
    RGB_hist = np.histogram(R + G + B, bins=bins, range=(0, 765))[0]
    
    # Normalize histograms
    RG_hist = RG_hist / RG_hist.sum()
    B_RG_hist = B_RG_hist / B_RG_hist.sum()
    RGB_hist = RGB_hist / RGB_hist.sum()
    
    return RG_hist, B_RG_hist, RGB_hist

# 5. GLCM Features
def glcm_features(image, dx, dy):
    gray = convert_to_grayscale(image)
    gray = (gray * 255).astype(np.uint8)  # Convert to uint8 for GLCM compatibility
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

# 6. HOG
def compute_hog(image, pixel_per_cell=16, cell_per_block=2, orientations=6):
    gray = convert_to_grayscale(image)
    hog = skf.hog(gray, pixels_per_cell=(pixel_per_cell, pixel_per_cell), 
        cells_per_block=(cell_per_block, cell_per_block), 
        orientations=orientations, feature_vector=True)
    
    # Round to 6 decimal places and convert to np.float32
    # hog_rounded = np.round(hog, decimals=6)  # Round to the desired precision
    hog_rounded = np.vectorize(lambda x: float(f"{x:.6f}"))(hog)  # Round to the desired precision

    return hog_rounded

# 7. Harris Corner Detector
def harris_corners(image, block_size=2, ksize=3, k=0.04, threshold=0.1):
    gray = convert_to_grayscale(image)
    gray = np.float32(gray)
    corners = cv2.cornerHarris(gray, block_size, ksize, k)
        
    pca = PCA(n_components=50)  # Keep top 50 principal components
    compressed_corners = pca.fit_transform(corners)

    # return corners
    return compressed_corners

# 8. GIST Descriptor (Simplified using Sobel)
def compute_gist(image, size=(img_size['x']//4, img_size['y']//4)):
    resized = resize(image, size)
    gray = skc.rgb2gray(resized)
    edges = sobel(gray)
    return edges.flatten()

# 9. SIFT
def compute_sift(image):
    gray = convert_to_grayscale(image)
    gray = (gray * 255).astype(np.uint8)  # Convert back to uint8
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    # return keypoints, descriptors

    pca = PCA(n_components=50)  # Keep top 50 principal components
    compressed_descriptors = pca.fit_transform(descriptors)
    # return descriptors
    return compressed_descriptors


# Will be Updated
def search_similar_images(image, feature_keys=['r_mean', 'g_mean', 'b_mean', 'intensity_mean'], top_n=10):
    image_rgb = image.copy()
    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
    if image is None:
        print("Error: Unable to read image.")
        return []
    
    image = resize_image(image)
    image = denoise_image(image)
    image = normalize_image(image)

    query_features = {}

    if 'r_mean' in feature_keys or 'g_mean' in feature_keys or 'b_mean' in feature_keys or 'intensity_mean' in feature_keys:
        r_mean, g_mean, b_mean, intensity_mean = color_intensity_mean(image)
        if 'r_mean' in feature_keys:
            query_features['r_mean'] = r_mean
        if 'g_mean' in feature_keys:
            query_features['g_mean'] = g_mean
        if 'b_mean' in feature_keys:
            query_features['b_mean'] = b_mean
        if 'intensity_mean' in feature_keys:
            query_features['intensity_mean'] = intensity_mean

    query = {
        "size": top_n,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": """
                        // Vector from the request
                        double r_mean = params.r_mean;
                        double g_mean = params.g_mean;
                        double b_mean = params.b_mean;
                        double intensity_mean = params.intensity_mean;

                        // Vector from the document
                        double doc_r_mean = doc['r_mean'].value;
                        double doc_g_mean = doc['g_mean'].value;
                        double doc_b_mean = doc['b_mean'].value;
                        double doc_intensity_mean = doc['intensity_mean'].value;

                        // Compute the dot product
                        double dot_product = (r_mean * doc_r_mean) + (g_mean * doc_g_mean) + (b_mean * doc_b_mean) + (intensity_mean * doc_intensity_mean);

                        // Compute the magnitude of the vectors
                        double doc_magnitude = Math.sqrt(Math.pow(doc_r_mean, 2) + Math.pow(doc_g_mean, 2) + Math.pow(doc_b_mean, 2) + Math.pow(doc_intensity_mean, 2));
                        double query_magnitude = Math.sqrt(Math.pow(r_mean, 2) + Math.pow(g_mean, 2) + Math.pow(b_mean, 2) + Math.pow(intensity_mean, 2));

                        // Compute the cosine similarity (dot product / (magnitude of query * magnitude of document))
                        double cosine_similarity = dot_product / (doc_magnitude * query_magnitude);

                        return cosine_similarity;
                    """,
                    "params": query_features
                }
            }
        }
    }


    response = es.search(index=ELASTIC_INDEX, body=query)
    similar_images = [{
        'file': hit["_source"]["file"],
        '_score': hit["_score"],
    } for hit in response["hits"]["hits"]]
    
    return similar_images

import numpy as np

def search_similar_images_from_keys(keys, feature_keys=['r_mean', 'g_mean', 'b_mean', 'intensity_mean'], top_n=10):
    if not keys:
        print("Error: No keys provided.")
        return []
    
    # Retrieve document data for the given keys
    docs = es.mget(index=ELASTIC_INDEX, body={"ids": keys})
    
    # Extract feature values
    feature_sums = {key: 0 for key in feature_keys}
    valid_docs = 0

    for doc in docs["docs"]:
        if doc.get("found", False):
            valid_docs += 1
            source = doc["_source"]
            for key in feature_keys:
                if key in source:
                    feature_sums[key] += source[key]

    if valid_docs == 0:
        print("Error: No valid documents found.")
        return []

    # Compute averages
    query_features = {key: feature_sums[key] / valid_docs for key in feature_keys if valid_docs > 0}

    # Elasticsearch query
    query = {
        "size": top_n,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": """
                        double r_mean = params.r_mean;
                        double g_mean = params.g_mean;
                        double b_mean = params.b_mean;
                        double intensity_mean = params.intensity_mean;

                        double doc_r_mean = doc['r_mean'].value;
                        double doc_g_mean = doc['g_mean'].value;
                        double doc_b_mean = doc['b_mean'].value;
                        double doc_intensity_mean = doc['intensity_mean'].value;

                        double dot_product = (r_mean * doc_r_mean) + (g_mean * doc_g_mean) + (b_mean * doc_b_mean) + (intensity_mean * doc_intensity_mean);
                        double doc_magnitude = Math.sqrt(Math.pow(doc_r_mean, 2) + Math.pow(doc_g_mean, 2) + Math.pow(doc_b_mean, 2) + Math.pow(doc_intensity_mean, 2));
                        double query_magnitude = Math.sqrt(Math.pow(r_mean, 2) + Math.pow(g_mean, 2) + Math.pow(b_mean, 2) + Math.pow(intensity_mean, 2));

                        double cosine_similarity = dot_product / (doc_magnitude * query_magnitude);
                        return cosine_similarity;
                    """,
                    "params": query_features
                }
            }
        }
    }

    # Execute search
    response = es.search(index=ELASTIC_INDEX, body=query)
    similar_images = [{
        'file': hit["_source"]["file"],
        '_score': hit["_score"],
    } for hit in response["hits"]["hits"]]
    
    return similar_images
