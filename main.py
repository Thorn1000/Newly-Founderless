import requests
import json

from bs4 import BeautifulSoup as BS

version = 0.1

headers = {
    "User-Agent": f"Newly Founderless Regions/{version} (developer: https://github.com/Thorn1000/Newly-Founderless ; user:Thorn1000;)"
}  # Im a good boy and set my useragent [v]


def clean_txt_files(first, second):
    with open('first.txt', 'r') as f:  # run a quick check to make sure first.txt has any data
        first_line = f.readline()
    if not first_line:  # if we have no data we copy the second file into the first then clear the second
        with open(first, 'a') as firstfile, open(second, 'r+') as secondfile:
            for line in secondfile:
                firstfile.write(line)
            secondfile.truncate(0)
    else:
        with open(second, 'r+') as f:
            f.truncate(0)  # clear the oldest data

    with open(first, 'r+') as firstfile, open(second, 'a') as secondfile:
        for line in firstfile:  # copy all the most recent data before any calls over to the oldest location
            secondfile.write(line)
        firstfile.truncate(0)  # clear all data in our original file to make room for new data
# yes this means that if we delete file 1 itll create file 1 copy data from file 2 to 1 and back to 2, sue me, I refuse to fix it


def api_work(first):
    targets = str(
        BS(requests.get(f"https://www.nationstates.net/cgi-bin/api.cgi?q=regionsbytag;tags=founderless,-password",
                        headers=headers).text, "xml").find_all("REGIONS"))  # our only API call or site interaction

    targets = targets.replace('[<REGIONS>', '')  # cleans the data before dumping it to the txt file
    targets = targets.replace('</REGIONS>]', '')  # I want a one region per line for the comparisons later
    targets = targets.replace(',', '\n')  # this is how it is accomplished

    with open(first, 'r+') as f:
        f.write(targets)  # take our now empty txt file and dump the cleaned API call into it


def compare_txt_files(file1, file2, json_file, backup_json):
    with open(file1, 'r') as f1:  # opens the newest data and dumps it to a list
        list1 = f1.read().splitlines()
    with open(file2, 'r') as f2:  # grabs the data from the run before this and makes a list
        list2 = f2.read().splitlines()

    diffs = set(list1) - set(list2)  # finds the differnce in this data and saves it to the diffs

    with open(json_file, 'r'):  # tries our first json file
        try:
            with open(json_file, 'r') as j1:
                data = json.load(j1)  # if we have data, cool
        except json.decoder.JSONDecodeError:  # if we dont, try the backup
            try:
                with open(backup_json, 'r') as j2:
                    data = json.load(j2)  # if we haev backup data, cool
            except json.decoder.JSONDecodeError:
                data = {}  # if neither work, lmfao make data and be sad this line was reached

    for diff in diffs:
        if diff not in data:
            data[diff] = 0  # add new regions to the json data with a value of 0 updates while CTEd

    for key in data.iterkeys():
        if key not in list1:  # if a region is in the json and not in the most recent call, delete it, ie founder back
            data.pop(key)  # I dont think I have a good way to test this, dunno if it works
        else:
            data[key] += 1  # if the data is found, incriment it by 1. Dunno if i should start at 0 or -1
            if data[key] >= 15:  # if its been 1 week, delete the data so we only have this weeks CTEs
                data.pop(key)

    sorted_data = dict(sorted(dict(data).items(), key=lambda item: (item[1], item[0])))
    # ^ this makes a new dictionary which is just the previous one sorted for recency then alphabeticaly
    with open(json_file, 'w') as f:
        json.dump(sorted_data, f, indent=2)  # overrwrites the json file with updated data, one per line

    with open(backup_json, 'w') as f:  # write data to a hopefully redundant backup
        json.dump(sorted_data, f, indent=2)


if __name__ != "__main__":
    pass
else:
    clean_txt_files('first.txt', 'second.txt')  # clean our little files
    api_work('first.txt')  # make the sole API request and do some cleaning
    compare_txt_files('first.txt', 'second.txt', 'stored.json', 'backup.json')  # heavy lifting with all the logic
