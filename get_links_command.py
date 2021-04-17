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


class GetLinksCommand(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self, url, num_links, sleep) -> None:
        self.logger = logging.getLogger("openwpm")
        self.url = url
        self.num_links = num_links
        self.sleep = sleep
        self.resultUrls = {url}

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "GetLinksCommand({},{},{})".format(self.url, self.num_links, self.sleep)

    
    def getRandomLinks(self, links, n):
        urls = list(map(lambda x: x.get_attribute("href"), links))
        uniqueUrls = set(urls)
        newUrls = uniqueUrls.difference(self.resultUrls)

        if len(newUrls) > 0:
            randomUrls = list(set(random.choices(list(newUrls), k=n)))
            return randomUrls
        
        return list()
    
    
    def getLinksFrom(
        self, 
        url, 
        n,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ):
        get_command = GetCommand(url, self.sleep)
        get_command.set_visit_browser_id(self.visit_id, self.browser_id)
        get_command.execute(
            webdriver,
            browser_params,
            manager_params,
            extension_socket,
        )
        # Lets get links of this subpage
        subpageLinks = [
            x
            for x in get_intra_links(webdriver, url)
            if is_displayed(x) is True
        ]
        subpageUrls = self.getRandomLinks(links=subpageLinks, n=3)
        
        return subpageUrls

    
    def getOutput(self):
        url = self.url
        count = len(self.resultUrls)
        linksJson = json.dumps(list(self.resultUrls))
        outputTemplate = "From the site {} we collected these {} urls:\n{}\n\n"
        output = outputTemplate.format(url, count, linksJson)
        return output
    
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

        get_command = GetCommand(self.url, self.sleep)
        get_command.set_visit_browser_id(self.visit_id, self.browser_id)
        get_command.execute(
            webdriver,
            browser_params,
            manager_params,
            extension_socket,
        )
        
        homepageLinks = [
            x
            for x in get_intra_links(webdriver, self.url)
            if is_displayed(x) is True
        ]

        resultHomepageUrls = self.getRandomLinks(links=homepageLinks, n=3)
        self.resultUrls.update(resultHomepageUrls)
        resultSubpagesLinks = set()

        self.logger.info('******************************')
        self.logger.info('I picked these three links:')
        for url in resultHomepageUrls:
            self.logger.info('\t%s', url)
            try:
                # Lets get that subpage
                subpageUrls = self.getLinksFrom(
                                url, 
                                3,
                                webdriver,
                                browser_params,
                                manager_params,
                                extension_socket,
                            )
                self.resultUrls.update(subpageUrls)
                
            except Exception as e:
                self.logger.error(
                    "BROWSER %i: Error visiting internal url %s",
                    browser_params.browser_id,
                    url,
                    exc_info=e,
                )
        
        sock = DataSocket(manager_params.storage_controller_address)

        sock.store_record(
            TableName("site_links"),
            self.visit_id,
            {
                "visit_id": self.visit_id,
                "browser_id": self.browser_id,
                "site_url": self.url,
                "links_count": len(list(self.resultUrls)),
                "subpage_links": json.dumps(list(self.resultUrls)),
            },
        )

        sock.close()  # close socket to storage controller

        # Lets write the gathered links out
        self.logger.info('===========================================================')
        self.logger.info('These %d links were gathered from %s: %s', len(self.resultUrls), self.url, list(self.resultUrls))
        self.logger.info('===========================================================')
