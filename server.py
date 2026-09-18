from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        message = "Hello! The answer was sent from the Docker server container.\n"
        self.wfile.write(message.encode('utf-8'))

def run():
    # The container's internal server is started on port 80.
    server_address = ('', 80)
    httpd = HTTPServer(server_address, SimpleHandler)
    print("Python server inside container enabled on port 80...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
