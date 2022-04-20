# \file
#  \brief Program to measure JS API calls for given set of pages.
#  
#   \author Copyright (C) 2021  Marek Schauer
#  
#   \license SPDX-License-Identifier: GPL-3.0-or-later
# 
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
# 
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
# 
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <https://www.gnu.org/licenses/>.
# 

from pathlib import Path

from intercept_javascript_command import InterceptJavaScriptCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.commands.browser_commands import BrowseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

import os
import argparse
import csv
import re
import json
import functools

import redis

class RedisQueue:
    redis = None

    def __init__(self, queue_name):
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            self.redis = redis.from_url(redis_url)
        self.queue_name = queue_name

    def __iter__(self):
        return self

    def __next__(self):
        if self.redis and self.redis.llen(self.queue_name):
            return json.loads(self.redis.lpop(self.queue_name).decode())
        raise StopIteration



parser = argparse.ArgumentParser()
parser.add_argument("--browsers", help="number of browsers to be spawned", type=int, required=True)
parser.add_argument("--sites", help="path to JSON file containing information about sites to be crawled, required attributes are \"site\" and \"links\"", type=str)
parser.add_argument("--start", help="index to start on", type=int, default=0)
parser.add_argument("--offset", help="how many websites should be taken", type=int)
parser.add_argument("--privacy", help="run the crawl with privacy extension", action="store_true")
args = parser.parse_args()

# The list of sites that we wish to crawl
NUM_BROWSERS = int(getattr(args, 'browsers'))

inputFilePath = getattr(args, 'sites')
sites_iterable = []  # sites placeholder
if inputFilePath:
    offset_start = int(getattr(args, 'start'))
    offset_end = int(getattr(args, 'start')) + int(getattr(args, 'offset'))

    sites = []
    with open(getattr(args, 'sites'), "r") as json_file:
        data = json.load(json_file)
        sites = data['sites']
    sites_iterable = sites[offset_start:offset_end]
else:
    sites_iterable = RedisQueue('sites')


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
    # We want install our modified Web API manager, not a default extension
    browser_params[i].extension_enabled = True
    browser_params[i].extension_default = False
    browser_params[i].extension_web_api_manager = True
    if getattr(args, 'privacy'):
        # We want install extension increesing privacy
        browser_params[i].extension_privacy = True


# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")

# memory_watchdog and process_watchdog are useful for large scale cloud crawls.
# Please refer to docs/Configuration.md#platform-configuration-options for more information
# manager_params.memory_watchdog = True
# manager_params.process_watchdog = True


sqlite_name = os.environ.get('HOSTNAME', 'crawl-data') + '.sqlite'

# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path(f"./datadir/{sqlite_name}")),
    None,
) as manager:
    # Visits the sites
    for index, siteObj in enumerate(sites_iterable):

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
