import cv2
import numpy as np
import skimage.feature as skf
import skimage.color as skc
from skimage.filters import sobel
from skimage.transform import resize
import os
from elasticsearch import Elasticsearch
import pywt

from dotenv import load_dotenv

load_dotenv()

ELASTIC_URL = os.getenv('ELASTIC_URL')
ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_INDEX = os.getenv('ELASTIC_INDEX')
bin_count = os.getenv('BIN_COUNT')
img_size_x = os.getenv('IMG_SIZE_X')
img_size_y = os.getenv('IMG_SIZE_Y')
img_size = {'x': 128, 'y': 128}

print("ELASTIC_URL:", os.getenv("ELASTIC_URL"))
print("ELASTIC_USERNAME:", os.getenv("ELASTIC_USERNAME"))
print("ELASTIC_PASSWORD:", os.getenv("ELASTIC_PASSWORD"))
print("ELASTIC_INDEX:", os.getenv("ELASTIC_INDEX"))

# Initialize Elasticsearch client
es = Elasticsearch(ELASTIC_URL,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)
es.info()

# FROM IPYNB

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

############## FULLY COMPLETED ##############

# 1. RGB Color Mean
def color_intensity_mean(image):
    b_mean, g_mean, r_mean = cv2.mean(image)[:3]  # Extract RGB mean values
    gray = convert_to_grayscale(image)
    intensity_mean = np.mean(gray)
    return r_mean, g_mean, b_mean, intensity_mean

# 2. RGB Color Histogram
def color_intensity_histogram(image, bins=bin_count):
    # Compute histograms for each channel separately
    blue_hist = cv2.calcHist([image], [0], None, [bins], [0, 256]).flatten()
    green_hist = cv2.calcHist([image], [1], None, [bins], [0, 256]).flatten()
    red_hist = cv2.calcHist([image], [2], None, [bins], [0, 256]).flatten()

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    intensity_hist = cv2.calcHist([gray], [0], None, [bins], [0, 256]).flatten()
    
    # Normalize histograms
    blue_hist /= blue_hist.sum()
    green_hist /= green_hist.sum()
    red_hist /= red_hist.sum()
    intensity_hist /= intensity_hist.sum()
    
    return red_hist, green_hist, blue_hist, intensity_hist

# 3. GLCM Features
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

def glcm_features_all_directions(image):
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]  # Right, Down, Diagonal, Anti-diagonal

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
    # return hog
    
    hog_rounded = np.vectorize(lambda x: float(f"{x:.6f}"))(hog)
    return hog_rounded

# 5. GIST Descriptor (Simplified using Sobel)
def compute_gist(image, size=(img_size['x']//4, img_size['y']//4)):
    resized = resize(image, size)
    gray = skc.rgb2gray(resized)
    edges = sobel(gray)
    return edges.flatten()

# 6. DCT Features
def extract_dct_features(image, block_size=16, num_coefficients=20):
    # Convert the image to grayscale if it's a color image
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Normalize the image to range [0, 255] if it's not already
    image = np.float32(image) / 255.0
    
    # Prepare an empty list to store DCT coefficients
    dct_features = []

    # Iterate through the image in blocks
    height, width = image.shape
    for i in range(0, height, block_size):
        for j in range(0, width, block_size):
            # Extract a block of the image
            block = image[i:i+block_size, j:j+block_size]
            
            # Apply DCT on the block (2D DCT)
            dct_block = cv2.dct(block)
            
            # Flatten the block's DCT coefficients and add to feature list
            dct_features.extend(dct_block.flatten()[:num_coefficients])

    # Return the first 'num_coefficients' from the whole image's DCT blocks as features
    return np.array(dct_features)

# 7. Wavelet Features
def extract_wavelet_features(image, wavelet='db1', level=3):
    # Perform Discrete Wavelet Transform (DWT)
    coeffs2 = pywt.dwt2(image, wavelet, level)
    
    # Extract sub-bands from the wavelet decomposition
    cA, (cH, cV, cD) = coeffs2
    
    # You can perform further decomposition on each of the sub-bands if needed
    # For simplicity, we'll focus on the first level decomposition.
    
    # Flatten the coefficients into one-dimensional arrays
    features = []
    
    # Calculate features like energy, standard deviation, etc. from each sub-band
    for coeff in [cA, cH, cV, cD]:
        energy = np.sum(coeff**2)  # Energy of the sub-band
        std_dev = np.std(coeff)    # Standard deviation of the sub-band
        mean = np.mean(coeff)      # Mean of the sub-band
        
        # Append these features to the list
        features.extend([energy, std_dev, mean])
    
    # Convert the feature list to a numpy array
    return np.array(features)

# 8. Harris Corner Detector
def harris_corners(image, block_size=2, ksize=3, k=0.04, threshold=0.1):
    image2 = image.copy()
    image2 = resize_image(image2, (32, 32))

    # Convert the image2 to grayscale
    gray = convert_to_grayscale(image2)
    gray = np.float32(gray)
    
    # Apply the Harris corner detection
    corners = cv2.cornerHarris(gray, block_size, ksize, k)
    # Apply threshold to corners
    corners = (corners > threshold * corners.max()).astype(np.uint8) * 255
    
    # return corners
    # Convert the 2D corner array to a 1D array
    corners_1d = corners.flatten()  # or np.ravel()
    
    return corners_1d


# Will be Updated
def search_similar_images(image, feature_keys=['mean', 'hist', 'glcm', 'hog', 'gist', 'dct', 'wavelet', 'corners'], top_n=10):
    print("Using Features: ", feature_keys)
    image_rgb = image.copy()
    image_rgb = cv2.cvtColor(image_rgb, cv2.COLOR_BGR2RGB)
    if image is None:
        print("Error: Unable to read image.")
        return []
    
    image = resize_image(image)
    image = denoise_image(image)

    query_features = {}

    if 'mean' in feature_keys:
        r_mean, g_mean, b_mean, i_mean = color_intensity_mean(image)
        query_features['r_mean'] = r_mean
        query_features['g_mean'] = g_mean
        query_features['b_mean'] = b_mean
        query_features['i_mean'] = i_mean

    if 'hist' in feature_keys:
        r_hist, g_hist, b_hist, i_hist = color_intensity_histogram(image)
        query_features['r_hist'] = r_hist.tolist()
        query_features['g_hist'] = g_hist.tolist()
        query_features['b_hist'] = b_hist.tolist()
        query_features['i_hist'] = i_hist.tolist()

    if 'glcm' in feature_keys :
        features = glcm_features_all_directions(image)
        query_features['energy'] = features['energy'].tolist()
        query_features['contrast'] = features['contrast'].tolist()
        query_features['entropy'] = features['entropy'].tolist()
        query_features['dissimilarity'] = features['dissimilarity'].tolist()
        query_features['homogeneity'] = features['homogeneity'].tolist()
        query_features['correlation'] = features['correlation'].tolist()

    if 'hog' in feature_keys:
        hog = compute_hog(image)
        query_features['hog'] = hog

    if 'gist' in feature_keys:
        gist = compute_gist(image)
        query_features['gist'] = gist

    if 'dct' in feature_keys:
        dct = extract_dct_features(image)
        query_features['dct'] = dct

    if 'wavelet' in feature_keys:
        wavelet = extract_wavelet_features(image)
        query_features['wavelet'] = wavelet

    if 'corners' in feature_keys:
        corners = harris_corners(image)
        query_features['corners'] = corners


    query = {
        "size": top_n,
        "query": {
            "script_score": {
                "query": { "match_all": {} },
                "script": {
                    "source": """
                        double total_cosineSimilarity = 0.0;
                        double total_weight = 0.0;
                        
                        if (params.containsKey('r_mean')) {
                            // Query values
                            double a1 = params.r_mean;
                            double a2 = params.g_mean;
                            double a3 = params.b_mean;
                            double a4 = params.i_mean;

                            // Document values
                            double b1 = params._source.r_mean;
                            double b2 = params._source.g_mean;
                            double b3 = params._source.b_mean;
                            double b4 = params._source.i_mean;

                            // Compute dot product
                            double dot_product = (a1 * b1) + (a2 * b2) + (a3 * b3) + (a4 * b4);

                            // Compute norms
                            double query_norm = Math.sqrt((a1 * a1) + (a2 * a2) + (a3 * a3) + (a4 * a4));
                            double doc_norm = Math.sqrt((b1 * b1) + (b2 * b2) + (b3 * b3) + (b4 * b4));

                            // Compute cosine similarity
                            total_cosineSimilarity += (query_norm * doc_norm == 0) ? 0 : dot_product / (query_norm * doc_norm);
                            total_weight += (query_norm * doc_norm == 0) ? 0 : 1;
                        }
                        if (params.containsKey('r_hist')) {
                            total_cosineSimilarity += (cosineSimilarity(params.r_hist, 'r_hist') + cosineSimilarity(params.g_hist, 'g_hist') + cosineSimilarity(params.b_hist, 'b_hist') + cosineSimilarity(params.i_hist, 'i_hist')) / 4 * 1;
                            total_weight += 1;
                        }
                        if (params.containsKey('energy')) {
                            total_cosineSimilarity += (cosineSimilarity(params.energy, 'energy') + cosineSimilarity(params.contrast, 'contrast') + cosineSimilarity(params.entropy, 'entropy') + cosineSimilarity(params.dissimilarity, 'dissimilarity') + cosineSimilarity(params.homogeneity, 'homogeneity') + cosineSimilarity(params.correlation, 'correlation')) / 6 * 1;
                            total_weight += 1;
                        }
                        if (params.containsKey('hog')) {
                            total_cosineSimilarity += cosineSimilarity(params.hog, 'hog');
                            total_weight += 1;
                        }
                        if (params.containsKey('gist')) {
                            total_cosineSimilarity += cosineSimilarity(params.gist, 'gist');
                            total_weight += 1;
                        }
                        if (params.containsKey('dct')) {
                            total_cosineSimilarity += cosineSimilarity(params.dct, 'dct');
                            total_weight += 1;
                        }
                        if (params.containsKey('wavelet')) {
                            total_cosineSimilarity += cosineSimilarity(params.wavelet, 'wavelet');
                            total_weight += 1;
                        }
                        if (params.containsKey('corners')) {
                            total_cosineSimilarity += cosineSimilarity(params.corners, 'corners');
                            total_weight += 1;
                        }

                        // Compute the average similarity and add 1.0 for Elasticsearch ranking
                        return (total_weight > 0.0) ? (total_cosineSimilarity / total_weight) : 0.0;
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


def search_similar_images_from_keys(keys, feature_keys=['mean', 'hist', 'glcm', 'hog', 'gist', 'dct', 'wavelet', 'corners'], top_n=10):
    print("Using Features: ", feature_keys)
    
    feature_map = {
        'mean': [
            {
                'name': 'r_mean',
                'type': 'number'
            }, {
                'name': 'g_mean',
                'type': 'number'
            }, {
                'name': 'b_mean',
                'type': 'number'
            }, {
                'name': 'i_mean',
                'type': 'number'
            }
        ],
        'hist': [
            {
                'name': 'r_hist',
                'type': 'vector',
                'length': 16
            }, {
                'name': 'g_hist',
                'type': 'vector',
                'length': 16
            }, {
                'name': 'b_hist',
                'type': 'vector',
                'length': 16
            }, {
                'name': 'i_hist',
                'type': 'vector',
                'length': 16
            }
        ],
        'glcm': [
            {
                'name': 'energy',
                'type': 'vector',
                'length': 4
            }, {
                'name': 'contrast',
                'type': 'vector',
                'length': 4
            }, {
                'name': 'entropy',
                'type': 'vector',
                'length': 4
            }, {
                'name': 'dissimilarity',
                'type': 'vector',
                'length': 4
            }, {
                'name': 'homogeneity',
                'type': 'vector',
                'length': 4
            }, {
                'name': 'correlation',
                'type': 'vector',
                'length': 4
            }
        ],
        'hog': [
            {
                'name': 'hog',
                'type': 'vector',
                'length': 1176
            }
        ],
        'gist': [
            {
                'name': 'gist',
                'type': 'vector',
                'length': 1024
            }
        ], 
        'dct': [
            {
                'name': 'dct',
                'type': 'vector',
                'length': 1280
            }
        ], 
        'wavelet': [
            {
                'name': 'wavelet',
                'type': 'vector',
                'length': 12
            }
        ], 
        'corners': [
            {
                'name': 'corners',
                'type': 'vector',
                'length': 1024
            }
        ]
    }
    
    if not keys:
        print("Error: No keys provided.")
        return []
    
    # Retrieve document data for the given keys
    docs = es.mget(index=ELASTIC_INDEX, body={"ids": keys})
    
    # Initialize feature sums
    feature_sums = {}
    for feature in feature_keys:
        for item in feature_map[feature]:
            if item['type'] == 'number':
                feature_sums[item['name']] = 0
            elif item['type'] == 'vector':
                feature_sums[item['name']] = [0 for i in range(item['length'])]

    valid_docs = 0

    for doc in docs["docs"]:
        if doc.get("found", False):
            valid_docs += 1
            source = doc["_source"]
            
            for field in feature_sums:
                if field in source:
                    if isinstance(source[field], (int, float)):  # Scalar feature (like r_mean, g_mean)
                        feature_sums[field] += source[field]
                    else:  # Dense vector features (like hist, hog)
                        vector = np.array(source[field])
                        if feature_sums[field] is None:
                            feature_sums[field] = vector  # Initialize
                        else:
                            feature_sums[field] += vector  # Element-wise sum

    if valid_docs == 0:
        print("Error: No valid documents found.")
        return []

    # Compute averages
    query_features = {}
    for field in feature_sums:
        query_features[feature] = {}
        if valid_docs > 0:
            if isinstance(feature_sums[field], (int, float)):  # Scalar feature
                query_features[field] = feature_sums[field] / valid_docs
            else:  # Vector feature
                query_features[field] = (feature_sums[field] / valid_docs).tolist()

    # Elasticsearch query
    query = {
        "size": top_n,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": """
                        double total_cosineSimilarity = 0.0;
                        double total_weight = 0.0;
                        
                        if (params.containsKey('r_mean')) {
                            // Query values
                            double a1 = params.r_mean;
                            double a2 = params.g_mean;
                            double a3 = params.b_mean;
                            double a4 = params.i_mean;

                            // Document values
                            double b1 = params._source.r_mean;
                            double b2 = params._source.g_mean;
                            double b3 = params._source.b_mean;
                            double b4 = params._source.i_mean;

                            // Compute dot product
                            double dot_product = (a1 * b1) + (a2 * b2) + (a3 * b3) + (a4 * b4);

                            // Compute norms
                            double query_norm = Math.sqrt((a1 * a1) + (a2 * a2) + (a3 * a3) + (a4 * a4));
                            double doc_norm = Math.sqrt((b1 * b1) + (b2 * b2) + (b3 * b3) + (b4 * b4));

                            // Compute cosine similarity
                            total_cosineSimilarity += (query_norm * doc_norm == 0) ? 0 : dot_product / (query_norm * doc_norm);
                            total_weight += (query_norm * doc_norm == 0) ? 0 : 1;
                        }
                        if (params.containsKey('r_hist')) {
                            total_cosineSimilarity += (cosineSimilarity(params.r_hist, 'r_hist') + cosineSimilarity(params.g_hist, 'g_hist') + cosineSimilarity(params.b_hist, 'b_hist') + cosineSimilarity(params.i_hist, 'i_hist')) / 4 * 1;
                            total_weight += 1;
                        }
                        if (params.containsKey('energy')) {
                            total_cosineSimilarity += (cosineSimilarity(params.energy, 'energy') + cosineSimilarity(params.contrast, 'contrast') + cosineSimilarity(params.entropy, 'entropy') + cosineSimilarity(params.dissimilarity, 'dissimilarity') + cosineSimilarity(params.homogeneity, 'homogeneity') + cosineSimilarity(params.correlation, 'correlation')) / 6 * 1;
                            total_weight += 1;
                        }
                        if (params.containsKey('hog')) {
                            total_cosineSimilarity += cosineSimilarity(params.hog, 'hog');
                            total_weight += 1;
                        }
                        if (params.containsKey('gist')) {
                            total_cosineSimilarity += cosineSimilarity(params.gist, 'gist');
                            total_weight += 1;
                        }
                        if (params.containsKey('dct')) {
                            total_cosineSimilarity += cosineSimilarity(params.dct, 'dct');
                            total_weight += 1;
                        }
                        if (params.containsKey('wavelet')) {
                            total_cosineSimilarity += cosineSimilarity(params.wavelet, 'wavelet');
                            total_weight += 1;
                        }
                        if (params.containsKey('corners')) {
                            total_cosineSimilarity += cosineSimilarity(params.corners, 'corners');
                            total_weight += 1;
                        }

                        // Compute the average similarity and add 1.0 for Elasticsearch ranking
                        return (total_weight > 0.0) ? (total_cosineSimilarity / total_weight) : 0.0;
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