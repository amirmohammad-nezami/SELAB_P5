import urllib.request
import os
import time

# Reads the server address from the Docker environment variable, assuming it is localhost if not present.
server_host = os.environ.get('SERVER_HOST', 'localhost')
url = f"http://{server_host}:80"

print(f"The client started. Attempting to connect to the server at address: {url}")

# Sends requests to the server 5 times at intervals
for i in range(5):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read().decode('utf-8')
            print(f"[Request {i+1}] Response received from server: {html.strip()}")
    except Exception as e:
        print(f"[Error] The server is not yet available or an error has occurred:{e}")
    time.sleep(3)
