may_be_duplicat = False
merged = []


with open("opensource_homepages") as file:
	for line in file:
		current = line.rstrip()
		while not current[-1].isalnum():
			current = current[:-1]
		
		if len(merged) > 0:
			current_cleaned = current.removeprefix("https://www.").removeprefix("http://www.").removeprefix("https://").removeprefix("http://")
			previous = merged[-1]
			previous_cleaned = previous.removeprefix("https://www.").removeprefix("http://www.").removeprefix("https://").removeprefix("http://")
			if current_cleaned == previous_cleaned:
				print(previous)
				print(current)
				if previous.startswith("http://") and current.startswith("https://"):
					merged[-1] = previous.replace("http://", "https://")
			else:
				merged.append(current)
		else:
			merged.append(current)



with open('opensource_homepages_merged', 'w') as f:
	for item in merged:
		f.write("%s\n" % item)

