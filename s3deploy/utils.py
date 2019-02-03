
from io import StringIO, BytesIO
import gzip
import json
import mimetypes
import os
from datetime import datetime

mimetypes.init()
mimetypes.add_type('application/x-font-ttf', '.ttf')
mimetypes.add_type('application/x-font-opentype', '.otf')
mimetypes.add_type('application/vnd.ms-fontobject', '.eot')
mimetypes.add_type('application/json', '.json')
mimetypes.add_type('text/cache-manifest', '.appcache')
mimetypes.add_type('text/plain', '.txt')
mimetypes.add_type('image/x-icon', '.cur')

'''


/master/eebba2c/1807181149/1807181149/
                           PRE img/
                           PRE lib/
                           PRE locales/
                           PRE style/
2018-07-18 11:49:58        172 info.json
2018-07-18 11:49:59      47456 layersConfig.de.json

 aws s3 ls   s3://$S3_MF_GEOADMIN3_PROD/master/eebba2c/1807181149/
                           PRE 1807181149/
                           PRE src/
2018-07-18 11:49:58      71474 404.html
2018-07-18 11:49:58         23 checker
2018-07-18 11:49:58       4659 embed.html
2018-07-18 11:49:58        326 favicon.ico
2018-07-18 11:49:58        384 geoadmin.1807181149.appcache
2018-07-18 11:49:58       7141 index.html

prd/cache/service --> /master/eebba2c/1807181149/1807181149/


src


aws s3 ls   s3://$S3_MF_GEOADMIN3_PROD/master/eebba2c/1807181149/src/
                           PRE components/
                           PRE img/
                           PRE js/
                           PRE lib/
                           PRE locales/
                           PRE style/
2018-07-18 11:50:06      71915 404.html
2018-07-18 11:50:06      11251 TemplateCacheModule.js
2018-07-18 11:50:06         23 checker
2018-07-18 11:50:06       3472 deps.js
2018-07-18 11:50:06       6238 embed.html
2018-07-18 11:50:06       9278 index.html
2018-07-18 11:49:59      47456 layersConfig.de.json
2018-07-18 11:49:59      49396 layersConfig.en.json
2018-07-18 11:49:59      50589 layersConfig.fr.json
2018-07-18 11:49:59      49941 layersConfig.it.json
2018-07-18 11:49:59      49898 layersConfig.rm.json
2018-07-18 11:50:06       9280 mobile.html
2018-07-18 11:49:59        956 services



is_chsdi_cache = bool(file_base_path.endswith('cache'))
                        local_file = os.path.join(file_base_path, file_name)
                        relative_file_path = file_base_path.replace('cache', '')
                        if directory == 'prd':
                            # Take only files directly in prd/
                            if file_name in root_files and relative_file_path.endswith('prd'):
                                relative_file_path = relative_file_path.replace('prd', '')
                            else:
                                relative_file_path = relative_file_path.replace('prd', version)
                        relative_file_path = relative_file_path.replace(base_dir + '/', '')
                        remote_file = os.path.join(s3_dir_path, relative_file_path, file_name)
                        # Don't cache some files
                        cached = is_cached(file_name, named_branch)
                        mimetype = get_file_mimetype(local_file)
                        save_to_s3(local_file, remote_file, bucket_name, cached=cached, mimetype=mimetype)
                        # Also upload chsdi metadata file to src folder if available
                        if is_chsdi_cache:
                            relative_file_path = relative_file_path.replace(version + '/', '')
                            remote_file = os.path.join(s3_dir_path, 'src/', relative_file_path, file_name)
                            save_to_s3(local_file, remote_file, bucket_name, cached=cached, mimetype=mimetype)
'''

def geoadmin_relative_file_path_rule(base_dir, directory,file_name,  file_base_path, root_files, version):
    
    #relative_file_path = file_base_path.replace('cache', '')
    if directory == 'prd':
        # Take only files directly in prd/
        relative_file_path = file_base_path.replace(base_dir + '/', '')
        if file_name in root_files and relative_file_path.endswith('prd'):
            relative_file_path = relative_file_path.replace('prd', '')
        else:
            relative_file_path = relative_file_path.replace('prd', version)
            
    # files in prd/cache i.e. prd/cache/layersConfig.en.json and prd/cache/service
    if bool(file_base_path.endswith('cache')):
        
        relative_file_path = version
        
            
            
    return relative_file_path
    
    

def get_files_to_upload(bucket_name=None, base_dir=None, s3_dir_path=None, project=None, named_branch=None, compress=True, skip_compress=[], version=None, upload_directories=None, exclude_files=None, root_files=None, **kwargs): #base_dir, s3_dir_path, named_branch, version, upload_directories, exclude_filename_patterns, root_files):
    
   
    files = []
    to_compress = False
    
    for directory in upload_directories:
        for file_path_list in os.walk(os.path.join(base_dir, directory)):
            file_names = file_path_list[2]
            if len(file_names) > 0:
                file_base_path = file_path_list[0]
                for file_name in file_names:
                    if len([p for p in exclude_files if p in file_name]) == 0:
                        local_file = os.path.join(file_base_path, file_name)
                        # Special rules for geoadmin
                        if 'geoadmin' in project:
                            
                            relative_file_path = geoadmin_relative_file_path_rule(base_dir, directory,file_name,  file_base_path, root_files, version)
                            #print('geoadmin stuff', relative_file_path, directory, file_name, file_base_path.replace(base_dir + '/', ''))
                        else:
                            # TODO check
                            relative_file_path = file_base_path.replace(base_dir + '/', '')
                            
                       
                        remote_file = os.path.join(s3_dir_path, relative_file_path, file_name)
                        # Don't cache some files
                        cached = is_cached(file_name, named_branch)
                        mimetype = get_file_mimetype(local_file)
                        

                        # Also upload chsdi metadata file to src folder if available
                        # TODO what the hell is this?
                        # if is_chsdi_cache:
                        #    relative_file_path = relative_file_path.replace(version + '/', '')
                        #    remote_file = os.path.join(s3_dir_path, 'src/', relative_file_path, file_name)
                            
                        if compress and mimetype not in skip_compress:
                            to_compress = True
                            
                            
                        file_dict = {'local_name': local_file, 'remote_name':  remote_file,'bucket_name':  bucket_name,'cached': cached, 'mimetype':mimetype,
                                     'is_chsdi_cache': is_chsdi_cache, 'to_compress': to_compress}
                        
                        files.append(file_dict)
    return files   


def headers_extra_args(to_compress, cached):
    cached = False # TODO
    extra_args = {}
 
    if to_compress:
        extra_args['ContentEncoding'] = 'gzip'


    if cached is False:
        extra_args['CacheControl'] = 'max-age=0, must-revalidate, s-maxage=300'
        extra_args['Expires'] = datetime(1990, 1, 1)
        extra_args['Metadata'] = {'Pragma': 'no-cache', 'Vary': '*'}
    else:
        extra_args['CacheControl'] = 'max-age=31536000, public'

    extra_args['ACL'] = 'public-read'
    
    return extra_args
        


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
    infile = BytesIO()
    try:
        gzip_file = gzip.GzipFile(fileobj=infile, mode='wb', compresslevel=5)
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
