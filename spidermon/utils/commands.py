from importlib import import_module
from os.path import abspath, dirname, join
from scrapy.utils.project import get_project_settings

MONITOR_SETTINGS = [
    "# Settings generated by the Spidermon CLI",
    "SPIDERMON_ENABLED = True",
    "EXTENSIONS = {}",
    "SPIDERMON_SPIDER_CLOSE_MONITORS = ('{}.monitors.SpiderCloseMonitorSuite',)",
]
EXTENSION_SETTING = {"spidermon.contrib.scrapy.extensions.Spidermon": 500}


def build_monitors_strings(monitors):
    monitors_list = []
    imports = []
    for monitor in monitors:
        monitors_list.append(monitor)
        imports.append("from {} import {}".format(monitors[monitor], monitor))

    return "[" + ",".join(monitors_list) + "]", "\n".join(imports)


def enable_spidermon():
    extensions = dict(get_project_settings().get("EXTENSIONS"))
    if extensions:
        extensions.update(EXTENSION_SETTING)
    else:
        extensions = EXTENSION_SETTING

    project_name = get_project_settings().get("BOT_NAME")
    formatted_settings = "\n".join(MONITOR_SETTINGS).format(
        str(extensions), project_name
    )
    with open(get_settings_path(), "a") as f:
        f.write(formatted_settings)
        f.write("\n")


def get_settings_path():
    module = import_module(get_project_settings().get("BOT_NAME"))
    return join(abspath(dirname(module.__file__)), "settings.py")


def is_setting_setup(setting):
    with open(get_settings_path(), "r") as f:
        read_data = f.read()

    return setting in read_data


def is_spidermon_enabled():
    settings = get_project_settings()
    return settings["SPIDERMON_ENABLED"]


def include_setting(settings):
    with open(get_settings_path(), "a") as f:
        f.write("\n".join(settings))
        f.write("\n")
