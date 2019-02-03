#!/usr/bin/env python
import os
import sys
import click
import yaml

from s3 import init_connection, list_version, version_info


def CommandWithConfigFile(config_file_param_name):
    class CustomCommandClass(click.Command):
        def invoke(self, ctx):
            config_file = ctx.params[config_file_param_name]
            if config_file is not None:
                try:
                    with open(config_file) as f:
                        config_data = yaml.load(f)
                        print(config_data)
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


if __name__ == "__main__":
    cli()
    # main('my_arg --config_file dummy.yaml'.split())
