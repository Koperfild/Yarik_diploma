import requests
import xlrd
from abc import abstractmethod
import json
from Config import Config
import os
import re

URL = "http://ws-dss.com/ws_jobs.json"
USER_TOKEN = "R1_bjpEvykBQfeBCyBky"

class RequestKeys:
    FUZZY_SETS = "fuzzy_sets"
    CRITERIONS = "criterions"
    ALTERNATIVES = "alternatives"


class TableProcessor:
    @staticmethod
    def get_header(excel_sheet, table_info):
        number_of_columns = excel_sheet.ncols
        header_row_index = table_info.header_row
        header = []
        for column in excel_sheet.row(header_row_index):
            header.append(column.value)
        return header


        self.table_info = table_info

    @staticmethod
    def get_rows(excel_sheet, table_info):
        result = []
        curr_index = table_info.start_record
        while curr_index <= table_info.end_record:
            result.append(excel_sheet.row(curr_index))
            curr_index += 1
        return  result

    @staticmethod
    def to_dictionary(table_info):
        """
        creates dictionary from header as keys and rows as values of these keys
        return: list of dictionaries representing table data (alternatives)
        """

        # with open(table_info.file_path, 'r') as table_file:
        excel_data_file = xlrd.open_workbook(table_info.file_path)
        sheet = excel_data_file.sheet_by_name(table_info.sheet_name)


        header = TableProcessor.get_header(sheet, table_info)
        rows = TableProcessor.get_rows(sheet, table_info)

        #TODO: check the structure of alternatives. THe 1st column can be special or not

        result = []
        for row in rows:
            res_row = (row[0].value, {})
            #begin from 1st member because 0th is description column and not supposed to be sent to the server within alternative
            for index, column in enumerate(header[1:]):
                #correction shift of index
                index += 1
                #adding index of each field and its value with escaped quotes if there are
                res_row[1].update({column: str(row[index].value).replace('"', r'\"')})
            result.append(res_row)
        return result


class CriterionProcessor:
    @abstractmethod
    def get_criterion_value(self):
        raise NotImplementedError

class CriterionRequestValueProcessor(CriterionProcessor):
    def __init__(self, criterion_file_path, table_info):
        """
        criterion is file with rules (beginning of the request json that show Jarik)
        """

        self.criterion_file_path = os.path.join(os.path.dirname(__file__), criterion_file_path).replace('\\','/')
        self.table_info = table_info

    def get_criterion_value(self):

        alternatives = TableProcessor.to_dictionary(self.table_info)
        alternatives = [q[1] for q in alternatives]
        request_json_dict = {}
        with open(self.criterion_file_path, 'r') as criterion_file:
            request_json_dict = json.load(criterion_file)
        request_json_dict.update({RequestKeys.ALTERNATIVES : alternatives})

        #response = requests.post(URL, headers={"user-token": USER_TOKEN}, data= json.dumps(request_json_dict, ))
        response = requests.post(URL, headers={"user-token": USER_TOKEN},
                      data={"ws_job[ws_method_id]": 29, "ws_job[input]": json.dumps(request_json_dict)})
        response = json.loads(response.content)
        print("jjdjdj")
        #TODO:j
        # parse criterion value from request
        raise NotImplementedError


class WeightedCriterionProcessor(CriterionProcessor):
    def __init__(self, table_info):
        self.table_info = table_info

    def get_criterion_value(self):
        # header = TableProcessor.
        raise NotImplementedError

class ProcessedAlternative:
    def __init__(self, alternative, criterion_value):
        self.alternative = alternative
        self.criterion_value = criterion_value

class CriterionWorker:
    def find_max_criterion_value_for_table(self, alternatives_with_criterion):
        """

        :param alternatives_with_criterion: [(alternative, criterion_value),..]
        :return: (alternative, criterion_value) . If there are several maxes take 1st
        """
        return max(alternatives_with_criterion, key=alternatives_with_criterion)
        # for alternative_with_criterion in alternatives_with_criterion:

    def find_max_criterions_sum(self, tables):
        """

        :param tables: {hash_of_table: [(alternative1, criterion_value), (alternative2, criterion_value), ..], }
        :return:
        """
        maxes = []
        for table in tables:
            maxes.append(self.find_max_criterion_value_for_table(table))
        max_criterions_sum = свёртка maxes
        return  max_criterions_sum

    #TODO: Change dict_of_tables to list
    def recursion(self, criterions_sums, chain_of_indices, accumulated_sum, list_of_tables, curr_table_index):
        """
        finds all criterions sums
        :param criterions_sums:
        :param chain_of_indices: list of current indices chain
        :param dict_of_tables:
        :param curr_table_index: {hash_of_table: [(alternative1, criterion_value), (alternative2, criterion_value), ..], }
        :return: [table_hash: index of alternative, ..] for each table
        """
        if curr_table_index >= len(list_of_tables):
            #create copy
            criterions_sums.append((list(chain_of_indices), accumulated_sum))
            # delete this chain_of_indices = []

            accumulated_sum = 0
            curr_table_index = 0
            #TODO: check if it's correct
            return
        curr_table = list_of_tables[curr_table_index]
        for alternative_index, processed_alternative in enumerate(curr_table):
            chain_of_indices.append(alternative_index)
            accumulated_sum += processed_alternative.criterion_value
            self.recursion(criterions_sums, chain_of_indices, accumulated_sum, list_of_tables)
            chain_of_indices.pop()
            accumulated_sum -= processed_alternative.criterion_value

    def get_all_criterions_sums(self, list_of_tables):
        criterions_sums = []
        self.recursion(criterions_sums, [], 0, list_of_tables, 0)
        return criterions_sums

    def get_criterion_sums_lower(self, list_of_tables, output_quantity, percents):
        all_criterion_sums = self.get_all_criterions_sums(list_of_tables)
        #(list_of_indices, sum)
        max_criterion_sum = max(all_criterion_sums,key=lambda x:x[1])

        res = filter(lambda x:x < percents/100 * max_criterion_sum[1], all_criterion_sums)
        res.sort(key= lambda x:x[1])
        return res[:output_quantity]




    def find_nearest_alternatives_to_max_criterions_sum(self, percents_edge, tables):
        """
        Searching nearest to 80% variants of list of alternatives (1 alternative from each table)
        :param percents_edge: 80% or other value
        :param tables:
        :return: [ [(alternative1, criterion_value), (alternative2, criterion_value2),..], several more lists as previous]
        """
        max = self.find_max_criterions_sum(tables)
        for


if __name__ == '__main__':
    criterion_values = []
    for table_and_criterion in Config.REQUEST_TABLES_WITH_CRITERION:
        table_info = table_and_criterion.get("data_table_info")
        criterion_file_path = table_and_criterion.get("criterion_file_path")
        processor = CriterionRequestValueProcessor(criterion_file_path, table_info)
        criterion_values.append(processor.get_criterion_value())
    for table_info in Config.WEIGHTED_SUM_TABLES:
        processor = WeightedCriterionProcessor(table_info)
        criterion_values.append(processor.get_criterion_value())










