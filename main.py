import requests
import xlrd
from abc import abstractmethod
import json
from Config import Config

from Config import Config

URL = "http://ws-dss.com/ws_jobs.json"
USER_TOKEN = "R1_bjpEvykBQfeBCyBky"
for

response = requests.post(URL, headers={"user-token": USER_TOKEN})

class RequestKeys:
    FUZZY_SETS = "fuzzy_sets"
    CRITERIONS = "criterions"
    ALTERNATIVES = "alternatives"


class TableProcessor:
    @staticmethod
    def get_header(self, excel_sheet, table_info):
        number_of_columns = excel_sheet.ncolumns
        header_row_index = table_info.header_row
        header = []
        for column in excel_sheet.row(header_row_index):
            header.append(column)
        return header


        self.table_info = table_info

    @staticmethod
    def get_rows(self, excel_sheet, table_info):
        result = []
        curr_index = table_info.start_record
        while curr_index <= table_info.end_record:
            result.append(excel_sheet.row(curr_index))
            ++curr_index
        return  result

    @staticmethod
    def to_dictionary(self, table_info):
        """
        creates dictionary from header as keys and rows as values of these keys
        return: list of dictionaries representing table data (alternatives)
        """

        # with open(table_info.file_path, 'r') as table_file:
        excel_data_file = xlrd.open_workbook(table_info.file_path)
        sheet = excel_data_file.sheet_by_index(table_info.sheet_number)


        header = self.get_header(sheet, table_info)
        rows = self.get_rows(sheet, table_info)

        #TODO: check the structure of alternatives. THe 1st column can be special or not

        result = []
        for row in rows:
            res_row = {}
            for index, column in enumerate(header):
                res_row.update({column: row[index]})
                result.append(res_row)
        return result


class TableInfo:
    def init(self, file_path, sheet_number, header_row_index, quantity_of_records):
        self.file_path = file_path
        self.sheet_number = sheet_number
        self.header_row = header_row_index
        self.start_record = self.header_row + 1
        self.end_record = self.start_record + quantity_of_records - 1


class CriterionProcessor:
    @abstractmethod
    def get_criterion_value(self):
        raise NotImplementedError

class CriterionRequestValueProcessor(CriterionProcessor):
    def init(self, criterion_file_path, table_info):
        """
        criterion is file with rules (beginning of the request json that show Jarik)
        """

        self.criterion_file_path = criterion_file_path
        self.table_info = table_info

    def get_criterion_value(self):

        alternatives = TableProcessor.to_dictionary(self.table_info)
        request_json_dict = {}
        with open(self.criterion_file_path, 'r') as criterion_file:
            request_json_dict = json.load(criterion_file)
        request_json_dict.update({RequestKeys.ALTERNATIVES : alternatives})

        response = requests.post(URL, headers={"user-token": USER_TOKEN}, data= json.dumps(request_json_dict))
        print("jjdjdj")
        #TODO:j
        # READ JSON Criterion from criterion_file_path
        # parse criterion value from request
        raise NotImplementedError


class WeightedCriterionProcessor(CriterionProcessor):
    def init(self, table_info):
        self.table_info = table_info

    def get_criterion_value(self):
        header = TableProcessor.
        raise NotImplementedError

if __name__ == '__main__':
    for table in Config.REQUEST_TABLES:
        CriterionRequestValueProcessor()


    class RequestDataCreator:
        def get_table_json(self):
            for table_file_path, table_info in Config.FILE_PATH_TO_TABLE_INFO
                table = TableProcessor(table_info)
                alternatives = table.to_dictionary






