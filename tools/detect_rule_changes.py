import sys
from bs4 import BeautifulSoup
import requests
import json
from termcolor import colored
import colorama
from os import listdir
from os.path import isfile, join

''' This script allows to verify if rules from cloud conformity are still up to date '''


def main():
    colorama.init()
    args = sys.argv[1:]
    if args[0] == "aws":
        path = "../ScoutSuite/providers/aws/rules/findings/"
    elif args[0] == "azure":
        path = "../ScoutSuite/providers/azure/rules/findings/"
    else:
        print("Wrong arguments, the usage is: detect_rule_changes.py [provider] [action]\nprovider is aws or azure "
              "and action compare or update")
        return -1
    if args[1] == "compare":
        action = "compare"
    elif args[1] == "update":
        action = "update"
    else:
        print(
            "Wrong arguments, the usage is: detect_rule_changes.py [provider] [action]\nprovider is aws or azure and "
            "action compare or update")
        return -1

    meta_path = path + "meta/meta.json"
    meta = load_file(meta_path)
    files = meta.keys()

    for file in files:
        f = open(path + file, 'r')
        try:
            data = json.load(f)
        except:
            continue
        f.close()
        try:
            urls = [s for s in data["references"] if "https://www.cloudconformity.com/" in s]
            if urls:
                url = urls[0]
                req = requests.get(url)

                soup = BeautifulSoup(req.text, "html.parser")
                date = soup.find(
                    'div',
                    {"class": "publication-date"}
                ).span.text
        except Exception as e:
            print(e)
        else:
            to_date = meta[file] == date
            if action == "compare":
                if to_date:
                    print(colored(file + ": rule up to date", "green"))
                if not to_date:
                    print(colored(file + ": rule needs to be checked", "yellow"))
            elif action == "update":
                meta[file] = date

    if action == "update":
        save_file(meta_path, meta)


def load_file(path):
    f = open(path, 'r')
    try:
        meta = json.load(f)
    except Exception as e:
        print(e)
    f.close()
    return meta


def save_file(path, file):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(file, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    main()