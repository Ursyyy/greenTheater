import xlsxwriter
import mysql.connector
from sqlRequests import fetchTableData

def export(table_name):
    workbook = xlsxwriter.Workbook('./excels/' + table_name + '.xlsx')
    header_cell_format = workbook.add_format({'bold': True, 'border': True})
    body_cell_format = workbook.add_format({'border': True})
    worksheets = ['Reservs', 'Users']
    data = fetchTableData(f"{table_name} 20:00:00")
    for index, item in enumerate(data):
        worksheet = workbook.add_worksheet(worksheets[index])
        header, rows = item

        row_index = 0
        column_index = 0

        for column_name in header:
            worksheet.write(row_index, column_index, column_name, header_cell_format)
            column_index += 1

        row_index += 1
        for row in rows:
            column_index = 0
            for column in row:
                worksheet.write(row_index, column_index, column, body_cell_format)
                column_index += 1
            row_index += 1
    workbook.close()