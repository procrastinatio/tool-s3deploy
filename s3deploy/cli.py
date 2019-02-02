#!/usr/bin/env python
import click
import yaml


def CommandWithConfigFile(config_file_param_name):

    class CustomCommandClass(click.Command):

        def invoke(self, ctx):
            config_file = ctx.params[config_file_param_name]
            if config_file is not None:
                with open(config_file) as f:
                    config_data = yaml.load(f)
                    for param, value in ctx.params.items():
                        if value is None and param in config_data:
                            ctx.params[param] = config_data[param]

            return super(CustomCommandClass, self).invoke(ctx)

    return CustomCommandClass

@click.group()
def cli():
    pass

@click.command(cls=CommandWithConfigFile('config_file'))
@click.argument("arg")
@click.option("--opt")
@click.option("--config_file", type=click.Path())
def main(arg, opt, config_file):
    print("arg: {}".format(arg))
    print("opt: {}".format(opt))
    print("config_file: {}".format(config_file))


if __name__ == '__main__':
        main()
        #main('my_arg --config_file dummy.yaml'.split()) 
