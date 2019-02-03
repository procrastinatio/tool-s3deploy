
from io import StringIO, BytesIO
import gzip
import json
import mimetypes
import os

mimetypes.init()
mimetypes.add_type('application/x-font-ttf', '.ttf')
mimetypes.add_type('application/x-font-opentype', '.otf')
mimetypes.add_type('application/vnd.ms-fontobject', '.eot')
mimetypes.add_type('application/json', '.json')
mimetypes.add_type('text/cache-manifest', '.appcache')
mimetypes.add_type('text/plain', '.txt')
mimetypes.add_type('image/x-icon', '.cur')




def get_file_mimetype(local_file):
    if local_file.endswith('services'):
        return 'application/json'
    else:
        mimetype, _ = mimetypes.guess_type(local_file)
        if mimetype:
            return mimetype
        return 'text/plain'

def is_cached(file_name, named_branch):
    if named_branch:
        return False
    # 1 exception
    if file_name == 'services':
        return True
    _, extension = os.path.splitext(file_name)
    return bool(extension not in ['.html', '.txt', '.appcache', ''])

def _gzip_data(data):
    out = None
    infile = StringIO()
    try:
        gzip_file = gzip.GzipFile(fileobj=infile, mode='w', compresslevel=5)
        gzip_file.write(data)
        gzip_file.close()
        infile.seek(0)
        out = infile.getvalue()
    except:
        out = None
    finally:
        infile.close()
    return out


def _unzip_data(compressed):
    inbuffer = BytesIO(compressed)
    f = gzip.GzipFile(mode='rb', fileobj=inbuffer)
    try:
        data = f.read()
    finally:
        f.close()

    return data
