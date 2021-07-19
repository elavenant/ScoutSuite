from ScoutSuite.output.dashboard_scripts.visualization import Visualization
from ScoutSuite.output.export_scripts import json_to_excel
import json
import sys
from time import strftime
from datetime import datetime


class AWSIAMVisualization(Visualization):

    def __init__(self, input):
        self.input = input
        self.users = self.input["services"]["iam"]["users"]
        self.roles = self.input["services"]["iam"]["roles"]
        self.groups = self.input["services"]["iam"]["groups"]
        self.policies = self.input["services"]["iam"]["policies"]
        self.json = {"sheet_list": [], "sheet_data": {}}

    def build_json(self):
        """

            build a json containing users information for excel reporting

            sheets:
                - Dashboard
                - Users
                - Roles
                - Groups
                - Policies
                - Findings

        """

        json_res = {"sheet_list": ["Users", "Roles", "Groups", "Policies"], "sheet_data": {}}

        json_res["sheet_data"]["Users"] = self.build_user_sheet()
        json_res["sheet_data"]["Groups"] = self.build_group_sheet()
        json_res["sheet_data"]["Roles"] = self.build_role_sheet()
        json_res["sheet_data"]["Policies"] = self.build_policy_sheet()

        self.json = json_res

    def build_user_sheet(self):
        """
        Users sheet
        """
        header_list = ["Arn", "Name", "Human account", "Tags", "Groups", "Roles", "MFA devices", "Create date",
                       "Last use", "Permissions", "Policies", "Inline policies", "Active access keys"]
        cell_format = {
            "header_style": {'bold': True, 'bg_color': '#60497A', 'font_color': 'white', 'left': 2, 'right': 2,
                             'bottom': 2, 'top': 2, 'align': 'center', 'valign': 'vcenter'},
            "data_style": {
                "Create date": {'num_format': 'yyyy-mm-dd hh:mm:ss'},
                "Last use": {'num_format': 'yyyy-mm-dd hh:mm:ss'}
            },
            "conditional_format": {
                "MFA devices": [
                    {
                        'type': 'formula',
                        'criteria': 'AND(${Human account}2="Yes", ${MFA devices}2="[]")',
                        'format': {'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'}
                    },
                    {
                        'type': 'formula',
                        'criteria': 'OR(${Human account}2="No", ${MFA devices}2<>"[]")',
                        'format': {'bg_color': '#C6EFCE',
                                   'font_color': '#006100'}
                    }
                ],
                "Groups": [
                    {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': '[]',
                        'format': {'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'}
                    }
                ]
            },
            "collapsed": {
                "Arn": {'level': 1, 'hidden': 0},
                "Permissions": {'level': 2, 'hidden': 0},
                "Policies": {'level': 1, 'hidden': 0},
                "Inline policies": {'level': 1, 'hidden': 0},
                "Active access keys": {'level': 1, 'hidden': 0}
            }
        }
        data_users = []
        user_roles = []

        for user_key, user in self.users.items():

            # Extracting the roles the user can assume
            for role_key, role in self.roles.items():
                for statement in role["assume_role_policy"]["PolicyDocument"]["Statement"]:
                    if statement["Action"] == "sts:AssumeRole" and statement["Effect"] == "Allow":
                        for principal_key, arn in statement["Principal"].items():
                            if arn == user["arn"]:
                                user_roles.append(role["name"])

            # Extracting user's policies
            user_policies = []
            if "policies" in user.keys():
                for policy in user["policies"]:
                    user_policies.append(self.policies[policy]["name"])

            # Extracting last use info
            last_authenticated = ""
            if "LastAuthenticated" in user.keys():
                last_authenticated = user["LastAuthenticated"][:-6]

            line = {
                "Arn": user["arn"],
                "Name": user["name"],
                "Tags": json.dumps(user["Tags"], indent=4),
                "Groups": json.dumps(user["groups"], indent=4),
                "Roles": json.dumps(user_roles, indent=4),
                "MFA devices": json.dumps(user["MFADevices"], indent=4),
                "Create date": user["CreateDate"][:-6],
                "Last use": last_authenticated,
                "Permissions": [],
                "Policies": json.dumps(user_policies, indent=4),
                "Inline policies": json.dumps(user["inline_policies"], indent=4),
                "Active access keys": json.dumps(user["AccessKeys"], indent=4)
            }

            data_users.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_users}

        return sheet_data

    def build_group_sheet(self):
        """
        Group sheet
        """
        header_list = ["Arn", "Name", "Create date", "Policies", "Inline policies"]
        cell_format = {
            "header_style": {'bold': True, 'bg_color': '#60497A', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2,
                             'top': 2, 'align': 'center', 'valign': 'vcenter'},
            "data_style": {
                "Create date": {'num_format': 'yyyy-mm-dd hh:mm:ss'},
            },
            "collapsed": {
                "Arn": {'level': 1, 'hidden': 1},
                "Policies": {'level': 1, 'hidden': 1},
                "Inline policies": {'level': 1, 'hidden': 1}
            }
        }
        data_groups = []

        for group_key, group in self.groups.items():

            # Extracting group's policies
            group_policies = []
            for policy in group["policies"]:
                group_policies.append(self.policies[policy]["name"])

            line = {
                "Arn": group["arn"],
                "Name": group["name"],
                "Create date": group["CreateDate"][:-6],
                "Policies": json.dumps(group_policies, indent=4),
                "Inline policies": json.dumps(group["inline_policies"], indent=4)
            }

            data_groups.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_groups}

        return sheet_data

    def build_role_sheet(self):
        """
        Role sheet
        """
        header_list = ["Arn", "Name", "Tags", "Description", "Create date", "Policies", "Inline policies"]
        cell_format = {
            "header_style": {'bold': True, 'bg_color': '#60497A', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2,
                             'top': 2, 'align': 'center', 'valign': 'vcenter'},
            "data_style": {
                "Create date": {'num_format': 'yyyy-mm-dd hh:mm:ss'}
            },
            "collapsed": {
                "Arn": {'level': 1, 'hidden': 1},
                "Policies": {'level': 1, 'hidden': 1},
                "Inline policies": {'level': 1, 'hidden': 1}
            }
        }
        data_roles = []

        for role_key, role in self.roles.items():

            # Extracting role's policies
            role_policies = []
            if "policies" in role.keys():
                for policy in role["policies"]:
                    role_policies.append(self.policies[policy]["name"])

            line = {
                "Arn": role["arn"],
                "Name": role["name"],
                "Create date": role["create_date"][:-6],
                "Policies": json.dumps(role_policies, indent=4),
                "Inline policies": json.dumps(role["inline_policies"], indent=4)
            }

            data_roles.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_roles}

        return sheet_data

    def build_policy_sheet(self):
        """
        Policy sheet
        """

        header_list = ["Name", "Group attached", "Role attached", "User attached"]
        cell_format = {
            "header_style": {'bold': True, 'bg_color': '#60497A', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2,
                             'top': 2, 'align': 'center', 'valign': 'vcenter'},
            "data_style": {
            },
            "conditional_format": {
                "User attached": [
                    {
                        'type': 'text',
                        'criteria': 'containing',
                        'value': '[',
                        'format': {'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'}
                    }
                ]
            },
            "collapsed": {
            }
        }

        data_policies = []

        for policy_key, policy in self.policies.items():

            line = {
                "Name": policy["name"],
            }
            if "groups" in policy["attached_to"].keys():
                group_list = []
                for group_dict in policy["attached_to"]["groups"]:
                    group_list.append(group_dict["name"])
                line["Group attached"] = group_list
            if "roles" in policy["attached_to"].keys():
                role_list = []
                for role_dict in policy["attached_to"]["roles"]:
                    role_list.append(role_dict["name"])
                line["Role attached"] = role_list
            if "users" in policy["attached_to"].keys():
                user_list = []
                for user_dict in policy["attached_to"]["users"]:
                    user_list.append(user_dict["name"])
                line["User attached"] = user_list

            data_policies.append(line)

        sheet_data = {"header_list": header_list, "cell_format": cell_format, "data": data_policies}

        return sheet_data


def get_id(arn):
    index = arn.find("::") + 2
    arn = arn[index:]
    index = arn.find(":")
    arn = arn[:index]

    return arn


