from ScoutSuite.output.export_scripts import json_to_excel
import abc
import json


class Visualization(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.json = {}

    @abc.abstractmethod
    def build_json(self, json_file):
        # Method to build dict object
        return

    def add_sheet(self, sheet, name):
        self.json["sheet_list"].append(name)
        self.json["sheet_data"][name] = sheet

    def load_json_from_file(self):
        with open(self.input) as f:
            json_payload = f.readlines()
            json_payload.pop(0)
            json_payload = ''.join(json_payload)
            self.json = json.loads(json_payload)

    def save(self):
        json_to_excel.to_excel(self.json, self.output)
