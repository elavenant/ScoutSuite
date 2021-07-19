import xlrd
import json
import xlsxwriter
from ScoutSuite.output.dashboard_scripts.dashboard import Dashboard


def create_sheets(json_file, workbook):
    sheets = {}
    
    for sheet_name in json_file["sheet_list"]:
        if sheet_name != "Dashboard":
            sheets[sheet_name] = workbook.add_worksheet(sheet_name)
            ''' Setting headers '''
            sheet_data = json_file["sheet_data"][sheet_name]
            header_format = workbook.add_format(sheet_data["cell_format"]["header_style"])
            for i, header in enumerate(sheet_data["header_list"]):
                sheets[sheet_name].write(0, i, header, header_format)
        
    return sheets


def fit_data_in_sheet(json_file, sheets, sheet_name, workbook):
    sheet = json_file["sheet_data"][sheet_name]
    data_format = {}
    for data_format_key, data_format_value in sheet["cell_format"]["data_style"].items():
        if "default" in sheet["cell_format"]["data_style"].keys():
            default = sheet["cell_format"]["data_style"]["default"]
            data_format_value = {**default, **data_format_value}
        data_format[data_format_key] = workbook.add_format(data_format_value)
    max_width_by_col = [15]*len(sheet["header_list"])
    nb_rows = len(sheet["data"])
    row = 1

    for line in sheet["data"]:

        if "merged_type" in line.keys():
            merge_format = data_format[line["merged_type"]]
            sheets[sheet_name].merge_range(row, 0, row, len(sheet["header_list"])-1, line["text"], merge_format)
            if line["merged_type"] == "merged_h1":
                sheets[sheet_name].set_row(row, 30)
            row += 1
        else:
            for col_name, data in line.items():
                col = sheet["header_list"].index(col_name)

                value = data
                if type(value) == list:
                    value = json.dumps(value)

                ''' Writing the value in the cell '''
                # Handling buttons for macros
                if "button" in col_name:
                    sheets[sheet_name].write(row, col, "", data_format[col_name])
                    if data["enabled"]:
                        sheets[sheet_name].insert_button(row, col, data["command"])
                else:
                    if col_name in data_format.keys():
                        sheets[sheet_name].write(row, col, value, data_format[col_name])
                    elif "default" in data_format.keys():
                        sheets[sheet_name].write(row, col, value, data_format["default"])
                    else:
                        sheets[sheet_name].write(row, col, value)

                ''' Tracking max column width '''
                max_width_by_col[col] = max(max_width_by_col[col], len(str(value)))

            row += 1

    for j in range(0, len(sheet["header_list"])):
        col_name = sheet["header_list"][j]
        
        ''' Adjusting cols width '''
        if "Macro filter button" not in col_name:
            max_width_by_col = [min(x, 100) for x in max_width_by_col]
            sheets[sheet_name].set_column(j, j, max_width_by_col[j])
        else:
            sheets[sheet_name].set_column(j, j, 100)
        
        ''' Setting conditional format '''
        if "conditional_format" in sheet["cell_format"].keys():
            if col_name in sheet["cell_format"]["conditional_format"].keys():
                conditional_format_list = sheet["cell_format"]["conditional_format"][col_name]
                for k, conditional_format in enumerate(conditional_format_list): 
                    conditional_format["format"] = workbook.add_format(conditional_format["format"])
                    
                    # If there is a formula with var to be interpreted
                    if conditional_format["type"] == "formula":
                        try:
                            conditional_format["criteria"] = parse_formula(sheet["header_list"], conditional_format["criteria"])
                        except Exception as e:
                            print("Formula can't be parsed :", e)
                    
                    sheets[sheet_name].conditional_format(1, j, nb_rows, j, conditional_format)

        ''' Setting autofilter ''' 
        sheets[sheet_name].autofilter(0, 0, nb_rows, len(sheet["header_list"])-1)

        ''' Collapsing selected cols '''
        if col_name in sheet["cell_format"]["collapsed"].keys():
            sheets[sheet_name].set_column(j, j, None, None, sheet["cell_format"]["collapsed"][col_name])


def parse_formula(header_list, formula):
    alpha_list = "ABCDEFGHIJKLMNOPQRSTUVWXYZ" 
    start = formula.find("{")
    if start != -1:
        end = formula.find("}")
        var = formula[start+1:end]
        index = header_list.index(var)
        new_formula = formula[0:start] + alpha_list[index] + formula[end+1:]
        return parse_formula(header_list, new_formula)
    else:
        return formula


def to_excel(json_file, save_file):
    workbook = xlsxwriter.Workbook(save_file)
    if "xlsm" in save_file:
        workbook.add_vba_project('ScoutSuite/output/export_scripts/Dashboard_macros.bin')
    
    if "Dashboard" in json_file["sheet_list"]:
        dashboard = Dashboard(workbook, json_file["sheet_data"]["Dashboard"])
        dashboard.create()
   
    sheets = create_sheets(json_file, workbook)
    
    for sheet_name in json_file["sheet_list"]:
        if sheet_name != "Dashboard":
            fit_data_in_sheet(json_file, sheets, sheet_name, workbook)
    
    workbook.close()