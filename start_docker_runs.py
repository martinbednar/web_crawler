from subprocess import run
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

while start+offset <= stop_on_page_index:
	print("#############################################")
	print("#######  C R A W L   S T A R T I N G  #######")
	print("#############################################")
	print("Start: " + str(start))
	print("Offset: " + str(offset))
	print("Privacy: " + str(privacy))
	print("#############################################")
	logging.debug("CRAWL STARTING:")
	logging.debug("-Start: %s", start)
	logging.debug("-Offset: %s", offset)
	
	env_file = "start=--start=" + str(start) + "\noffset=--offset=" + str(offset) + "\n"
	
	if privacy:
		volume_name = "crawl_" + str(start) + "_privacy"
	else:
		env_file += "privacy=\n"
		volume_name = "crawl_" + str(start)
	
	
	with open('docker_crawl.env', 'w') as f:
		f.write(env_file)
	
	cmd_vol = ["docker", "volume", "create", volume_name]
	cmd_run = ["docker", "run", "-it", "--name=" + volume_name + "", "--env-file", "docker_crawl.env", "--mount", "source=" + volume_name + ",destination=/opt/OpenWPM/datadir", "martan305/web_crawler"]
	
	run(cmd_vol)
	try:
		run(cmd_run, timeout=(offset*45)/3+600)
	except:
		logging.debug("CRAWL TIMEOUT")
		failure_counter += 1
		cmd_clean1 = ["docker", "stop", volume_name]
		cmd_clean2 = ["docker", "rm", volume_name]
		cmd_clean3 = ["docker", "volume", "rm", volume_name]
		run(cmd_clean1)
		run(cmd_clean2)
		run(cmd_clean3)
		
		if failure_counter >= 3:
			# Skip current block and continue crawling.
			logging.debug("Skipping this block, because current number of failures reached: %s", str(failure_counter))
			failure_counter = 0
			start += offset
		else:
			logging.debug("Try to crawl this block again. Current number of failures: %s", str(failure_counter))
	else:
		logging.debug("CRAWLED SUCCESSFULLY")
		failure_counter = 0
		start += offset

