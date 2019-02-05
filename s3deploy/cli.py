#!/usr/bin/env python3


# see http://click.palletsprojects.com/en/7.x/complex/
# https://krzysztofzuraw.com/blog/2016/factory-pattern-python.html

import os
import click
import yaml
import json   


from repository import  SimpleRepo, GeoAdminRepo, RepoManager

pass_repo = click.make_pass_decorator(RepoManager)

@click.group()
@click.option('--bucket-name','-b', 'bucket_name',  envvar='BUCKET_NAME', default='.repo')
@click.option('--debug/--no-debug', default=False,
              envvar='REPO_DEBUG')
@click.option("--config_file", "-c", type=click.Path(), required=True)
@click.pass_context
def cli(ctx, config_file, bucket_name, debug):
    
    ctx.obj = SimpleRepo(bucket_name, debug)
    
    with open(config_file) as f:
        config_data = yaml.load(f)
        for param, value in ctx.params.items():
            config_data[param] = ctx.params[param]

    print(json.dumps(config_data, indent=4))
    
    
    
    ctx.obj= RepoManager('GeoAdminRepo', bucket_name, debug)
    #print('Repo', r)


    
@cli.command(name='list')
@click.argument('src')
@click.argument('dest', required=False)
#@click.pass_obj
@pass_repo
def list_versions(repo, src, dest):
    print(repo, src, dest, repo.archive_engine.generate())


if __name__ == '__main__':
    cli()
