from ScoutSuite.output.dashboard_scripts.base.resources import ResourcesVisualization


class AzureResourcesVisualization(ResourcesVisualization):
    def __init__(self, input, service_list):
        super().__init__(input, service_list)

    def build_json(self):
        header_list = ["Id", "Name", "Resource group", "Category", "Sub category", "Tags"]
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
                        for tag in rsc_data["tags"]:
                            tags += tag + "\n"

                    line = {
                        "Id": rsc_data["id"] if "id" in rsc_data.keys() else rsc_key,
                        "Name": rsc_data["name"] if "name" in rsc_data.keys() else "",
                        "Resource group": rsc_data["resource_group_name"] if "resource_group_name" in rsc_data.keys() else "",
                        "Category": service,
                        "Sub category": sub_category_key,
                        "Tags": tags
                    }

                    data_resources.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_resources}

        self.json = {"sheet_list": ["Resources"], "sheet_data": {"Resources": sheet_data}}
