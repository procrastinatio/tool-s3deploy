
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


def geoadmin_relative_file_path_rule(directory,file_name,  file_base_path, root_files, version):
    
    relative_file_path = file_base_path.replace('cache', '')
    if directory == 'prd':
        # Take only files directly in prd/
        if file_name in root_files and relative_file_path.endswith('prd'):
            relative_file_path = relative_file_path.replace('prd', '')
        else:
            relative_file_path = relative_file_path.replace('prd', version)
            
            
    return relative_file_path
    
    

def get_files_to_upload(bucket_name=None, base_dir=None, s3_dir_path=None, project=None, named_branch=None, compress=True, skip_compress=[], version=None, upload_directories=None, exclude_files=None, root_files=None, **kwargs): #base_dir, s3_dir_path, named_branch, version, upload_directories, exclude_filename_patterns, root_files):
    
   
    files = []
    compressed = False
    
    for directory in upload_directories:
        for file_path_list in os.walk(os.path.join(base_dir, directory)):
            file_names = file_path_list[2]
            if len(file_names) > 0:
                file_base_path = file_path_list[0]
                for file_name in file_names:
                    if len([p for p in exclude_files if p in file_name]) == 0:
                        local_file = os.path.join(file_base_path, file_name)
                        # Special rules for geoadmin
                        # files in prd/cache i.e. prd/cache/layersConfig.en.json and prd/cache/services
                        is_chsdi_cache = bool(file_base_path.endswith('cache'))
                        if project == 'geoadmin':
                            relative_file_path = geoadmin_relative_file_path_rule(directory, file_name, file_base_path, root_files, version)
                        else:
                            # TODO check
                            relative_file_path = file_base_path.replace(base_dir + '/', '')
                            
                       
                        remote_file = os.path.join(s3_dir_path, relative_file_path, file_name)
                        # Don't cache some files
                        cached = is_cached(file_name, named_branch)
                        mimetype = get_file_mimetype(local_file)
                        

                        # Also upload chsdi metadata file to src folder if available
                        if is_chsdi_cache:
                            relative_file_path = relative_file_path.replace(version + '/', '')
                            remote_file = os.path.join(s3_dir_path, 'src/', relative_file_path, file_name)
                            
                        if compress and mimetype not in skip_compress:
                            compressed = True
                            
                            
                        file_dict = {'local_name': local_file, 'remote_name':  remote_file,'bucket_name':  bucket_name,'cached': cached, 'mimetype':mimetype,
                                     'is_chsdi_cache': is_chsdi_cache, compressed: compressed}
                        
                        files.append(file_dict)
    return files                    
        


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
