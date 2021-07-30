from ScoutSuite.output.export_scripts import json_to_excel
from ScoutSuite.output.export_scripts import findings
import json
import sys
from time import strftime
from datetime import datetime


def main():
    args = sys.argv[1:]
    file = ""
    save_file = ""

    if "--input" in args:
        index = args.index("--input")
        file = args[index + 1]
    if "--output" in args:
        index = args.index("--output")
        save_file = args[index + 1]
    viz_computing(file, save_file)


def build_json(json_file):
    """

    build a json containing computing information for excel reporting

    sheets:
        - EC2
        - AMI
        - Lambda
        - ECR
        - Snapshots
        - External attack surface
        - Findings
    """

    json_res = {}
    ec2 = get_ec2_all_regions(json_file["services"]["ec2"])
    roles = json_file["services"]["iam"]["roles"]
    groups = json_file["services"]["iam"]["groups"]
    policies = json_file["services"]["iam"]["policies"]
    json_res["sheet_list"] = ["Dashboard", "Findings", "Ec2", "AMI", "Lambda", "ECR", "Snapshots", "External attack surface"]
    json_res["sheet_data"] = {}

    json_res["sheet_data"]["Dashboard"] = build_dashboard(json_res["sheet_list"])
    json_res["sheet_data"]["Ec2"] = build_ec2_sheet(ec2)
    json_res["sheet_data"]["Groups"] = build_group_sheet(groups, policies)
    json_res["sheet_data"]["Roles"] = build_role_sheet(roles, policies)
    json_res["sheet_data"]["Policies"] = build_policy_sheet(policies)
    json_res["sheet_data"]["Findings"] = findings.build_finding_sheet(json_file, "ec2")

    return json.dumps(json_res)


def get_ec2_all_regions(json_file_ec2):
    ec2 = []

    for region_key, region in json_file_ec2.items():
        if region["instances_count"] != 0:
            for vpc_key, vpc in region["vpcs"]:
                for instance_key, instance in vpc["instances"]:
                    instance["vpc"] = vpc_key
                    instance["region"] = region_key
                    ec2.append(instance)
    return ec2


def build_ec2_sheet(ec2):
    header_list = ["Arn", "Name", "Instance Type", "State", "Iam instance profile", "Iam role", "User data",
                   "User data secrets", "Tags", "Region", "Launch time", "Key name", "Subnet Id", "Monitoring enabled",
                   "Reservation id"]
    cell_format = {
        "header_style": {'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2,
                         'top': 2, 'align': 'center', 'valign': 'vcenter'},
        "data_style": {
        },
        "conditional_format": {
        },
        "collapsed": {
            "Arn": {'level': 1, 'hidden': 1},
            "Iam instance profile": {'level': 1, 'hidden': 1},
            "Iam role": {'level': 1, 'hidden': 1},
            "User data": {'level': 1, 'hidden': 1},
            "User data secrets": {'level': 1, 'hidden': 1},
            "Launch time": {'level': 2, 'hidden': 1},
            "Key Name": {'level': 2, 'hidden': 1},
            "Subnet Id": {'level': 2, 'hidden': 1}
        }
    }

    data_ec2 = []

    for ec2_data in ec2:

        line = {
            "Arn": ec2_data["arn"],
            "Name": ec2_data["name"],
            "Instance Type": ec2_data["InstanceType"],
            "State": ec2_data["State"]["Name"],
            "Iam instance profile": json.dumps(ec2_data["IamInstanceProfile"]),
            "Iam role": json.dumps(ec2_data["iam_role"]),
            "User data": json.dumps(ec2_data["user_data"]),
            "User data secrets": json.dumps(ec2_data["user_data_secrets"]),
            "Tags": json.dumps(ec2_data["Tags"]),
            "Region": json.dumps(ec2_data["region"]),
            "Launch time": ec2_data["LaunchTime"][:-6],
            "Key name": json.dumps(ec2_data["KeyName"]),
            "Subnet id": json.dumps(ec2_data["SubnetId"]),
            "Monitoring enabled": json.dumps(ec2_data["monitoring_enabled"]),
            "Reservation id": json.dumps(ec2_data["reservation_id"])
        }

        data_ec2.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_ec2}

        return sheet_data


def build_ami_sheet(ami):
