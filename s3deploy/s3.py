import sys
import os
import json
from datetime import datetime
import re
import botocore
import boto3

from utils import _unzip_data, _gzip_data, get_files_to_upload, headers_extra_args

from git import create_s3_dir_path


def init_connection(bucket_name):
    """ Init the S3 connection
     
    """
    try:
        session = boto3.session.Session()
    except botocore.exceptions.BotoCoreError as e:
        print(
            'Cannot establish connection to bucket "%s". Check you credentials.' %
            bucket_name)
        print(e)
        sys.exit(1)

    s3client = session.client(
        "s3", config=boto3.session.Config(signature_version="s3v4")
    )
    s3 = session.resource(
        "s3", config=boto3.session.Config(
            signature_version="s3v4"))

    bucket = s3.Bucket(bucket_name)
    return (s3, s3client, bucket)


# s3://$S3_MF_GEOADMIN3_INT/mom_webmerc_search/1812041829/

# aws s3 ls s3://$S3_MF_GEOADMIN3_PROD/master/e9c53df/1807181420/
""" Prefix master/
    CommonPrefixes: master/e6eacb9/
    Prefixes  None
"""


def clean_path(path, previous_path):
    if previous_path is not None:
        cleaned_path = path.replace(previous_path, "")
    return cleaned_path.replace("/", "")


def get_subitems(bucket, prefix=""):
    """Get all subkeys of an items

    """
    items = []
    builds = bucket.meta.client.list_objects(
        Bucket=bucket.name, Prefix=prefix, Delimiter="/"
    )

    for v in builds.get("CommonPrefixes"):
        build = v.get("Prefix")
        build = clean_path(build, prefix)
        items.append(build)

    return items


def get_version_info(s3, bucket, s3_path):
    """Get build metadata
    """
    print("App version is: %s" % s3_path)
    version_target = s3_path.split("/")[2]
    obj = s3.Object(bucket.name, "%s/%s/info.json" % (s3_path, version_target))
    try:
        content = obj.get()["Body"].read()
        raw = _unzip_data(content)
        data = json.loads(raw)
    except botocore.exceptions.ClientError:
        return None
    except botocore.exceptions.BotoCoreError:
        return None
    return data


def version_info(s3, bucket, s3_path):
    info = get_version_info(s3, bucket, s3_path)
    if info is None:
        print("No info for version %s" % s3_path)
        sys.exit(1)
    for k in info.keys():
        print("%s: %s" % (k, info[k]))


'''
1/ Not a official path for branch fix_4200

Named branch: fix_4200 (version: 1803190954)
Named branch: fix_4200 (version: 1803191110)
Named branch: fix_4200 (version: 1803201226)
Named branch: fix_4200 (version: 1803201352)
Not a official path for branch fix_4200

$ aws s3 ls s3://$S3_MF_GEOADMIN3_INT/fix_4200/
                           PRE 1803190954/
                           PRE 1803191110/
                           PRE 1803201226/
                           PRE 1803201352/
                           PRE src/
2018-03-20 14:55:30      71474 404.html
2018-03-20 14:55:30         23 checker
2018-03-20 14:55:30       4524 embed.html
2018-03-20 14:55:30        326 favicon.ico
2018-03-19 10:57:44        372 geoadmin.1803190954.appcache





2/ Full version: gal_cloudfront/110ba87/1472481476

shas 110ba87, 1e37ff9/ et e70190b/
many version




'''


def version_exists(bucket, s3_path):
    """Check if a given version exists in the given bucket
    
    """
    files = bucket.objects.filter(Prefix=str(s3_path)).all()
    return len(list(files)) > 0

def activate_version(s3_path, bucket_name, deploy_target):
    print(deploy_target,'activate_version')
    s3, s3client, bucket = init_connection(bucket_name)
     
    if version_exists(bucket, s3_path) is False:
        print('Version <{}> does not exists in Bucket {}. Aborting'.format(s3_path, bucket_name))
        sys.exit(1)

    msg = input('Are you sure you want to activate version <%s>?\n' % s3_path)
    if msg.lower() in ('y', 'yes'):
        # Prod files
        for n in ('index', 'embed', 'mobile', '404'):
            src_key_name = '{}/{}.html'.format(s3_path, n)
            print('{} --> {}.html'.format(src_key_name, n))
            s3client.copy_object(
                Bucket=bucket_name,
                CopySource=bucket_name + '/' + src_key_name,
                Key=n + '.html',
                ACL='public-read')
        # Delete older appcache files
        appcache_versioned_files = list(bucket.objects.filter(Prefix='geoadmin.').all())
        indexes = [{'Key': k.key} for k in appcache_versioned_files if k.key.endswith('.appcache')]
        if len(indexes) > 0:
            s3client.delete_objects(Bucket=bucket_name, Delete={'Objects': indexes})

        appcache = None
        files = list(bucket.objects.filter(Prefix='{}/geoadmin.'.format(s3_path)).all())
        if len(files) > 0:
            appcache = os.path.basename(sorted(files)[-1].key)
        for j in ('robots.txt', 'checker', 'favicon.ico', appcache):
            # In prod move robots prod
            src_file_name = 'robots_prod.txt' if j == 'robots.txt' and deploy_target == 'prod' else j
            src_key_name = '{}/{}'.format(s3_path, src_file_name)
            print('%s ---> %s' % (src_key_name, j))
            try:
                s3client.copy_object(
                    Bucket=bucket_name,
                    CopySource=bucket_name + '/' + src_key_name,
                    Key=j,
                    CopySourceIfModifiedSince=datetime(2015, 1, 1),
                    ACL='public-read')
            except botocore.exceptions.ClientError as e:
                print('Cannot copy {}: {}'.format(j, e))
        print('\nPlease check it on:\n{}'.format(get_url(deploy_target)))
        print('And:\n{}'.format(get_url(deploy_target, key_name=s3_path + '/src/index.html')))
    else:
        print('Aborting activation of version {}'.format(s3_path))
        sys.exit(1)

def list_version(bucket):
    """List all versions in a given bucket
    
    """
    for branch in get_subitems(bucket, prefix=""):

        # if re.search(r"^\D", branch):  # branch's name may have number!!!
        if re.search(r"^[a-z0-9_-]", branch):

            shas = get_subitems(bucket, prefix=branch + "/")

            for sha in shas:

                nice_sha = clean_path(sha, branch)
                # Full version path to display

                if re.match("[0-9a-f]{7}$", nice_sha) is not None:

                    builds = get_subitems(
                        bucket, prefix=branch + "/" + nice_sha + "/")
                    for build in builds:
                        if re.match("[0-9]{10}", build):

                            print(
                                "Full version: %s/%s/%s" %
                                (branch, nice_sha, clean_path(
                                    build, nice_sha)))
                else:
                    # Matching a version of the deployed branch (it is olds ?)
                    if re.match("[0-9]{10}", nice_sha):
                        print(
                            "Named branch: %s (version: %s)"
                            % (branch.replace("/", ""), nice_sha)
                        )
            else:
                print("Not a official path for branch %s" % branch)


def upload_to_s3(s3, cfg):
    """Uploads a dir to a bucket given a configuration

    """
    s3_dir_path, version = create_s3_dir_path(
        cfg['base_dir'], cfg['named_branch'], cfg['git_branch'])
    print('Destination folder is:')
    print('%s' % s3_dir_path)

    cfg['version'] = version
    cfg['root_files'] = [s.format(**cfg) for s in cfg['root_files']]
    cfg['s3_dir_path'] = s3_dir_path

    # s3_dir_path, named_branch, version, upload_directories, exclude_files,
    # root_files)
    files = get_files_to_upload(**cfg)

    # with open('mf-geoadmin3_s3deploy.json', 'w') as f:
    #    f.write(json.dumps(files, indent=4))

    for f in files:
        if cfg['noop']:
            if 'Cesium' not in f['local_name'] and 'awesome' not in f['local_name']:
                print(json.dumps(f, indent=4))
        else:
            save_to_s3(s3, **f)


def save_to_s3(
        s3,
        local_name=None,
        remote_name=None,
        bucket_name=None,
        to_compress=False,
        cached=True,
        mimetype=None,
        break_on_error=False,
        **kwargs):
    '''Reading data for uploading to S3
    
    '''
    try:
        with open(local_name, 'rb') as f:
            data = f.read()
    except EnvironmentError as e:
        print('Failed to upload %s' % local_name)
        print(str(e))
        if break_on_error:
            print("Exiting...")
            sys.exit(1)
        else:
            return False
    _save_to_s3(
        s3,
        data,
        remote_name,
        mimetype,
        bucket_name,
        cached=cached,
        to_compress=to_compress)


def _save_to_s3(
        s3,
        in_data,
        dest,
        mimetype,
        bucket_name,
        to_compress=True,
        cached=True):
    '''Uploading data to S3
    
    '''
    data = in_data
    extra_args = {}

    if to_compress:
        data = _gzip_data(in_data)

    extra_args = headers_extra_args(to_compress, cached)

    extra_args['ContentType'] = mimetype

    try:
        print('Uploading to %s - %s, gzip: %s, cache headers: %s' %
              (dest, mimetype, to_compress, cached))

        # TODO: do nothig
        s3.Object(bucket_name, dest).put(Body=data, **extra_args)
    except Exception as e:
        print('Error while uploading %s: %s' % (dest, e))
