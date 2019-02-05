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
@click.option('--repo-home', envvar='REPO_HOME', default='.repo')
@click.option('--debug/--no-debug', default=False,
              envvar='REPO_DEBUG')
@click.option("--config_file", "-c", type=click.Path(), required=True)
@click.pass_context
def cli(ctx, config_file, repo_home, debug):
    
    ctx.obj = SimpleRepo(repo_home, debug)
    
    with open(config_file) as f:
        config_data = yaml.load(f)
        for param, value in ctx.params.items():
            config_data[param] = ctx.params[param]

    print(json.dumps(config_data, indent=4))
    
    
    
    ctx.obj= RepoManager('GeoAdminRepo', repo_home, debug)
    #print('Repo', r)


    
@cli.command()
@click.argument('src')
@click.argument('dest', required=False)
#@click.pass_obj
@pass_repo
def clone(repo, src, dest):
    print(repo, src, dest, repo.archive_engine.generate())


if __name__ == '__main__':
    cli()
