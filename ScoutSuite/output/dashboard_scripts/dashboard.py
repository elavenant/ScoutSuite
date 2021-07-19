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

        self.cell_format_base = workbook.add_format(cell_format_base)
        self.cell_format_header = workbook.add_format(cell_format_header)

        self.cell_format = {
            "cell_format_header": self.cell_format_header,
            "cell_format_base": self.cell_format_base,
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
            row += self._create_block(row, col, {"header": key, "body": data}) + 2

        # Columns can be hidden explicitly. This doesn't increase the file size..
        self.sheet.set_column('H:XFD', None, None, {'hidden': True})

    def _create_block(self, row, col, data):
        self._create_block_header(row, col, data)
        nb_rows = self._create_block_body(row + 1, col, data)

        # Returns the number of rows created
        return nb_rows + 1

    def _create_block_header(self, row, col, data):
        self.sheet.set_row(row, 20)
        self.sheet.merge_range(row, col, row, col + 1, data["header"], self.cell_format["cell_format_header"])
        self.sheet.set_column(col, 400)
        self.sheet.set_column(col + 1, 1000)

    def _create_block_body(self, row, col, data):
        for row_index, key in enumerate(data["body"].keys()):
            self.sheet.write(row+row_index, col, key, self.cell_format["cell_format_base"])
            self.sheet.write(row + row_index, col + 1, data["body"][key], self.cell_format["cell_format_base"])

        return row_index + 1



