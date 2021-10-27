How to run
----------

docker volume create crawler_output

docker build -t martan305/web_crawler .

docker run -it --name=web_crawler --mount source=crawler_output,destination=/opt/OpenWPM/datadir martan305/web_crawler

ls /var/lib/docker/volumes/crawler_output/_data

(on Windows: \\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\ )

docker push martan305/web_crawler




Delete all volumes:
docker volume rm $(docker volume ls -q)

Delete all containers:
docker rm -vf $(docker ps -a -q)

Delete all images:
docker rmi -f $(docker images -a -q)

