How to run
----------

docker volume create crawler_output

docker build -t martan305/crawl_links .

docker run -it --env start='--start=501' --env length='--length=1' --name=crawl_links --mount source=crawler_output,destination=/opt/OpenWPM/datadir martan305/crawl_links

ls /var/lib/docker/volumes/crawler_output/_data

(on Windows: \\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\ )

docker push martan305/crawl_links




Delete all volumes:
docker volume rm $(docker volume ls -q)

Delete all containers:
docker rm -vf $(docker ps -a -q)

Delete all images:
docker rmi -f $(docker images -a -q)

