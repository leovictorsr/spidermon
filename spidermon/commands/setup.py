import click
import itertools

from spidermon.commands.prompts import monitor_prompts, validation_prompts
from spidermon.decorators.commands import is_inside_project
from spidermon.utils import monitors as monitors_manager
from spidermon.utils.commands import (
    build_monitors_strings,
    enable_schemas,
    enable_spidermon,
    enable_pipeline,
    find_jsonschema_schema_files,
    find_schematics_schema_classes,
    is_predefined_setting_setup,
    is_setting_setup,
    is_spidermon_enabled,
    is_valid,
    parse_dict,
    parse_int,
    parse_list,
    parse_user_input,
    update_settings,
)
from spidermon.utils import file_utils

VALIDATION_OPTIONS = ["schematics", "jsonschema"]
VALIDATION_SEARCH_FUNCTIONS = {
    "schematics": find_schematics_schema_classes,
    "jsonschema": find_jsonschema_schema_files,
}


@click.command(
    "setup",
    help="Enable Spidermon and setup the monitors from the Scrapy Monitor Suite.",
)
@is_inside_project
def setup():
    if is_spidermon_enabled():
        click.echo(monitor_prompts["already_enabled"])
    else:
        enable_spidermon()
        click.echo(monitor_prompts["enabled"])

    enable_monitors()

    if click.confirm("\n" + validation_prompts["enable"]):
        enable_pipeline()
        enable_validation()


def enable_monitors():
    monitors = {}
    settings = []
    for module in monitors_manager.find_monitor_modules():
        new_monitors, new_settings = get_monitors_with_settings(module)
        monitors.update(new_monitors)
        settings += new_settings

    monitors_list, imports = build_monitors_strings(monitors)
    filename = file_utils.copy_template_to_project("monitor_suite.py.tmpl")

    if settings:
        update_settings(settings)
    file_utils.render_file(filename, monitors_list=monitors_list, imports=imports)

    click.echo(monitor_prompts["response"])


def enable_validation():
    options = {i + 1: name for (i, name) in enumerate(VALIDATION_OPTIONS)}
    schemas_list = [
        "[{}] {}".format(i + 1, option) for i, option in enumerate(VALIDATION_OPTIONS)
    ]

    msg = "\n".join(schemas_list)
    msg = validation_prompts["validation_schema"].format(msg)
    click.echo("\n")
    while True:
        selected_type = click.prompt(msg)
        if is_valid(selected_type, "int") and parse_int(selected_type) in options:
            selected_type = options[parse_int(selected_type)]
            schemas = []
            try:
                if selected_type in VALIDATION_SEARCH_FUNCTIONS:
                    schemas = VALIDATION_SEARCH_FUNCTIONS[selected_type]()
            except ImportError:
                msg = validation_prompts["response_error"]
                click.echo(click.style(msg, fg="red", bg="white"))
                return

            if not schemas:
                click.echo(validation_prompts["response_no_schema"])
                msg = validation_prompts["response_error"]
                click.echo(click.style(msg, fg="red", bg="white"))
                return

            schemas = get_schemas_to_enable(schemas)
            if enable_schemas(schemas, selected_type):
                click.echo(validation_prompts["response"])
                return

            click.echo("\n")
            click.echo(click.style(msg, fg="red", bg="white"))
            click.echo(validation_prompts["response_error"])
            return
        elif not click.confirm(validation_prompts["invalid_validation_schema"]):
            click.echo(validation_prompts["response_error"])
            return


def get_schemas_to_enable(schemas):
    validators = []
    while True:
        if not schemas:
            return validators

        item_list = [
            "[{}] {}".format(i + 1, schema[0]) for i, schema in enumerate(schemas)
        ]

        msg = "\n".join(item_list)
        msg = validation_prompts["validation_list"].format(msg)
        click.echo("\n")
        selected_schema = click.prompt(msg)

        msg = validation_prompts["validation_list_error"]
        if is_valid(selected_schema, "int") and parse_int(selected_schema) <= len(
            schemas
        ):
            item_index = parse_int(selected_schema) - 1
            validators.append(schemas[item_index])
            item_list.pop(item_index)
            schemas.pop(item_index)
        elif not click.confirm(msg):
            return validators

        msg = validation_prompts["validation_list_confirm"]
        if schemas and not click.confirm(msg):
            return validators


def get_monitors_with_settings(module):
    monitors = {}
    settings = []
    for monitor in module["monitors"]:
        msg = monitor_prompts["enable"].format(module["monitors"][monitor]["name"])
        if click.confirm("\n" + msg):
            monitors[monitor] = module["path"]
            settings += get_settings(module["monitors"][monitor])

    return monitors, settings


def get_settings(monitor):
    settings = []
    setting = monitor["setting"]
    name = monitor["name"]

    if is_setting_setup(setting):
        click.echo(monitor_prompts["setting_already_setup"].format(name))
        return settings

    setting_string = monitor["setting_string"]
    setting_type = monitor["setting_type"]
    description = monitor["description"]

    user_input = get_user_input(setting_type, description)
    if user_input:
        setting = setting_string.format(user_input)
        settings.append(setting)

    return settings


def get_user_input(setting_type, description):
    while True:
        user_input = []
        setting_types = []
        user_input += [click.prompt(monitor_prompts[setting_type].format(description))]
        setting_types += [setting_type]
        if setting_type == "dict":
            user_input += [click.prompt(monitor_prompts["list"].format(description))]
            setting_types += ["list"]

        if all(is_valid(a, b) for (a, b) in zip(user_input, setting_types)):
            return parse_user_input(user_input, setting_type)
        elif not click.confirm(monitor_prompts["setting_error"]):
            return []
