from setuptools import setup, find_packages

setup(
    name = 'S3Deploye',
    version = '0.0.1',
    url = 'https://github.com/mypackage.git',
    author = 'Marc Monnerat',
    author_email = 'procrastinatio@gmail.com’,
    description = 'Deploy website to S3',
    packages = find_packages(),    
    install_requires = ['numpy >= 1.11.1', 'matplotlib >= 1.5.1'],
)
