from pathlib import Path

from intercept_javascript_command import InterceptJavaScriptCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.commands.browser_commands import BrowseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

import argparse
import csv
import re
import json

parser = argparse.ArgumentParser()
parser.add_argument("--sites", help="path to JSON file containing information about sites to be crawled, required attributes are \"site\" and \"links\"", type=str)
parser.add_argument("--start", help="index to start on", type=int)
parser.add_argument("--offset", help="how many websites should be taken", type=int)
parser.add_argument("--ghostery", help="run the crawl with ghostery", action="store_true")
args = parser.parse_args()

args = parser.parse_args()
offset_start = int(getattr(args, 'start'))
offset_end = int(getattr(args, 'start')) + int(getattr(args, 'offset'))

inputFilePath = getattr(args, 'sites')


# The list of sites that we wish to crawl
NUM_BROWSERS = 1
sites = []
with open(getattr(args, 'sites'), "r") as json_file:
    data = json.load(json_file)
    sites = data['sites']
sites = sites[offset_start:offset_end]


# Loads the default ManagerParams
# and NUM_BROWSERS copies of the default BrowserParams
manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="headless") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for i in range(NUM_BROWSERS):
    # Record HTTP Requests and Responses
    browser_params[i].http_instrument = False
    # Record cookie changes
    browser_params[i].cookie_instrument = False
    # Record Navigations
    browser_params[i].navigation_instrument = False
    # Record JS Web API calls
    browser_params[i].js_instrument = True
    # Record the callstack of all WebRequests made
    browser_params[i].callstack_instrument = False
    # Record DNS resolution
    browser_params[i].dns_instrument = False
    # We want default extension, not a Web API manager
    browser_params[i].web_api_manager_enabled = True
    if getattr(args, 'ghostery'):
        # Load our custom profile
        browser_params[i].seed_tar = Path("./ghostery-profile.tar.gz")


# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_directory = Path("./datadir/")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
# manager_params.memory_watchdog = True
# manager_params.process_watchdog = True






# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite")),
    None,
) as manager:
    # Visits the sites
    for index, siteObj in enumerate(sites):

        def callback(success: bool, val: str = siteObj['site_url']) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            siteObj['site_url'],
            site_rank=index,
            callback=callback,
            reset=True
        )

        # Visiting the page
        # command_sequence.append_command(GetCommand(url=site, sleep=15), timeout=60)
        timeout = int(siteObj['links_count']) * 60
        command_sequence.append_command(InterceptJavaScriptCommand(siteObj=siteObj, sleep=30), timeout=timeout)

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
