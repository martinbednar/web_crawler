How to run
----------

docker volume create crawler_output

docker build -t web_crawler .

docker run -it --name=web_crawler --mount source=crawler_output,destination=/opt/OpenWPM/datadir web_crawler

ls /var/lib/docker/volumes/crawler_output/_data

