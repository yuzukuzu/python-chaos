import sys
from urllib.parse import urlparse
from socket import *

param_url = sys.argv[1]
param_file = sys.argv[2]

url_parsed = urlparse(param_url)
hostname = url_parsed.hostname
port = url_parsed.port if url_parsed.port else 80
path = url_parsed.path if url_parsed.path else '/'

try: 
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((hostname, port))

    request = f"GET {path} HTTP/1.1\r\n"
    request += f"Host: {hostname}\r\n"
    request += "Connection: close\r\n\r\n"

    s.send(request.encode())

    response = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data

    header_end = response.find(b'\r\n\r\n')
    headers = response[:header_end].decode()
    body = response[header_end+4:] 

    status_line = headers.split('\r\n')[0]
    status_code = int(status_line.split(' ')[1])

    if status_code == 200:
        mode = 'wb' if 'image' in headers.lower() else 'w'
        with open(param_file, mode) as f:
            f.write(body) if mode == 'wb' else f.write(body.decode())
        print(f"Successfully saved to {param_file}")
    else:
        with open(param_file, 'w') as f:
            f.write(headers)
        print(f"Error {status_code} - headers saved to {param_file}")

except gaierror:
    print(f"DNS Error: Could not resolve {hostname}")
    with open(param_file, 'w') as f:
        f.write(f"DNS resolution failed for {hostname}")
except error as e:
    print(f"Connection Error: {e}")
    with open(param_file, 'w') as f:
        f.write(f"Connection failed: {str(e)}")
finally:
    s.close()
    print("\nFinishing downloading ...")
