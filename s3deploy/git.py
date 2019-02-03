
import subprocess
import os.path

def local_git_last_commit(basedir):
    try:
        output = subprocess.check_output(('git rev-parse HEAD',), cwd=basedir, shell=True)
        return output.decode('ascii', 'ignore').strip()
    except subprocess.CalledProcessError:
        print('Not a git directory: %s' % basedir)
    try:
        with open(os.path.join(basedir, '.build-artefacts', 'last-commit-ref'), 'r') as f:
            data = f.read()
        return data.decode('ascii', 'ignore')
    except IOError:
        print('Error while reading \'last-commit-ref\' from %s' % basedir)
    return None


def local_git_branch(basedir):
    output = subprocess.check_output(('git rev-parse --abbrev-ref HEAD',), cwd=basedir, shell=True)
    return output.decode('ascii', 'ignore').strip()


def local_last_version(basedir):
    print(basedir)
    try:
        with open(os.path.join(basedir, '.build-artefacts', 'last-version'), 'r') as f:
            data = f.read()
        return data
    except IOError as e:
        print('Cannot find version: %s' % e)
    return None


def create_s3_dir_path(base_dir, named_branch, git_branch):
    print(base_dir)
    if git_branch is None:
        git_branch = local_git_branch(base_dir)
    version = local_last_version(base_dir).strip()
    if named_branch:
        return (git_branch, version)
    git_short_sha = local_git_last_commit(base_dir)[:7]
    print(git_branch, git_short_sha, version)
    return (os.path.join(git_branch, git_short_sha, version), version)