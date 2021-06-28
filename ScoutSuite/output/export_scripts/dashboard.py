import json
import sys
import xlsxwriter

def create_block(row, col, nb_rows, nb_cols, sheet, cell_format):
    
    cell_format_base_italic = cell_format["cell_format_base_italic"]
    cell_format_base = cell_format["cell_format_base"]
    cell_format_top_left = cell_format["cell_format_top_left"]
    cell_format_top_right = cell_format["cell_format_top_right"]
    cell_format_bottom_left = cell_format["cell_format_bottom_left"]
    cell_format_bottom_right = cell_format["cell_format_bottom_right"]
    cell_format_bottom = cell_format["cell_format_bottom"]
    cell_format_top = cell_format["cell_format_top"]
    cell_format_left = cell_format["cell_format_left"]
    cell_format_right = cell_format["cell_format_right"]
    
    for i in range(nb_rows):
        for k in range(nb_cols):
            if i == 0 and k == 0:
                sheet.write(row+i, col+k, "", cell_format_top_left)
            elif i == 0 and k == nb_cols-1:
                sheet.write(row+i, col+k, "", cell_format_top_right)
            elif i == nb_rows-1 and k == 0:
                sheet.write(row+i, col+k, "", cell_format_bottom_left)
            elif i == nb_rows-1 and k == nb_cols-1:
                sheet.write(row+i, col+k, "", cell_format_bottom_right)
            elif i == nb_rows-1 and k != 0 and k != nb_cols-1:
                sheet.write(row+i, col+k, "", cell_format_bottom)
            elif i == 0 and k != 0 and k != nb_cols-1:
                sheet.write(row+i, col+k, "", cell_format_top)
            elif k == 0 and i != 0 and i != nb_rows-1:
                sheet.write(row+i, col+k, "", cell_format_left)
            elif k == nb_cols-1 and i != 0 and i != nb_rows-1:
                sheet.write(row+i, col+k, "", cell_format_right)
            else:
                sheet.write(row+i, col+k, "", cell_format_base)
    sheet.set_column(col+nb_cols-1, col+nb_cols-1, 50)
        
def header(data, nb_cols, sheet, cell_format):
    row = 1
    col = 1
    nb_rows = len(data.keys()) + 2
    create_block(row, col, nb_rows, nb_cols, sheet, cell_format)
    
    x = row+1
    for key, data in data.items():
        key = key + " : "
        text = key + data
        sheet.write(x, col+1, text, cell_format["cell_format_base"])
        x+=1
    return nb_rows + 2    

def body(data, row, nb_cols, sheet, cell_format):
    row_index = 1
    col = 1
    col_index = 0
    
    # Calculating number of rows needed
    nb_rows = 2
    for key in data.keys():
        nb_rows += 2
        nb_rows += len(data[key].keys())*3
    
    create_block(row, col, nb_rows, nb_cols, sheet, cell_format)
    
    col_index += 1
    
    for key in data.keys():
        sheet.write(row + row_index, col + col_index, key, cell_format["cell_format_base"])
        row_index += 2
        col_index += 1
        for sub_key, sub_data in data[key].items():
            sheet.write(row + row_index, col + col_index, sub_data["description"], cell_format["cell_format_base_italic"])
            row_index += 1
            macro = "'goToSheet \""+ sub_data["shortcut"] +"\"'"
            sheet.insert_button(row + row_index, col + col_index, {'macro':   macro,
                               'caption': 'go to '+sub_key+ ' sheet',
                               'width':   200,
                               'height':  30})
            row_index += 2
        col_index -= 1
    return row + row_index 
            
def create_dashboard(data, sheet, workbook):
    
    cell_format_base_italic = {
        'bold': False,
        'italic': True,
        'bg_color': '#D9D9D9',
        'font_color': 'black',
        'left': 0,
        'right': 0,
        'bottom': 0,
        'top': 0
    }
    cell_format_base = {
        'bold': True,
        'bg_color': '#D9D9D9',
        'font_color': 'black',
        'left': 0,
        'right': 0,
        'bottom': 0,
        'top': 0
    }
    cell_format_top = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 0,
            'right': 0,
            'bottom': 0,
            'top': 6
        }
    cell_format_top_left = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 6,
            'right': 0,
            'bottom': 0,
            'top': 6
        }
    cell_format_top_right = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 0,
            'right': 6,
            'bottom': 0,
            'top': 6
        }
    cell_format_bottom = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 0,
            'right': 0,
            'bottom': 6,
            'top': 0
        }
    cell_format_bottom_left = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 6,
            'right': 0,
            'bottom': 6,
            'top': 0
        }
    cell_format_bottom_right = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 0,
            'right':6,
            'bottom': 6,
            'top': 0
        }
    cell_format_right = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 0,
            'right': 6,
            'bottom': 0,
            'top': 0
        }
    cell_format_left = {
            'bold': True,
            'bg_color': '#D9D9D9',
            'font_color': 'black',
            'left': 6,
            'right': 0,
            'bottom': 0,
            'top': 0
        }
    
    cell_format_base_italic = workbook.add_format(cell_format_base_italic)
    cell_format_base = workbook.add_format(cell_format_base)
    cell_format_top = workbook.add_format(cell_format_top)
    cell_format_bottom = workbook.add_format(cell_format_bottom)
    cell_format_top_left = workbook.add_format(cell_format_top_left)
    cell_format_top_right = workbook.add_format(cell_format_top_right)
    cell_format_right = workbook.add_format(cell_format_right)
    cell_format_left = workbook.add_format(cell_format_left)
    cell_format_bottom_left = workbook.add_format(cell_format_bottom_left)
    cell_format_bottom_right = workbook.add_format(cell_format_bottom_right)
    
    cell_format = {
        "cell_format_base_italic": cell_format_base_italic,
        "cell_format_base": cell_format_base,
        "cell_format_top": cell_format_top,
        "cell_format_bottom": cell_format_bottom,
        "cell_format_top_left": cell_format_top_left,
        "cell_format_top_right": cell_format_top_right,
        "cell_format_right": cell_format_right,
        "cell_format_bottom_left": cell_format_bottom_left,
        "cell_format_bottom_right": cell_format_bottom_right,
        "cell_format_left": cell_format_left
    }
    
    data_header = data["data_header"]
    data_body = data["data_body"]
    
    row_index = header(data_header, 5, sheet, cell_format)
    row_index = body(data_body, row_index, 5, sheet, cell_format)
    
    # Hide all rows without data.
    sheet.set_default_row(hide_unused_rows=True)

    # Set the height of empty rows that we do want to display even if it is
    # the default height.
    for row in range(0, row_index+2):
        sheet.set_row(row, 15)

    # Columns can be hidden explicitly. This doesn't increase the file size..
    sheet.set_column('H:XFD', None, None, {'hidden': True})

