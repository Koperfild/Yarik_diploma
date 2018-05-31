import xlsxwriter


class ResultWriter:
    @staticmethod
    def write_to_excel(table_names, result):
        workbook = xlsxwriter.Workbook('Results.xlsx')
        worksheet = workbook.add_worksheet("Results")
        for index, t_name in enumerate(table_names):
            worksheet.write(0, index, t_name)
        worksheet.write(0, len(table_names)+3, "Сумма рангов")
        row_num = 1
        for combination in result:
            for column_index, alternative in enumerate(combination[0]):
                worksheet.write(row_num, column_index, alternative[0])
                worksheet.write(row_num+1, column_index, alternative[1])
            worksheet.write(row_num+1, len(table_names) + 3, combination[1])
            row_num += 3
        workbook.close()