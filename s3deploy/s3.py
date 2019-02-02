import sys
import botocore
import boto3
import re
import json

from utils import _unzip_data


def init_connection(bucket_name):
    try:
        session = boto3.session.Session()
    except botocore.exceptions.BotoCoreError as e:
        print('Cannot establish connection to bucket "%s". Check you credentials.' % bucket_name)
        print(e)
        sys.exit(1)

    s3client = session.client('s3', config=boto3.session.Config(signature_version='s3v4'))
    s3 = session.resource('s3', config=boto3.session.Config(signature_version='s3v4'))

    bucket = s3.Bucket(bucket_name)
    return (s3, s3client, bucket)

# s3://$S3_MF_GEOADMIN3_INT/mom_webmerc_search/1812041829/

# aws s3 ls s3://$S3_MF_GEOADMIN3_PROD/master/e9c53df/1807181420/
''' Prefix master/
    CommonPrefixes: master/e6eacb9/
    Prefixes  None
'''

def clean_path(path, previous_path):
    return path.replace(previous_path, '').replace('/', '')

def get_subitems(bucket, prefix=''):
    items = []
    builds = bucket.meta.client.list_objects(Bucket=bucket.name,
                                   Prefix=prefix,
                                   Delimiter='/')

    for v in builds.get('CommonPrefixes'):
        build = v.get('Prefix')
       
        if prefix is not None:
            build = clean_path(build, prefix)
        else:
            build = v.replace('/','')
        items.append(build)
        
    return items



def get_version_info(s3,bucket, s3_path):
    print('App version is: %s' % s3_path)
    version_target = s3_path.split('/')[2]
    obj = s3.Object(bucket.name, '%s/%s/info.json' % (s3_path, version_target))
    try:
        content = obj.get()["Body"].read()
        raw = _unzip_data(content)
        data = json.loads(raw)
    except botocore.exceptions.ClientError:
        return None
    except botocore.exceptions.BotoCoreError:
        return None
    return data


def version_info(s3,bucket, s3_path):
    info = get_version_info(s3, bucket, s3_path)
    if info is None:
        print('No info for version %s' % s3_path)
        sys.exit(1)
    for k in info.keys():
        print('%s: %s' % (k, info[k]))

def version_exists(s3_path):
    files = bucket.objects.filter(Prefix=str(s3_path)).all()
    return len(list(files)) > 0

def list_version(bucket):
   
        
    for branch in get_subitems(bucket, prefix=''):

        
        if re.search(r'^\D', branch):
        
            shas = get_subitems(bucket, prefix=branch + '/')

            for sha in shas:

                    nice_sha = clean_path(sha, branch)
                    # Full version path to display

                    if re.match('[0-9a-f]{7}$', nice_sha) is not None:
                       
                        builds = get_subitems(bucket, prefix=branch + '/' + nice_sha + '/')
                        for build in builds:
                        
                            print('Full version: %s/%s/%s' % (branch,
                                                             nice_sha,
                                                             clean_path(build, nice_sha) ))
                    else:
                        # Matching a version of the deployed branch
                        if re.match('[0-9]{10}', nice_sha):
                            print('Named branch: %s (version: %s)' % (branch.replace('/', ''), nice_sha))
            else:
                print('Not a official path for branch %s' % branch)
