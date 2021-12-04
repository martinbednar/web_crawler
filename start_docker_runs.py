from subprocess import run
import os
import shutil
from zipfile import ZipFile
import sqlite3
import argparse
import logging

parser = argparse.ArgumentParser()
parser.add_argument("--privacy", help="run the crawls with privacy extension", action="store_true")
args = parser.parse_args()

start = 0
offset = 1
privacy = getattr(args, 'privacy')
stop_on_page_index = 1000000
# Max 3 failures in the same block (start+offset)
failure_counter = 0

if privacy:
	logging_filename = 'docker_runs_privacy.log'
else:
	logging_filename = 'docker_runs.log'

logging.basicConfig(level=logging.DEBUG, filename=logging_filename, filemode='w', format='%(asctime)s - %(message)s')


def is_root():
    return os.geteuid() == 0


def delete_crawl(volume_name):
	cmd_clean1 = ["docker", "stop", volume_name]
	cmd_clean2 = ["docker", "rm", volume_name]
	cmd_clean3 = ["docker", "volume", "rm", volume_name]
	run(cmd_clean1)
	run(cmd_clean2)
	run(cmd_clean3)


def get_docker_volume_folder(volume_name):
	if os.name == 'nt':
		# I run on Windows.
		return "//wsl$/docker-desktop-data/version-pack-data/community/docker/volumes/" + volume_name + "/_data/"
	else:
		return "/var/lib/docker/volumes/" + volume_name + "/_data/"


def get_percent_successfully_crawled_websites(volume_name):
	docker_volume_folder = get_docker_volume_folder(volume_name)
	db = sqlite3.connect(docker_volume_folder + "crawl-data.sqlite")
	cur = db.cursor()
	sql_query = "SELECT top_level_url FROM javascript GROUP BY top_level_url"
	cur.execute(sql_query)
	websites_visited = len(cur.fetchall())
	db.close()
	return(100*websites_visited/offset)


def move_db_to_output_folder(volume_name, start, offset):
	docker_volume_folder = get_docker_volume_folder(volume_name)
	os.mkdir(volume_name)
	shutil.copyfile(docker_volume_folder + "crawl-data.sqlite", volume_name + "/" + volume_name + ".sqlite")
	shutil.copyfile(docker_volume_folder + "openwpm.log", volume_name + "/" + volume_name + ".log")
	with ZipFile(volume_name + ".zip", 'w') as zip_obj:
		zip_obj.write(volume_name + "/" + volume_name + ".sqlite", volume_name + ".sqlite")
		zip_obj.write(volume_name + "/" + volume_name + ".log", volume_name + ".log")
	shutil.rmtree(volume_name)


if not is_root():
	print("Run me as a root, please. I need administrator privileges to read from the folder " + get_docker_volume_folder("crawl_0") + ".")
	exit()

while start+offset <= stop_on_page_index:
	print("#############################################")
	print("#######  C R A W L   S T A R T I N G  #######")
	print("#############################################")
	print("Start: " + str(start))
	print("Offset: " + str(offset))
	print("Privacy: " + str(privacy))
	print("#############################################")
	logging.debug("#############################################")
	logging.debug("CRAWL STARTING:")
	logging.debug("-Start: %s", start)
	logging.debug("-Offset: %s", offset)
	
	env_file = "start=--start=" + str(start) + "\noffset=--offset=" + str(offset) + "\n"
	
	if privacy:
		volume_name = "crawl_" + str(start)  + "-" + str(start+offset) + "_privacy"
	else:
		env_file += "privacy=\n"
		volume_name = "crawl_" + str(start)  + "-" + str(start+offset)
	
	
	with open('docker_crawl.env', 'w') as f:
		f.write(env_file)
	
	cmd_vol = ["docker", "volume", "create", volume_name]
	cmd_run = ["docker", "run", "-it", "--name=" + volume_name + "", "--env-file", "docker_crawl.env", "--mount", "source=" + volume_name + ",destination=/opt/OpenWPM/datadir", "martan305/web_crawler"]
	
	run(cmd_vol)
	try:
		run(cmd_run, timeout=(offset*50)/3+600)
	except:
		logging.debug("CRAWL TIMEOUT")
		failure_counter += 1
		
		if failure_counter >= 3:
			# Skip current block and continue crawling.
			logging.debug("Skipping this block, because current number of failures reached: %s", str(failure_counter))
			failure_counter = 0
			start += offset
		else:
			logging.debug("Try to crawl this block again. Current number of failures: %s", str(failure_counter))
	else:
		succesfully_crawled_websites = get_percent_successfully_crawled_websites(volume_name)
		if (succesfully_crawled_websites > 75):
			logging.debug("CRAWLED SUCCESSFULLY")
			move_db_to_output_folder(volume_name, start, offset)
			failure_counter = 0
			start += offset
		elif failure_counter >= 3:
			# Skip current block and continue crawling.
			logging.debug("Skipping this block, because current number of failures reached: %s", str(failure_counter))
			failure_counter = 0
			start += offset
		else:
			logging.debug("CRAWLED LESS THAN 75 PERCENT WEBSITES")
			logging.debug("Only %s percent websites was succesfully crawled.", str(succesfully_crawled_websites))
			logging.debug("Try to crawl this block again. Current number of failures: %s", str(failure_counter))
			failure_counter += 1
	# Save disk space.
	delete_crawl(volume_name)

