import os
import json
import cgi
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
from dotenv import load_dotenv
load_dotenv()

from custom_functions import search_similar_images, search_similar_images_from_keys

PORT = os.getenv('PORT')
IMAGE_URL_PREFIX = os.getenv('IMAGE_URL_PREFIX')

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handles OPTIONS requests for CORS preflight"""
        self.send_response(204)  # No Content
        self.send_header("Access-Control-Allow-Origin", "*")  # Allow all origins
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")  # Allowed methods
        self.send_header("Access-Control-Allow-Headers", "Content-Type")  # Allowed headers
        self.end_headers()

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
                    boundary = boundary.encode('ascii')  # Convert boundary to bytes

                    # Set the boundary correctly
                    form_data = cgi.parse_multipart(self.rfile, {'boundary': boundary})

                    # Get the image file from the form field
                    image_data = form_data.get('image', [None])[0]
                    if image_data:
                        nparr = np.frombuffer(image_data, np.uint8)
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                        if image is not None:
                            response = search_similar_images(image)
                            for item in response:
                                item['file'] = IMAGE_URL_PREFIX+item['file']

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

            # Ensure content type is JSON
            if content_type == "application/json":
                # Read and parse JSON body
                body = self.rfile.read(content_length)
                data = json.loads(body)

                # Extract 'file_keys' from request
                file_keys = data.get('file_keys', [])

                if not isinstance(file_keys, list):
                    self.send_error(400, "file_keys must be a list")
                    return

                # Process the file_keys list
                file_keys = [item.replace(IMAGE_URL_PREFIX, '') for item in file_keys]  
                response = search_similar_images_from_keys(file_keys)
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
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
