import zipfile

zfile = zipfile.ZipFile("library.json.zip")
for name in zfile.namelist():
    with open(name, "w") as file:
        zfile.read(file)
