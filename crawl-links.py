# \file
#  \brief Program to get the subpages for given set of pages.
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

from get_links_command import GetLinksCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.commands.browser_commands import BrowseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

import argparse
import csv
import re


def formaturl(url):
    if not re.match('(?:http|https)://', url):
        return 'http://{}'.format(url)
    return url


parser = argparse.ArgumentParser()
parser.add_argument("--sites", help="path to CSV file containing sites to crawl in format (id, domain)", type=str, required=True)
parser.add_argument("--start", help="offset to start on", type=int, required=True)
parser.add_argument("--length", help="length of resulting list", type=int, required=True)
args = parser.parse_args()

args = parser.parse_args()
offset_start = getattr(args, 'start')
result_length = getattr(args, 'length')
offset_end = getattr(args, 'start') + result_length

inputFilePath = getattr(args, 'sites')


# The list of sites that we wish to crawl
NUM_BROWSERS = 1
sites = []
with open(inputFilePath, newline='') as csvfile:
    # Let's fill the sites array
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
    for row in spamreader:
        url = row[1]
        if not (url in sites):
            sites.append(formaturl(url))

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
    browser_params[i].js_instrument = False
    # Record the callstack of all WebRequests made
    browser_params[i].callstack_instrument = False
    # Record DNS resolution
    browser_params[i].dns_instrument = False
    # We want default extension, not a Web API manager
    browser_params[i].web_api_manager_enabled = False


# Update TaskManager configuration (use this for crawl-wide settings)
manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")



# Commands time out by default after 60 seconds
with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite")),
    None,
) as manager:
    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )

        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=index,
            callback=callback,
            reset=True
        )

        # Start by visiting the page
        # command_sequence.append_command(GetCommand(url=site, sleep=15), timeout=60)
        # Have a look at custom_command.py to see how to implement your own command
        command_sequence.append_command(GetLinksCommand(url=site, num_links=3, sleep=5), timeout=180)

        # Run commands across all browsers (simple parallelization)
        manager.execute_command_sequence(command_sequence)
