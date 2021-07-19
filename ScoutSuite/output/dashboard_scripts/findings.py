import json
from ScoutSuite.output.dashboard_scripts.visualization import Visualization


class AWSFindingsVisualization(Visualization):

    def __init__(self, input, service_list):
        self.service_list = service_list
        self.input = input
        self.services = {}
        self.json = {}

    def build_json(self):
        header_list = ["Id", "Name", "Description", "Rationale", "Category", "Sub category", "Risk associated", "Items", "Items list", "Level", "Compliance", "Scoring scale", "Macro filter selector", "Macro filter button", "References", "Remediation", "Checked items", "Flagged items", "Path"]
        cell_format = {
            "header_style": {'bold': True, 'bg_color': '#60497A', 'font_color': 'white',
                             'align': 'center', 'valign': 'vcenter'},
            "data_style": {
                "default": {'border': 1, 'align': 'center', 'valign': 'vcenter'},
                "merged_h1": {'bold': True, 'bg_color': '#946BC5', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1},
                "merged_h2": {'bold': True, 'bg_color': '#9E9E9E', 'font_color': 'white', 'align': 'center', 'valign': 'vcenter', 'border': 1},
                "Scoring scale": {'text_wrap': True},
                "Items": {'text_wrap': True},
                "Risk associated": {'text_wrap': True},
                "Macro filter button": {'bg_color': "#D5D5D5"}
            },
            "conditional_format": {
                "Level": [
                    {
                        'type': 'text',
                        'criteria': 'containing',
                        "value": 'danger',
                        'format': {'bg_color': '#FF0000',
                                   'font_color': 'white',
                                   }
                    },
                    {
                        'type': 'text',
                        'criteria': 'containing',
                        "value": 'warning',
                        'format': {'bg_color': '#FFC000',
                                   'font_color': '#5F5F5F',
                                   }
                    },
                    {
                        'type': 'text',
                        'criteria': 'containing',
                        "value": 'low',
                        'format': {'bg_color': '#FFFF00',
                                   'font_color': '#5F5F5F',
                                   }
                    }
                ],
                "Compliance": [
                    {
                        'type': 'cell',
                        'criteria': '=',
                        "value": 0,
                        'format': {'bg_color': '#FF7C80',
                                   'font_color': 'white',
                                   }
                    },
                    {
                        'type': 'cell',
                        'criteria': '=',
                        "value": 1,
                        'format': {'bg_color': '#92D050',
                                   'font_color': 'white',
                                   }
                    },
                    {
                        'type': 'cell',
                        'criteria': '=',
                        "value": -1,
                        'format': {'bg_color': '#808080',
                                   'font_color': 'white',
                                   }
                    }
                ]
            },
            "collapsed": {
                "Name": {'level': 2, 'hidden': 1},
                "References": {'level': 2, 'hidden': 1},
                "Flagged items": {'level': 2, 'hidden': 1},
                "Checked items": {'level': 2, 'hidden': 1},
                "Path": {'level': 2, 'hidden': 1},
                "Items list": {'level': 2, 'hidden': 1},
                "Remediation": {'level': 1, 'hidden': 1},
                "Rationale": {'level': 1, 'hidden': 1},
                "Macro filter selector": {'hidden': 1}
            }
        }

        data_findings = []
        for service in self.service_list:
            findings = self.input["services"][service]["findings"]
            sub_categories = []

            data_findings.append({'merged_type': 'merged_h1', 'text': service.upper()})

            findings = dict(sorted(findings.items(), key=lambda item: item[1]["dashboard_name"]))
            findings = dict(sorted(findings.items(), key=lambda item: item[1]["id"]))

            for finding_key, finding in findings.items():

                finding_completed = finding

                for field in header_list:
                    field = field.lower().replace(" ", "_")
                    if field not in finding.keys():
                        finding_completed[field] = ""

                if finding_completed["dashboard_name"] not in sub_categories:
                    data_findings.append({'merged_type': 'merged_h2', 'text': finding_completed["dashboard_name"]})
                    sub_categories.append(finding_completed["dashboard_name"])

                rsc = []
                beautify_rsc = ""
                rsc_id = ""
                macro_filter = {"enabled": False, "command": {'macro': "'filterById \"Resources\"'",
                                                                               'caption': 'View items',
                                                                               'width': 70,
                                                                               'height': 20}}

                if finding_completed["flagged_items"] > 0:
                    rsc_name, rsc_arn, rsc_id = find_rsc(self.input, finding_completed)

                    ''' preparing macro filter array '''
                    macro_filter["enabled"] = True

                    ''' Beautifying the flagged resources list for display'''
                    if "Impossible to retrieve the name of the resource" not in rsc_name:
                        beautify_rsc = "\n".join(rsc_name)
                    else:
                        beautify_rsc = "\n".join(rsc_arn)

                    if "Impossible to retrieve the arn of the resource" not in rsc_arn:
                        rsc = rsc_arn
                    else:
                        rsc = rsc_name

                line = {
                    "Id": finding_completed["id"],
                    "Name": finding_key,
                    "Description": finding_completed["description"],
                    "Rationale": finding_completed["rationale"],
                    "Compliance": 0 if finding_completed["flagged_items"] > 0 else 1,
                    "Category": service.upper(),
                    "Sub category": finding_completed["dashboard_name"],
                    "Checked items": finding_completed["checked_items"],
                    "Flagged items": finding_completed["flagged_items"],
                    "Level": finding_completed["level"],
                    "Macro filter selector": ",".join(rsc_id),
                    "Macro filter button": macro_filter,
                    'Items': beautify_rsc,
                    'Items list': json.dumps(rsc),
                    "Scoring scale": "Compliant: 1\nNot compliant: 0",
                    "References": "\n".join(finding_completed["references"]) if finding_completed["references"] else "",
                    "Path": finding_completed["path"],
                    "Remediation": finding_completed["remediation"],
                    "Risk associated": "\n".join(finding_completed["associated_risks"] if finding_completed["associated_risks"] else "")
                }

                # If the rule isn't enabled, put -1 in compliance
                if not finding_completed["enabled"]:
                    line["Compliance"] = -1

                data_findings.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_findings}

        self.json = {"sheet_list": ["Controls"], "sheet_data": {"Controls": sheet_data}}


# Allows to find resources by path and returns their "name" or "arn"
def find_rsc(json_file, rule):
    path = rule["display_path"].split('.') if "display_path" in rule.keys() else rule["path"].split('.')
    items = rule["items"]
    id_type = ""
    rsc = []
    rsc_name = []
    rsc_arn = []
    rsc_id = []

    if "id" in path:
        for item in items:
            item = item.split('.')
            temp = json_file["services"]
            for chain_id, chain in enumerate(path):
                temp = temp[item[chain_id]]

            keys = []
            for key in temp.keys():
                keys.append(str(key))
            keys_upper = [x.upper() for x in keys]
            if "NAME" in keys_upper:
                rsc_name.append(temp[keys[keys_upper.index("NAME")]])
            else:
                rsc_name.append("Impossible to retrieve the name of the resource")
            if "ARN" in keys_upper:
                rsc_arn.append(temp[keys[keys_upper.index("ARN")]])
            else:
                rsc_arn.append("Impossible to retrieve the arn of the resource")
            if "ID" in keys_upper:
                rsc_id.append(temp[keys[keys_upper.index("ID")]])
            else:
                rsc_id.append(item[len(path)-1])

    return rsc_name, rsc_arn, rsc_id

