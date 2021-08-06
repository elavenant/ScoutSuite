import sys
import json
from ScoutSuite.output.dashboard_scripts.aws.iam_visualization import AWSIAMVisualization
from ScoutSuite.output.dashboard_scripts.aws.resources import AWSResourcesVisualization
from ScoutSuite.output.dashboard_scripts.azure.resources import AzureResourcesVisualization
from ScoutSuite.output.dashboard_scripts.base.findings import FindingsVisualization
from ScoutSuite.output.export_scripts import json_to_excel


REPORT_PATH = 'scoutsuite-report/'
RESULTS_PATH = 'scoutsuite-report/scoutsuite-results/'


class Excel:

    def __init__(self, provider, services, file_input, file_output):
        self.file_output = file_output
        self.file_input = file_input
        self.services = services
        self.provider = provider
        self.json_file = {}
        self.visualizations = []
        self.json = {"sheet_list": [], "sheet_data": {}}

        # loading data in json
        self.load_json()

        # Adding default dashboard
        self.add_dashboard()

        # if full services wanted
        if not self.services:
            self.get_full_services()

    def load_json(self):
        with open(RESULTS_PATH + self.file_input) as f:
            json_payload = f.readlines()
            json_payload.pop(0)
            json_payload = ''.join(json_payload)
            self.json_file = json.loads(json_payload)

    def generate(self):

        if self.provider == 'aws':

            self.visualizations.append(AWSResourcesVisualization(self.json_file, self.services))
            self.visualizations.append(FindingsVisualization(self.json_file, self.services))

            # If IAM is the only service we can add detailed version
            if self.services == ["iam"]:
                self.visualizations.append(AWSIAMVisualization(self.json_file))

        elif self.provider == 'azure':

            self.visualizations.append(AzureResourcesVisualization(self.json_file, self.services))
            self.visualizations.append(FindingsVisualization(self.json_file, self.services))

        self.build_json()
        self.merge_json()

        self.save()

    def build_json(self):
        for i in range(len(self.visualizations)):
            self.visualizations[i].build_json()

    def merge_json(self):
        for visualization in self.visualizations:
            for sheet in visualization.json["sheet_list"]:
                self.json["sheet_list"].append(sheet)
                self.json["sheet_data"].update(visualization.json["sheet_data"])

    def get_full_services(self):
        self.services = self.json_file["service_list"]

    def save(self):
        json_to_excel.to_excel(self.json, REPORT_PATH + self.file_output)

    def add_dashboard(self):
        self.json["sheet_list"].append("Dashboard")
        sheet_data = {}
        last_run = self.json_file["last_run"]["time"]
        ruleset_name = self.json_file["last_run"]["ruleset_name"]
        provider = self.json_file["provider_code"].upper()
        account = self.json_file["account_id"]

        sheet_data["Information"] = {
            "Provider": provider,
            "Rule set used": ruleset_name,
            "Last run": last_run
        }

        sheet_data["Provider information"] = {
            "Account": account
        }

        self.json["sheet_data"]["Dashboard"] = sheet_data

