""" Command for getting links from given webpage.

Author: Marek Schauer

"""
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
