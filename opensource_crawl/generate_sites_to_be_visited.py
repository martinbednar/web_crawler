import sqlite3
import json

sqliteConnection = sqlite3.connect('crawl-data.sqlite')

sqliteConnection.row_factory = sqlite3.Row

cursor = sqliteConnection.cursor()

sqlite_select_Query = "SELECT site_url as site_url, links_count as links_count, subpage_links as links, id as id FROM site_links"
cursor.execute(sqlite_select_Query)
data = cursor.fetchall()
cursor.close()

output = '{"sites": ['

for row in data:
    output += '{"site_url": "' + row['site_url'] + '", "links_count": ' + str(row['links_count']) + ', "links": ' + row['links'] + ', "tranco_rating": "' + str(row['id']) + '"}, '

output = output[:-2]
output += ']}'

with open('oupensource_sites_to_be_visited.json', 'w') as f:
    f.write(output)

