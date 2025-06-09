import sys
from urllib.parse import urlparse
from socket import *

if len(sys.argv) != 3:
    print("Usage: python web_client.py <URL> <output_file>")
    sys.exit(1)

param_url = sys.argv[1]
param_file = sys.argv[2]

url_parsed = urlparse(param_url)
hostname = url_parsed.hostname
port = url_parsed.port if url_parsed.port else 80
path = url_parsed.path if url_parsed.path else '/'

try: 
    s = socket(AF_INET, SOCK_STREAM)
    s.settimeout(10)
    s.connect((hostname, port))

    request = f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nConnection: close\r\n\r\n"
    s.sendall(request.encode())

    response = b''
    while True:
        data = s.recv(1024)
        if not data:
            break
        response += data

    header_end = response.find(b'\r\n\r\n')
    if header_end == -1:
        raise ValueError("Invalid HTTP response")
        
    headers = response[:header_end].decode(errors='ignore')
    body = response[header_end+4:]

    try:
        status_line = headers.split('\r\n')[0]
        status_code = int(status_line.split(' ')[1])
    except (IndexError, ValueError):
        status_code = 0

    if status_code == 200:
        mode = 'wb' if any(x in headers.lower() for x in ['image/png', 'image/jpeg']) else 'w'
        with open(param_file, mode) as f:
            f.write(body) if mode == 'wb' else f.write(body.decode(errors='ignore'))
        print(f"Successfully saved to {param_file}")
    else:
        with open(param_file, 'w') as f:
            f.write(status_line)
        print(f"Error {status_code} - response saved")

except gaierror:
    print(f"DNS Error: Could not resolve {hostname}")
    with open(param_file, 'w') as f:
        f.write(f"DNS resolution failed for {hostname}")
except timeout:
    print("Connection timeout")
    with open(param_file, 'w') as f:
        f.write("Connection timeout")
except error as e:
    print(f"Connection Error: {e}")
    with open(param_file, 'w') as f:
        f.write(f"Connection failed: {str(e)}")
except Exception as e:
    print(f'Unexpected error: {e}')
    with open(param_file, 'w') as f:
        f.write(f"Error: {str(e)}")      
finally:
    if 's' in locals(): s.close()
    print("Download complete")
    
