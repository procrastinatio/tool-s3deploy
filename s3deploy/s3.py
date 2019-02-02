import sys
import botocore
import boto3
import re


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


def clean_path(path, previous_path):
    return path.replace(previous_path, '').replace('/', '')

def get_subitems(bucket, prefix=None):
    items = []
    builds = bucket.meta.client.list_objects(Bucket=bucket.name,
                                   Delimiter='/')
    if prefix is not None:
        builds['Prefix'] = prefix
    for v in builds.get('CommonPrefixes'):
        build = v.get('Prefix')
        items.append(build.replace(prefix, ''))
        
    return items

def list_version(bucket):
    branches = bucket.meta.client.list_objects(Bucket=bucket.name,
                                               Delimiter='/')
    for b in branches.get('CommonPrefixes'):
        branch = b.get('Prefix')
        print(branch)
        if re.search(r'^\D', branch):
            shas = bucket.meta.client.list_objects(Bucket=bucket.name,
                                                   Prefix=branch,
                                                   Delimiter='/')
            
            shas = shas.get('CommonPrefixes')
            if shas:
                for s in shas:
                    print(s)
                    sha = s.get('Prefix')
                    nice_sha = clean_path(sha, branch)
                    # Full version path to display
                    if re.match('[0-9a-f]{7}$', nice_sha) is not None:
                        for build in get_subitems(bucket, prefix=sha):
                        
                            print('Full version: %s%s/%s' % (branch,
                                                             nice_sha,
                                                             clean_path(build, sha) ))
                    else:
                        # Matching a version of the deployed branch
                        if re.match('[0-9]{10}', nice_sha):
                            pass #print('Named branch: %s (version: %s)' % (branch.replace('/', ''), nice_sha))
            else:
                print('Not a official path for branch %s' % branch)
