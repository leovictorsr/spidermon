import click

from importlib import import_module
from scrapy.utils.project import inside_project
from spidermon.commands.prompts import monitor_prompts, validation_prompts


def decorator_with_arguments(decorator):
    def decorator_maker(*args, **kwargs):
        def wrapper(func):
            return decorator(func, *args, **kwargs)

        return wrapper

    return decorator_maker


@decorator_with_arguments
def is_packaged_installed(func, *args, **kwargs):
    def wrapper_is_packaged_installed():
        try:
            if "module" in kwargs:
                import_module(kwargs["module"])
                kwargs.pop("module")
                return func(*args, **kwargs)
        except ImportError:
            msg = validation_prompts["module_error"].format(kwargs["module"])
            click.echo("\n")
            click.echo(click.style(msg, fg="red", bg="white"))
            raise ImportError

    return wrapper_is_packaged_installed


def is_inside_project(command):
    def wrapper_is_inside_project(*args, **kwargs):
        if inside_project():
            command(*args, **kwargs)
        else:
            click.echo(monitor_prompts["project_error"])

    return wrapper_is_inside_project
