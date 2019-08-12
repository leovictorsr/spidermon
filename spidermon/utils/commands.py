from importlib import import_module
from os import walk
from os.path import abspath, dirname, join
from scrapy.utils.project import get_project_settings

from spidermon.decorators.commands import is_packaged_installed

MONITOR_SETTINGS = [
    "# Settings generated by the Spidermon CLI",
    "SPIDERMON_ENABLED = True",
    "SPIDERMON_SPIDER_CLOSE_MONITORS = ('{}.monitors.SpiderCloseMonitorSuite',)",
]
PIPELINE_SETTINGS = [
    "ITEM_PIPELINES = {'spidermon.contrib.scrapy.pipelines.ItemValidationPipeline': 800, }"
]
EXTENSIONS_STRING = (
    "EXTENSIONS = {{'spidermon.contrib.scrapy.extensions.Spidermon': 500}}"
)
EXTENSIONS_UPDATE_STRING = (
    "EXTENSIONS.update({{'spidermon.contrib.scrapy.extensions.Spidermon': 500}})"
)
SPIDERMON_VALIDATION_MODELS = "SPIDERMON_VALIDATION_MODELS = {}"
SPIDERMON_VALIDATION_SCHEMAS = "SPIDERMON_VALIDATION_SCHEMAS = {}"
DICT_INPUT_FORMAT = "{}: {},"


def build_monitors_strings(monitors):
    monitors_list = []
    imports = []
    for monitor in monitors:
        monitors_list.append(monitor)
        imports.append("from {} import {}".format(monitors[monitor], monitor))

    return "[" + ",".join(monitors_list) + "]", "\n".join(imports)


def enable_spidermon():
    project_name = get_project_settings().get("BOT_NAME")

    extensions = get_project_settings().getdict("EXTENSIONS")
    if extensions:
        formatted_settings = "\n".join(MONITOR_SETTINGS + [EXTENSIONS_UPDATE_STRING])
    else:
        formatted_settings = "\n".join(MONITOR_SETTINGS + [EXTENSIONS_STRING])

    formatted_settings = formatted_settings.format(project_name)
    update_settings(formatted_settings)


def enable_pipeline():
    if not is_predefined_setting_setup("ITEM_PIPELINES"):
        update_settings(PIPELINE_SETTINGS)


def get_settings_path():
    module = import_module(get_project_settings().get("BOT_NAME"))
    return join(abspath(dirname(module.__file__)), "settings.py")


def parse_dict(keys, value):
    keys = parse_list(keys)
    return {key: parse_int(value) for key in keys}


def parse_int(entry):
    return int(entry)


def parse_list(entry):
    items = entry.split(",")
    return [i.strip() for i in items]


def is_setting_setup(setting):
    return (
        setting in get_project_settings().attributes
        and get_project_settings().get(setting) is not None
    )


def is_predefined_setting_setup(setting):
    return setting in get_project_settings().attributes and bool(
        get_project_settings().get(setting)
    )


def is_spidermon_enabled():
    if is_setting_setup("SPIDERMON_ENABLED"):
        return get_project_settings().get("SPIDERMON_ENABLED")
    return False


def is_valid(user_input, setting_type):
    if setting_type == "list":
        return bool(user_input)
    try:
        return int(user_input) > 0
    except:
        return False


def parse_user_input(user_input, setting_type):
    if setting_type == "list":
        return parse_list(user_input[0])
    elif setting_type == "dict":
        return parse_dict(user_input[1], user_input[0])
    return parse_int(user_input[0])


def update_settings(settings):
    with open(get_settings_path(), "a") as f:
        f.write("\n")
        if type(settings) == list:
            f.write("\n".join(settings))
        else:
            f.write(settings)
        f.write("\n")


@is_packaged_installed(module="schematics")
def find_schematics_schema_classes():
    import schematics

    try:
        validators = import_module(
            get_project_settings().get("BOT_NAME") + ".validators"
        )

        return [
            (cls.__name__, cls.__module__ + "." + cls.__name__)
            for i, cls in enumerate(schematics.models.Model.__subclasses__())
            if not is_setting_setup("SPIDERMON_VALIDATION_MODELS")
            or cls.__name__ not in get_project_settings()["SPIDERMON_VALIDATION_MODELS"]
        ]
    except ImportError:
        return []


@is_packaged_installed(module="jsonschema")
def find_jsonschema_schema_files():
    json_files = []
    module = import_module(get_project_settings().get("BOT_NAME"))
    for root, dirs, files in walk(abspath(dirname(module.__file__))):
        json_files += [
            (f.split(".")[0], abspath(f))
            for i, f in enumerate(files)
            if f.endswith(".json")
            and (
                not is_setting_setup("SPIDERMON_VALIDATION_SCHEMAS")
                or f.split(".")[0]
                not in get_project_settings()["SPIDERMON_VALIDATION_SCHEMAS"]
            )
        ]
    return json_files


def enable_schemas(schemas, module):
    settings = {s[0]: s[1] for s in schemas}
    if module == "schematics":
        settings = SPIDERMON_VALIDATION_MODELS.format(str(settings))
    elif module == "jsonschema":
        settings = SPIDERMON_VALIDATION_SCHEMAS.format(str(settings))

    try:
        update_settings(settings)
        return True
    except:
        return False
