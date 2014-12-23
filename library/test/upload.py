import requests
import argparse

def upload_catalog(filename, url):
    with open(filename, 'rb') as f:
        r = requests.post(url + '/upload_catalog',
                          files={'uploaded_file': f})
        return r.content
    return None

def upload_catalog_json(filename, url):
    with open(filename, 'rt') as f:
        r = requests.post(url + '/upload_catalog_json',
                          data={'uploaded_file': f.read()})
        return r.content
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help="file to upload", required=True)
    parser.add_argument('--url', help="url", required=False,
                        default='http://localhost:4321')
    args = parser.parse_args()
    print(upload_catalog_json(args.file, args.url))
