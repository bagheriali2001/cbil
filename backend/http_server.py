import os
import json
import cgi
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
from search import search_similar_images, search_similar_images_from_keys
from dotenv import load_dotenv

load_dotenv()
PORT = os.getenv('PORT')
IMAGE_URL_PREFIX = os.getenv('IMAGE_URL_PREFIX')
IMAGE_FOLDER = os.getenv('IMAGE_FOLDER', 'images')

print("IMAGE_FOLDER:", IMAGE_FOLDER)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handles OPTIONS requests for CORS preflight"""
        self.send_response(204)  # No Content
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS, GET")  # Allowed methods
        self.send_header("Access-Control-Allow-Headers", "Content-Type")  # Allowed headers
        self.end_headers()

    def do_GET(self):
        """Handles GET requests for serving images"""
        if self.path.startswith("/img/"):
            filename = self.path[len("/img/"):]  # Extract filename
            file_path = os.path.join(IMAGE_FOLDER, filename)

            # Validate if the file exists
            if os.path.isfile(file_path):
                # Guess MIME type
                _, ext = os.path.splitext(filename)
                mime_type = {
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                }.get(ext.lower(), "application/octet-stream")

                # Serve the file
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.end_headers()
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/upload":
            # Parse the content length and content type
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']

            # Only process multipart form-data
            if "multipart/form-data" in content_type:
                _, params = cgi.parse_header(content_type)
                boundary = params.get('boundary')

                if boundary:
                    # Convert boundary to bytes
                    boundary = boundary.encode('ascii')  

                    # Parse the form data
                    form_data = cgi.parse_multipart(self.rfile, {'boundary': boundary})

                    # Get image data
                    image_data = form_data.get('image', [None])[0]
                    # Get features field
                    features = form_data.get('features', [None])[0]

                    if image_data:
                        nparr = np.frombuffer(image_data, np.uint8)
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                        if image is not None:
                            response = search_similar_images(image, features)
                            for item in response:
                                item['file'] = IMAGE_URL_PREFIX + item['file']

                            self.send_response(200)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps(response).encode())
                        else:
                            self.send_error(400, "Failed to decode image")
                    else:
                        self.send_error(400, "No image uploaded")
                else:
                    self.send_error(400, "Boundary not found")
            else:
                self.send_error(400, "Expected multipart/form-data")

        elif self.path == "/feedback":
            # Parse content length and type
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers['Content-Type']

            if content_type == "application/json":
                body = self.rfile.read(content_length)
                data = json.loads(body)

                # Extract file_keys and features
                file_keys = data.get('file_keys', [])
                features = data.get('features', None)

                if not isinstance(file_keys, list):
                    self.send_error(400, "file_keys must be a list")
                    return

                # Remove prefix from file keys
                file_keys = [item.replace(IMAGE_URL_PREFIX, '') for item in file_keys]  
                response = search_similar_images_from_keys(file_keys, features)
                for item in response:
                    item['file'] = IMAGE_URL_PREFIX + item['file']

                # Send JSON response
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_error(400, "Expected application/json")
        else:
            self.send_error(404, "Not Found")

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    server_address = ('', int(PORT))
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {int(PORT)}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
