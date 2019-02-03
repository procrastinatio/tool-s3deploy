import sys
import os
import botocore
import boto3
import re
import json

from utils import _unzip_data

from git import create_s3_dir_path


def init_connection(bucket_name):
    try:
        session = boto3.session.Session()
    except botocore.exceptions.BotoCoreError as e:
        print(
            'Cannot establish connection to bucket "%s". Check you credentials.'
            % bucket_name
        )
        print(e)
        sys.exit(1)

    s3client = session.client(
        "s3", config=boto3.session.Config(signature_version="s3v4")
    )
    s3 = session.resource("s3", config=boto3.session.Config(signature_version="s3v4"))

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
def version_exists(s3_path):
    files = bucket.objects.filter(Prefix=str(s3_path)).all()
    return len(list(files)) > 0


def list_version(bucket):

    for branch in get_subitems(bucket, prefix=""):

        #if re.search(r"^\D", branch):  # branch's name may have number!!!
        if re.search(r"^[a-z0-9_-]", branch):

            shas = get_subitems(bucket, prefix=branch + "/")

            for sha in shas:

                nice_sha = clean_path(sha, branch)
                # Full version path to display

                if re.match("[0-9a-f]{7}$", nice_sha) is not None:

                    builds = get_subitems(bucket, prefix=branch + "/" + nice_sha + "/")
                    for build in builds:
                        if re.match("[0-9]{10}", build):

                          print(
                            "Full version: %s/%s/%s"
                            % (branch, nice_sha, clean_path(build, nice_sha))
                          )
                else:
                    # Matching a version of the deployed branch (it is olds ?)
                    if re.match("[0-9]{10}", nice_sha):
                        print(
                            "Named branch: %s (version: %s)"
                            % (branch.replace("/", ""), nice_sha)
                        )
            else:
                print("Not a official path for branch %s" % branch)
                
                
def upload_to_s3(bucket_name, base_dir, deploy_target, named_branch, git_branch):
    s3_dir_path, version = create_s3_dir_path(base_dir, named_branch, git_branch)
    print('Destination folder is:')
    print('%s' % s3_dir_path)
    upload_directories = ['prd', 'src']
    exclude_filename_patterns = ['.less', '.gitignore', '.mako.']
    root_files = ('index.html', 'mobile.html', 'embed.html', '404.html',
                  'robots.txt', 'robots_prod.txt', 'favicon.ico',
                  'checker', 'geoadmin.%s.appcache' % version)
    
    for directory in upload_directories:
        for file_path_list in os.walk(os.path.join(base_dir, directory)):
            file_names = file_path_list[2]
            if len(file_names) > 0:
                file_base_path = file_path_list[0]
                for file_name in file_names:
                    print(file_name)
