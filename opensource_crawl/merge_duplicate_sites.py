may_be_duplicat = False
merged_http = []


with open("opensource_homepages") as file:
	for line in file:
		line = line.rstrip()
		
		if may_be_duplicat and line.startswith("https://"):
			may_be_duplicat = False
			if merged_http[-1][7:] == line[8:]:
				print(line[8:])
				print(merged_http[-1][7:])
				merged_http[-1] = line
			else:
				merged_http.append(line)
		elif not line.startswith("https://") and line.startswith("http://"):
			may_be_duplicat = True
			merged_http.append(line)
		else:
			merged_http.append(line)


may_be_duplicat = False
merged_slash = []


for line in merged_http:
	if not line.endswith("/") and len(merged_slash) > 0:
		if merged_slash[-1][:-1] == line:
			print(merged_slash[-1][:-1])
			print(line)
		else:
			merged_slash.append(line)
	else:
		merged_slash.append(line)



with open('opensource_homepages_merged', 'w') as f:
	for item in merged_slash:
		f.write("%s\n" % item)

