import requests
import argparse

def upload(filename):
    f = open(filename, 'rb')
    r = requests.post("http://localhost:4321/upload_catalog",
                      files={'uploaded_file': f})
    print r.content
    f.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', help="file to upload", required=True)
    args = parser.parse_args()
    upload(args.file)
