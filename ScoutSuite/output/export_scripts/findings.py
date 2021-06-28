import json


def build_findings(json_file, service):
    header_list = ["Name", "Description", "Rationale", "Compliance", "Checked items", "Flagged items", "Level", "References", "Path", "Remediation"]
    header_format = {
        "header_style": {'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2,
                         'top': 2, 'align': 'center', 'valign': 'vcenter'},
        "data_style": {
        },
        "conditional_format": {
            "level": [
                {
                    'type': 'text',
                    'criteria': 'containing',
                    "value": 'danger',
                    'format': {'bg_color': '#FFC7CE',
                               'font_color': '#9C0006',
                               "bold": True
                               }
                },
                {
                    'type': 'text',
                    'criteria': 'containing',
                    "value": 'warning',
                    'format': {'bg_color': '#FFC000',
                               'font_color': '#9C6502',
                               "bold": True
                               }
                },
                {
                    'type': 'text',
                    'criteria': 'containing',
                    "value": 'low',
                    'format': {'bg_color': '#C6EFCE',
                               'font_color': '#006100',
                               "bold": True
                               }
                }
            ]
        },
        "autofilter": ["Name", "Compliance", "Checked items", "Flagged_items", "Level"],
        "collapsed": {
            "References": {'level': 1, 'hidden': 0},
            "Path": {'level': 1, 'hidden': 0},
            "Remediation": {'level': 1, 'hidden': 0}
        }
    }

    findings = json_file["services"][service]["findings"]
    data_findings = {}

    for finding_key, finding in findings.items():

        finding_completed = finding

        for field in header_list:
            field = field.lower().replace(" ", "_")
            if field not in finding.keys():
                finding_completed[field] = ""

        line = {
            "Name": finding_key,
            "Description": finding_completed["description"],
            "Rationale": finding_completed["rationale"],
            "Compliance": finding_completed["compliance"],
            "Checked items": finding_completed["checked_items"],
            "Flagged items": finding_completed["flagged_items"],
            "Level": finding_completed["level"],
            "References": json.dumps(finding_completed["references"]),
            "Path": finding_completed["path"],
            "Remediation": finding_completed["remediation"]
        }

        data_findings.append(line)

    sheet_data = {"header_list": header_list, "cell_format": header_format, "data": data_findings}

    return sheet_data
