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

print("ELASTIC_URL:", ELASTIC_URL)
print("ELASTIC_USERNAME:", ELASTIC_USERNAME)
print("ELASTIC_PASSWORD:", ELASTIC_PASSWORD)
print("ELASTIC_INDEX:", ELASTIC_INDEX)

es = Elasticsearch(ELASTIC_URL,
    basic_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD)
)
es.info()

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
    
    docs = es.mget(index=ELASTIC_INDEX, body={"ids": keys})
    
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
                    if isinstance(source[field], (int, float)):
                        feature_sums[field] += source[field]
                    else:
                        vector = np.array(source[field])
                        if feature_sums[field] is None:
                            feature_sums[field] = vector
                        else:
                            feature_sums[field] += vector

    if valid_docs == 0:
        print("Error: No valid documents found.")
        return []

    query_features = {}
    for field in feature_sums:
        query_features[feature] = {}
        if valid_docs > 0:
            if isinstance(feature_sums[field], (int, float)):
                query_features[field] = feature_sums[field] / valid_docs
            else:
                query_features[field] = (feature_sums[field] / valid_docs).tolist()

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

    response = es.search(index=ELASTIC_INDEX, body=query)
    similar_images = [{
        'file': hit["_source"]["file"],
        '_score': hit["_score"],
    } for hit in response["hits"]["hits"]]
    
    return similar_images