# Web Crawler

**This branch contains a tool for getting links from the homepages of the websites.**

Web Crawler is a tool for automatically visiting websites and collecting JavaScript calls that they make. Web Crawler is based on OpenWPM.

[OpenWPM](https://github.com/openwpm/OpenWPM) is a platform that allows a large number of websites to be visited in order to perform various measurements on the web.
In our work, we extended OpenWPM with a modified [Web API Manager extension](https://github.com/pes10k/web-api-manager), which we use to detect access to various JavaScript APIs in a web browser.



## Run without Docker (in native OS Ubuntu)

### Installation

The OpenWPM platform can be installed according to official documentation.

The recommended operating system on which Web Crawler has been tested is Ubuntu 18.04.

1) Install [Conda environment](https://docs.conda.io/en/latest/miniconda.html).
1) Run the script `install.sh`.
1) Activate environment `openwpm` by running command `conda activate openwpm`.

### Extension of the Tranco list by subpages
To extend the Tranco list by subpages, we can use the `crawl-links.py` script, which accepts 3 input parameters:

````
--sites={string}
--start={integer}
--length={integer}
````

The `--sites={string}` parameter specifies the path to the input file that contains the Tranco list in CSV format.
The `--start={integer}` parameter then specifies the initial index from which the given Tranco list is to be extended by a list of subpages.
The `--length={integer}` parameter specifies the length of the resulting sub-page list.

The results will be recorded in a SQLite database in the `./datadir` folder.
You need to export the JSON file from this SQLite database and edit it to have the same format as the `sites_to_be_visited.json` file.


## Run in a Docker container

The recommended way is to launch a Web Crawler in the Docker container.

### Create the Docker image

Build Docker image:

```
docker build -t martan305/crawl_links .
```

Run links crawling:

```
docker volume create crawler_output
docker run -it --env start='--start=0' --env length='--length=1' --name=crawl_links --mount source=crawler_output,destination=/opt/OpenWPM/datadir martan305/crawl_links
```

Check crawler output:

```
ls /var/lib/docker/volumes/crawler_output/_data

(on Windows: \\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\ )
```

Push the new version of the Docker image to Docker Hub:

```
docker push martan305/crawl_links
```


### Docker clean up

Delete all containers:
```
docker rm -vf $(docker ps -a -q)
```

Delete all volumes:
```
docker volume rm $(docker volume ls -q)
```

Delete all images:
```
docker rmi -f $(docker images -a -q)
```
