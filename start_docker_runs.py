from subprocess import run
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--privacy", help="run the crawls with privacy extension", action="store_true")
args = parser.parse_args()

start = 0
offset = 1
privacy = getattr(args, 'privacy')

while True:
	print("#############################################")
	print("#######  C R A W L   S T A R T I N G  #######")
	print("#############################################")
	print("Start: " + str(start))
	print("Offset: " + str(offset))
	print("Privacy: " + str(privacy))
	print("#############################################")
	
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
	run(cmd_run)
	
	start += offset

