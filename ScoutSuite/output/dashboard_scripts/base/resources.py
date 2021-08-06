import json
from ScoutSuite.output.dashboard_scripts.base.visualization import Visualization


class ResourcesVisualization(Visualization):
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
