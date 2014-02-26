import requests
import argparse

def upload(filename):
    with open(filename, 'rb') as f:
        r = requests.post("http://localhost:4321/upload_catalog",
                          files={'uploaded_file': f})
        return r.content
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help="file to upload", required=True)
    args = parser.parse_args()
    print(upload(args.file))
