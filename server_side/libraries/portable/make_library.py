# not complete...

with open('library.json', 'r') as fin:
    with open('data.js', 'w') as fout:
        fout.write('LIBRARY = {};'.format(fin.read()))
