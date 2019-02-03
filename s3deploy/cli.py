#!/usr/bin/env python
import os
import sys
import click
import json
import yaml

from s3 import init_connection, list_version, version_info, upload_to_s3


def get_file_dir():
       return os.path.dirname(os.path.realpath(__file__))


def CommandWithConfigFile(config_file_param_name):
    class CustomCommandClass(click.Command):
        def invoke(self, ctx):
            config_file = ctx.params[config_file_param_name]
            if config_file is not None:
                try:
                    with open(config_file) as f:
                        config_data = yaml.load(f)
                        print(config_data)
                        '''
                        cli_params = ctx.params
                        for param, value in cli_params.items():
                            print(param, value)
                            config_data[param] = cli_params[param]
                               
                         ctx['config_data'] = config_data'''
                   
                        for param, value in ctx.params.items():
                            if value is None and param in config_data:
                                ctx.params[param] = config_data[param]
                      
                except IOError:
                    print("Cannot open file {}".format(config_file))
                    sys.exit()

            return super(CustomCommandClass, self).invoke(ctx)

    return CustomCommandClass


@click.group()
def cli():
    pass


@click.group()
@click.option("--config_file", type=click.Path())
@click.pass_context
def another(ctx, config_file):
    ctx.obj = {"config_file": config_file}


@cli.command(name="info", cls=CommandWithConfigFile("config_file"))
@click.option("--bucket", "-b", type=str, required=True)
@click.option("--config_file", "-c", type=click.Path(), required=True)
@click.argument("s3_path")
def info_version(s3_path, bucket, config_file):
    print("bucket: {}".format(bucket))
    print("config_file: {}".format(config_file))

    s3, s3client, bucket = init_connection(bucket)

    version_info(s3, bucket, s3_path)


@cli.command(name="list", cls=CommandWithConfigFile("config_file"))
@click.option("--bucket", "-b", type=str, required=True)
@click.option("--config_file", "-c", type=click.Path(), required=True)
@click.pass_context
def list_versions(ctx, bucket, config_file):
    print("bucket: {}".format(bucket))
    print("config_file: {}".format(ctx.obj))

    s3, s3client, bucket = init_connection(bucket)

    print(list_version(bucket))
    

@cli.command(name="upload", cls=CommandWithConfigFile("config_file"))
@click.option("--bucket", "-b", "bucket_name", type=str, required=True)
@click.option("--named_branch",  "named_branch",is_flag=True, default=False, help="Print more output.")
@click.option("--base_dir","-d",   "base_dir", type=str, default=get_file_dir(), required=False)
@click.option("--url", "-u", "url_name", type=str, required=False)
@click.option("--config_file", "-c", type=click.Path(), required=True)
@click.option("--git_branch","-g", type=str, default=None, required=False)
@click.pass_context
def upload_version(ctx,  bucket_name, named_branch ,base_dir, url_name, git_branch, config_file):
    print("bucket: {}".format(bucket_name))
    print("config_file: {}".format(config_file))
    print("base_dir: {}".format(base_dir))
    print(ctx.params)
    
    with open(config_file) as f:
        config_data = yaml.load(f)
        for param, value in ctx.params.items():
            config_data[param] = ctx.params[param]
            
            
    print(json.dumps(config_data, indent=4))
    
    
    
   
   
    upload_to_s3(config_data)


if __name__ == "__main__":
    cli()
    # main('my_arg --config_file dummy.yaml'.split())
