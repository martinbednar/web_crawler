# \file
#  \brief Command for intercepting JS API calls for given set of pages.
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

import json
import logging
import random
import time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket
from openwpm.storage.storage_controller import DataSocket, StorageControllerHandle
from openwpm.storage.storage_providers import (
    StructuredStorageProvider,
    TableName,
    UnstructuredStorageProvider,
)

from openwpm.commands.browser_commands import GetCommand

from openwpm.commands.utils.webdriver_utils import (
    get_intra_links,
    is_displayed,
    wait_until_loaded,
)


class InterceptJavaScriptCommand(BaseCommand):
    """This command visits links of given page"""

    def __init__(self, siteObj, sleep) -> None:
        self.logger = logging.getLogger("openwpm")
        self.siteObj = siteObj
        self.url = siteObj['site_url']
        self.urls = siteObj['links']

        self.sleep = sleep

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "InterceptJavaScriptCommand({},{})".format(self.url, self.sleep)

    
    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:

        current_url = webdriver.current_url

        
        for url in self.urls:
            self.logger.info('I am going to visit following subpage of %s: %s', self.url, url)
            try:
                # Lets visit the subpage
                get_command = GetCommand(url, self.sleep)
                get_command.set_visit_browser_id(self.visit_id, self.browser_id)
                get_command.execute(
                    webdriver,
                    browser_params,
                    manager_params,
                    extension_socket,
                )

            except Exception as e:
                self.logger.error(
                    "BROWSER %i: Error visiting url %s",
                    browser_params.browser_id,
                    url,
                    exc_info=e,
                )
