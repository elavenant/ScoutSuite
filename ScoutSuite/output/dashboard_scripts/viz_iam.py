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
    viz_iam(file, save_file)

def build_json(json_file):
    """
    
    build a json containing users information for excel reporting
    
    parameters:
        - Name
        - Tags
        - Groups
        - Roles 
        - Permissions
        - MFA devices
        - Policies
        - Inline policies
        - Create date
        - Last use
        - Number of active AccessKeys 
    
    """
    
    json_res = {}
    users = json_file["services"]["iam"]["users"]
    roles = json_file["services"]["iam"]["roles"]
    groups = json_file["services"]["iam"]["groups"]
    policies = json_file["services"]["iam"]["policies"]
    json_res["sheet_list"] = ["Dashboard", "Users", "Roles", "Groups", "Policies", "Findings"]
    json_res["sheet_data"] = {}
  
    json_res["sheet_data"]["Dashboard"] = build_dashboard(json_res["sheet_list"])
    json_res["sheet_data"]["Users"] = build_user_sheet(users, roles, policies)
    json_res["sheet_data"]["Groups"] = build_group_sheet(groups, policies)
    json_res["sheet_data"]["Roles"] = build_role_sheet(roles, policies)
    json_res["sheet_data"]["Policies"] = build_policy_sheet(policies)
    json_res["sheet_data"]["Findings"] = findings.build_finding_sheet(json_file, "iam")
    
    return json.dumps(json_res)
    
def viz_iam(file, save_file):
    
    with open(file) as f:
        json_payload = f.readlines()
        json_payload.pop(0)
        json_payload = ''.join(json_payload)
        json_file = json.loads(json_payload)
    
    json_res = json.loads(build_json(json_file))
    json_to_excel.to_excel(json_res, save_file)
    

def build_dashboard(sheet_list):
    data_header = {"Version": "1.0", "Date": str(datetime.now()), "Auteurs": "ScoutSuite"}
    data_body = {
        "Findings": {
            "Findings": {
                "shortcut": "Findings",
                "description": "report of automated tests by ScoutSuite"
            }
        },
        "Main dashboards": {
            "Users": {
                "shortcut": "Users",
                "description": "information about users"
            },
            "Groups": {
                "shortcut": "Groups",
                "description": "information about groups"
            },
            "Roles": {
                "shortcut": "Roles",
                "description": "information about roles"
            },
            "Policies": {
                "shortcut": "Policies",
                "description": "information about policies"
            },
        }
    }
    data= {}
    data["data_header"] = data_header
    data["data_body"] = data_body
    return data

    
def build_user_sheet(users, roles, policies):
    """
    Users sheet
    """
    header_list = ["Name", "Human account", "Tags", "Groups", "Roles", "MFA devices", "Create date", "Last use", "Permissions", "Policies", "Inline policies", "Active access keys"]
    header_format = {
        "header_style": {'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2, 'top': 2, 'align': 'center', 'valign': 'vcenter'},
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
            "Permissions": {'level': 2,'hidden': 0},
            "Policies": {'level': 1,'hidden': 0},
            "Inline policies": {'level': 1,'hidden': 0},
            "Active access keys": {'level': 1,'hidden': 0}
        }
    }
    data_users = []
    user_roles = []
    
    for user_key, user in users.items():
        
        # Extracting the roles the user can assume
        for role_key, role in roles.items():
            for statement in role["assume_role_policy"]["PolicyDocument"]["Statement"]:
                if statement["Action"] == "sts:AssumeRole" and statement["Effect"] == "Allow":
                    for principal_key, arn in statement["Principal"].items():
                        if arn == user["arn"]:
                            user_roles.append(role["name"])
                            
        #Extracting user's policies
        user_policies = []
        if "policies" in user.keys():
            for policy in user["policies"]:
                user_policies.append(policies[policy]["name"])
                
        #Extracting last use info
        last_authenticated = ""
        if "LastAuthenticated" in user.keys():
            last_authenticated = user["LastAuthenticated"][:-6]
        
        line = {
            "Name": user["name"],
            "Tags": json.dumps(user["Tags"]),
            "Groups": json.dumps(user["groups"]),
            "Roles": json.dumps(user_roles),
            "MFA devices": json.dumps(user["MFADevices"]),
            "Create date": user["CreateDate"][:-6],
            "Last use": last_authenticated,
            "Permissions": [],
            "Policies": json.dumps(user_policies),
            "Inline policies": json.dumps(user["inline_policies"]),
            "Active access keys": json.dumps(user["AccessKeys"])
        }
        
        data_users.append(line)
         
    sheet_data = {"header_list": header_list,"cell_format": header_format, "data": data_users}
    
    return sheet_data
    
    
def build_group_sheet(groups, policies):
    """
    Group sheet
    """
    header_list = ["Name", "Create date", "Policies", "Inline policies"]
    cell_format = {
        "header_style": {'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2, 'top': 2, 'align': 'center', 'valign': 'vcenter'},
        "data_style": {
            "Create date": {'num_format': 'yyyy-mm-dd hh:mm:ss'},
        },
        "collapsed": {
            "Policies": {'level': 1,'hidden': 1},
            "Inline policies": {'level': 1,'hidden': 1}
        }
    }
    data_groups = []
    
    for group_key, group in groups.items():
        
        #Extracting group's policies
        group_policies = []
        for policy in group["policies"]:
            group_policies.append(policies[policy]["name"])
        
        line = {
            "Name": group["name"],
            "Create date": group["CreateDate"][:-6],
            "Policies": json.dumps(group_policies),
            "Inline policies": json.dumps(group["inline_policies"])
        }
        
        data_groups.append(line)
        
    sheet_data = {"header_list": header_list,"cell_format": cell_format, "data": data_groups}
    
    return sheet_data
    
    
def build_role_sheet(roles, policies):
    """
    Role sheet
    """
    header_list = ["Name", "Tags", "Description", "Create date", "Policies", "Inline policies"]
    cell_format = {
        "header_style": {'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2, 'top': 2, 'align': 'center', 'valign': 'vcenter'},
        "data_style": {
            "Create date": {'num_format': 'yyyy-mm-dd hh:mm:ss'}
        },
        "collapsed": {
            "Policies": {'level': 1,'hidden': 1},
            "Inline policies": {'level': 1,'hidden': 1}
        }
    }
    data_roles = []
    
    for role_key, role in roles.items():
        
        #Extracting role's policies
        role_policies = []
        for policy in role["policies"]:
            role_policies.append(policies[policy]["name"])
        
        line = {
            "Name": role["name"],
            "Create date": role["create_date"][:-6],
            "Policies": json.dumps(role_policies),
            "Inline policies": json.dumps(role["inline_policies"])
        }
        
        data_roles.append(line)
        
    sheet_data = {"header_list": header_list,"cell_format": cell_format, "data": data_roles}
    
    return sheet_data
                                          
def build_policy_sheet(policies):
    """
    Policy sheet
    """ 
                                          
    header_list = ["Name", "Group attached", "Role attached", "User attached"]
    cell_format = {
        "header_style": {'bold': True, 'bg_color': '#0070C0', 'font_color': 'white', 'left': 2, 'right': 2, 'bottom': 2, 'top': 2, 'align': 'center', 'valign': 'vcenter'},
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
        
    for policy_key, policy in policies.items():
         
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
    
    sheet_data = {"header_list": header_list,"cell_format": cell_format, "data": data_policies}
    
    return sheet_data
        
        
if __name__ == "__main__":
    main()