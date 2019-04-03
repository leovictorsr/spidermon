import pytest

from scrapy import Spider
from scrapy.crawler import Crawler
from spidermon.contrib.scrapy.runners import SpiderMonitorRunner
from spidermon.python import factory, PythonExpressionMonitor
from spidermon import MonitorSuite
from spidermon.exceptions import NotConfigured

@pytest.fixture
def make_data(request):
    def _make_data(settings=None):
        crawler = Crawler(Spider, settings=settings)
        spider = Spider("dummy")
        return {
            "stats": crawler.stats.get_stats(),
            "crawler": crawler,
            "spider": spider,
            "runner": SpiderMonitorRunner(spider=spider),
            "job": None,
        }

    return _make_data

@pytest.fixture
def make_dict(request):
    def _make_dict():
        test = {
            "expression":
        }
        return {
            "tests":
        }

    return _make_dict

@pytest.fixture
def make_json(request):
    def _make_json():
        return {

        }

    return _make_dict

def test_should_create_monitor_class_from_dict(make_dict):
    """Factory should create an instance of PythonExpressionsMonitor with dict as parameter"""

def test_should_create_monitor_class_from_json(make_json):
    """Factory should create an instance of PythonExpressionsMonitor with json as parameter"""

def test_python_expressions_monitors_should_fail():
    """Python expressions monitors should fail when expression is not found"""

def test_python_expressions_monitors_should_pass():
    """Python expressions monitors should pass when expression is found"""

def test_needs_to_configure_python_expressions_monitor(make_data, item_count_suite):
    """Should raise an exception when PythonExpressionsMonitor it's not configured"""
    data = make_data()
    runner = data.pop("runner")
    data["crawler"].stats.set_value("item_scraped_count", 10)
    with pytest.raises(NotConfigured):
        runner.run(item_count_suite, **data)
