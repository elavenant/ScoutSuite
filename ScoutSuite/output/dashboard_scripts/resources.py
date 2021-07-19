import json
from ScoutSuite.output.dashboard_scripts.visualization import Visualization


class AWSResourcesVisualization(Visualization):
    def __init__(self, input, service_list):
        self.input = input
        self.service_list = service_list
        self.services = {}
        self.json = {}

        self.get_services()

    def get_services(self):
        for service in self.service_list:
            for key, data in self.input["metadata"].items():
                if service in data.keys():
                    self.services[service] = {}
                    for resource_key, resource_data in data[service]["resources"].items():
                        if "full_path" in resource_data:
                            path = resource_data["full_path"]
                        else:
                            path = resource_data["path"]
                        path = path.split('.')
                        self.services[service][resource_key] = get_service(self.input, path)

    def build_json(self):
        header_list = ["Id", "Name", "Arn", "Category", "Sub category", "Description", "Tags"]
        cell_format = {
            "header_style": {'bold': True, 'bg_color': '#60497A', 'font_color': 'white',
                             'align': 'center', 'valign': 'vcenter'},
            "data_style": {
                "default": {'border': 1, 'align': 'center', 'valign': 'vcenter'},
                "merged_h1": {'bold': True, 'bg_color': '#946BC5', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1},
                "merged_h2": {'bold': True, 'bg_color': '#9E9E9E', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1},
            },
            "conditional_format": {},
            "collapsed": {
                "Description": {'level': 1, 'hidden': 1},
                "Tags": {'level': 1, 'hidden': 1},
                "Id": {'level': 2, 'hidden': 1},
            }
        }

        data_resources = []
        for service in self.service_list:
            data_resources.append({'merged_type': 'merged_h1', 'text': service.upper()})
            for sub_category_key, sub_category_data in self.services[service].items():
                data_resources.append({'merged_type': 'merged_h2', 'text': sub_category_key})
                for rsc_key, rsc_data in sub_category_data.items():

                    tags = ""
                    if "tags" in rsc_data.keys():
                        for tag in rsc_data["tags"]["Tags"]:
                            tags += "'" + tag["Key"] + "': " + "'" + tag["Value"] + "'"

                    line = {
                        "Id": rsc_data["id"] if "id" in rsc_data.keys() else rsc_key,
                        "Name": rsc_data["name"] if "name" in rsc_data.keys() else "",
                        "Arn": rsc_data["arn"] if "arn" in rsc_data.keys() else "",
                        "Category": service,
                        "Sub category": sub_category_key,
                        "Description": rsc_data["description"] if "description" in rsc_data.keys() and rsc_data["description"] is not None else "",
                        "Tags": tags
                    }

                    data_resources.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_resources}

        self.json = {"sheet_list": ["Resources"], "sheet_data": {"Resources": sheet_data}}

    def get_sheet(self):
        return self.json


def get_service(json_file, path):
    data = []
    temp = json_file
    if len(path) == 1:
        return json_file[path[0]]
    else:
        if path[0] != "id":
            return get_service(json_file[path[0]], path[1:])
        else:
            res = {}
            for key in json_file.keys():
                res = {**res, **get_service(json_file[key], path[1:])}
            return res
