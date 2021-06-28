import xlrd
import json
import xlsxwriter


def json_to_excel(json_file, save_file):
    workbook = xlsxwriter.Workbook(save_file)

    sheets = create_sheets(json_file, workbook)
    for sheet_name in json_file["sheet_list"]:
        fit_data_in_sheet(json_file, sheets, sheet_name)

    workbook.close()


def create_sheets(json_file, workbook):
    sheets = {}

    for sheet_name in json_file["sheet_list"]:
        sheets[sheet_name] = workbook.add_worksheet(sheet_name)
        ''' Setting headers '''
        sheet_data = json_file["sheet_data"][sheet_name]
        for i, header in enumerate(sheet_data["header_list"]):
            sheets[sheet_name].write(0, i, header, sheet_data["header_format"]["style"])

    return sheets


def fit_data_in_sheet(json_file, sheets, sheet_name):
    sheet = json_file["sheet_data"][sheet_name]
    max_width_by_col = [15] * len(sheet["header_list"])
    nb_rows = len(sheet["data"])
    row = 1

    for line in sheet["data"]:
        for data in line:
            col = sheet["header_list"].index(data["col"])
            value = data["value"]

            ''' Writing the value in the cell '''
            sheets[sheet_name].write(row, col, value)

            ''' Tracking max column width '''
            max_width_by_col[col] = max(max_width_by_col[col], len(str(value)))

        row += 1

    for j in range(0, len(sheet["header_list"])):
        ''' Ajusting cols width '''
        sheets[sheet_name].set_column(j, j, max_width_by_col[j])

        ''' Setting autofilter for level field '''
        if sheet["header_format"]["autofilter"]:
            sheets[sheet_name].autofilter(0, j, nb_rows, j)

        ''' Collapsing selected cols '''
        if sheet["header_format"]["collapsed"]:
            sheets[sheet_name].set_column(j, j, None, None, {'level': 1, 'hidden': 1})


