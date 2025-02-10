# CBIL

## Initializing Elasticsearch Index

Run these commands on Elasticsearch console:

```
PUT /cbil_db

PUT /cbil_db/_mapping
{
  "properties": {
    "energy": { "type": "dense_vector", "dims": 4 },
    "contrast": { "type": "dense_vector", "dims": 4 },
    "entropy": { "type": "dense_vector", "dims": 4 },
    "dissimilarity": { "type": "dense_vector", "dims": 4 },
    "homogeneity": { "type": "dense_vector", "dims": 4 },
    "correlation": { "type": "dense_vector", "dims": 4 },

    "r_hist": { "type": "dense_vector", "dims": 16 },
    "g_hist": { "type": "dense_vector", "dims": 16 },
    "b_hist": { "type": "dense_vector", "dims": 16 },
    "i_hist": { "type": "dense_vector", "dims": 16 },

    "sift": {
        "type": "nested",
        "properties": {
            "vector": {
                "type": "dense_vector",
                "dims": 128
            }
        }
    },

    "hog": { "type": "dense_vector", "dims": 1176 },
    "gist": { "type": "dense_vector", "dims": 1024 },
    "dct": { "type": "dense_vector", "dims": 1280 },
    "wavelet": { "type": "dense_vector", "dims": 12 },
    "corners": { "type": "dense_vector", "dims": 1024 }
  }
}
```
