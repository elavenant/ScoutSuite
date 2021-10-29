import json
import sys
import xlsxwriter


class Dashboard:

    def __init__(self, workbook, dashboard_data):
        self.workbook = workbook
        self.dashboard_data = dashboard_data

        cell_format_header = {
            'bold': False,
            'bg_color': '#503078',
            'font_color': 'white',
            'font_size': 20,
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'bottom': 1,
            'top': 1
        }
        cell_format_header_light = {
            'bold': False,
            'bg_color': '#946BC5',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'bottom': 1,
            'top': 1
        }
        cell_format_base = {
            'bold': True,
            'text_wrap': True,
            'bg_color': 'white',
            'font_color': 'black',
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'bottom': 1,
            'top': 1
        }
        cell_format_dashboard_danger = {
            'bg_color': '#FF5050',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'bottom': 1,
            'top': 1
        }
        cell_format_dashboard_warning = {
            'bg_color': '#FABF8F',
            'font_color': '#5F5F5F',
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'bottom': 1,
            'top': 1
        }
        cell_format_dashboard_low = {
            'bg_color': '#FFFF66',
            'font_color': '#5F5F5F',
            'align': 'center',
            'valign': 'vcenter',
            'left': 1,
            'right': 1,
            'bottom': 1,
            'top': 1
        }

        self.cell_format_base = workbook.add_format(cell_format_base)
        self.cell_format_dashboard_danger = workbook.add_format(cell_format_dashboard_danger)
        self.cell_format_dashboard_warning = workbook.add_format(cell_format_dashboard_warning)
        self.cell_format_dashboard_low = workbook.add_format(cell_format_dashboard_low)
        self.cell_format_header = workbook.add_format(cell_format_header)
        self.cell_format_header_light = workbook.add_format(cell_format_header_light)

        self.cell_format = {
            "cell_format_header": self.cell_format_header,
            "cell_format_header_light": self.cell_format_header_light,
            "cell_format_base": self.cell_format_base,
            "cell_format_dashboard_danger": self.cell_format_dashboard_danger,
            "cell_format_dashboard_warning": self.cell_format_dashboard_warning,
            "cell_format_dashboard_low": self.cell_format_dashboard_low
        }

        self.sheet = self.workbook.add_worksheet("Dashboard")

    def create(self):
        self._create_dashboard()

    def _create_dashboard(self):
        self.sheet.set_row(0, 50)
        self.sheet.merge_range("A1:H1", "Dashboard", self.cell_format["cell_format_header"])

        row = 3
        col = 1
        for key, data in self.dashboard_data.items():
            if key != "Alerts":
                row += self._create_block(row, col, {"header": key, "body": data}) + 2
            else:
                row += self._create_block_compliance(row, col, {"header": key, "body": data}) + 2

        # Columns can be hidden explicitly. This doesn't increase the file size..
        self.sheet.set_column('H:XFD', None, None, {'hidden': True})

    def _create_block(self, row, col, data):
        self._create_block_header(row, col, 4, data)
        nb_rows = self._create_block_body(row + 1, col, 4, data)

        # Returns the number of rows created
        return nb_rows + 1

    def _create_block_header(self, row, col, length, data):
        self.sheet.set_row(row, 20)
        self.sheet.merge_range(row, col, row, col + length -1, data["header"], self.cell_format["cell_format_header"])
        self.sheet.set_column(col, 400)
        self.sheet.set_column(col + 1, 1000)

    def _create_block_body(self, row, col, length, data):
        row_index = 0
        for row_index, key in enumerate(data["body"].keys()):
            self.sheet.write(row + row_index, col, key, self.cell_format["cell_format_base"])
            self.sheet.merge_range(row + row_index, col + 1, row + row_index, col + length - 1, data["body"][key],
                                   self.cell_format["cell_format_base"])

        return row_index + 1

    def _create_block_compliance(self, row, col, data):
        self._create_block_header(row, col, 4, data)
        return self._create_block_compliance_body(row+1, col, data) + 1

    def _create_block_compliance_body(self, row, col, data):
        row_index = 0
        col_index = col
        labels = ["Service", "Danger alert", "Warning alert", "Low alert"]

        for label in labels:
            self.sheet.write(row + row_index, col_index, label, self.cell_format["cell_format_header_light"])
            col_index += 1
        row_index += 1

        for service in data["body"]["services"]:
            self.sheet.write(row + row_index, col, service, self.cell_format["cell_format_base"])
            self.sheet.write_formula(row + row_index, col + 1,
                                     '=COUNTIFS(Controls!E1:E91,"='+service+'",Controls!J1:J91,"=danger",Controls!K1:K91,"=0") & "/" & COUNTIFS(Controls!E1:E91,"='+service+'",Controls!J1:J91,"=danger")',
                                     self.cell_format["cell_format_dashboard_danger"])
            self.sheet.write_formula(row + row_index, col + 2,
                                     '=COUNTIFS(Controls!E1:E91,"=' + service + '",Controls!J1:J91,"=warning",Controls!K1:K91,"=0") & "/" & COUNTIFS(Controls!E1:E91,"=' + service + '",Controls!J1:J91,"=warning")',
                                     self.cell_format["cell_format_dashboard_warning"])
            self.sheet.write_formula(row + row_index, col + 3,
                                     '=COUNTIFS(Controls!E1:E91,"=' + service + '",Controls!J1:J91,"=low",Controls!K1:K91,"=0") & "/" & COUNTIFS(Controls!E1:E91,"=' + service + '",Controls!J1:J91,"=low")',
                                     self.cell_format["cell_format_dashboard_low"])
            row_index += 1
        return row + row_index

