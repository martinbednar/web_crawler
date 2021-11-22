from subprocess import run
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--privacy", help="run the crawls with privacy extension", action="store_true")
args = parser.parse_args()

start = 5000
offset = 250
privacy = getattr(args, 'privacy')

while True:
	print("#############################################")
	print("#######  C R A W L   S T A R T I N G  #######")
	print("#############################################")
	print("Start: " + str(start))
	print("Offset: " + str(offset))
	print("Privacy: " + str(privacy))
	print("#############################################")
	
	abc = "./touch"
	if privacy:
		volume_name = "crawl_" + str(start) + "_privacy"
		cmd_vol = ["docker", "volume", "create", volume_name]
		cmd_run = ["docker", "run", "-it", "--env-file", "docker_crawl_privacy.env", "--mount", "source=" + volume_name + ",destination=/opt/OpenWPM/datadir", "martan305/web_crawler"]
	else:
		volume_name = "crawl_" + str(start)
		cmd_vol = ["docker", "volume", "create", volume_name]
		cmd_run = ["docker", "run", "-it", "--env-file", "docker_crawl.env", "--mount", "source=" + volume_name + ",destination=/opt/OpenWPM/datadir", "martan305/web_crawler"]
		
	run(cmd_vol)
	run(cmd_run)
	
	start += 1
