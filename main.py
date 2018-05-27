#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import requests
import xlrd
from abc import abstractmethod
import json
from Config import Config
import os
from functools import reduce
from table_info import TableInfo

URL = "http://ws-dss.com/ws_jobs/3522.json"
USER_TOKEN = "R1_bjpEvykBQfeBCyBky"

class RequestKeys:
    FUZZY_SETS = "fuzzy_sets"
    CRITERIONS = "criterions"
    ALTERNATIVES = "alternatives"


class IncorrectTableInputError(Exception):
    pass


class Optimization:
    OPTIMIZATION_DIRECTION = 'optimization_direction'
    COLUMN_WEIGHT = 'column_weight'
    MAX = 'max'
    MIN = 'min'


class TableProcessor:
    table_info_to_sheet = {}

    @staticmethod
    def _get_excel_sheet(table_info):
        sheet = TableProcessor.table_info_to_sheet.get(table_info)
        if sheet is None:
            excel_data_file = xlrd.open_workbook(table_info.file_path)#DELETE: , formatting_info=True)
            sheet = excel_data_file.sheet_by_name(table_info.sheet_name)
            if sheet.ragged_rows:
                raise IncorrectTableInputError("Ragged table in sheet {} in file {}".format(table_info.sheet_name, table_info.file_path))
            TableProcessor.table_info_to_sheet.update({table_info: sheet})
        return sheet

    @staticmethod
    def get_header(table_info):
        excel_sheet = TableProcessor._get_excel_sheet(table_info)
        number_of_columns = excel_sheet.ncols
        header_row_index = table_info.header_row
        header = []
        for column in excel_sheet.row(header_row_index):
            header.append(column.value)
        return header

    @staticmethod
    def get_optimization_info(table_info):
        """

        :param table_info:
        :return: { column : optimization_direction }
        """
        header = TableProcessor.get_header(table_info)
        header = header[1:]
        if not table_info.weighted_table:
            raise IncorrectTableInputError("Table {} is not supposed for weighted sum criterion".format(table_info.sheet_name))
        sheet = TableProcessor._get_excel_sheet(table_info)
        rows_quantity = sheet.nrows
        optimization_row_index = rows_quantity - 4
        column_weight_index = rows_quantity - 3
        max_row_index = rows_quantity -2
        min_row_index = rows_quantity -1
        optimization_info_rows = TableProcessor._get_rows_by_indices(table_info, optimization_row_index, column_weight_index, max_row_index, min_row_index)
        optimization_row = optimization_info_rows[0][1:]
        weights_row = optimization_info_rows[1][1:]
        max_row = optimization_info_rows[2][1:]
        min_row = optimization_info_rows[3][1:]
        # Do not take 1st cell as it contains name of alternative, not value
        res = {}
        for index, column in enumerate(header):
            res[column] = {Optimization.OPTIMIZATION_DIRECTION: optimization_row[index].value, Optimization.COLUMN_WEIGHT: weights_row[index].value, Optimization.MAX: max_row[index].value, Optimization.MIN: min_row[index].value}
        return res

    @staticmethod
    def _get_rows_by_indices(table_info, *indices):
        excel_sheet = TableProcessor._get_excel_sheet(table_info)
        res = []
        for index in indices:
            res.append(excel_sheet.row(index))
        return res

    @staticmethod
    def get_all_data_rows(table_info):
        excel_sheet = TableProcessor._get_excel_sheet(table_info)
        result = []
        curr_index = table_info.start_record
        data_records_end_index = excel_sheet.nrows
        if table_info.weighted_table:
            data_records_end_index = excel_sheet.nrows - TableInfo.ROWS_FOR_WEIGHT_PART
        while curr_index < data_records_end_index:
            result.append(excel_sheet.row(curr_index))
            curr_index += 1
        return  result

    @staticmethod
    def to_dictionary(table_info):
        """
        creates dictionary from header as keys and rows as values of these keys
        return: list of tuples, in tuple: 1st is 0th value in excel row, i.e. Name,  characteristics as { char_name: value,..}
        """
        header = TableProcessor.get_header(table_info)
        rows = TableProcessor.get_all_data_rows(table_info)
        #DELETE: this is only for test
        #rows = rows[:1]
        result = []
        for row in rows:
            res_row = {row[0].value: {}}
            #begin from 1st member because 0th is description column and not supposed to be sent to the server within alternative
            for index, column in enumerate(header[1:]):
                #correction shift of index
                index += 1
                res_row[row[0].value].update({column: row[index].value})
            result.append(res_row)
        return result


class CriterionProcessor:
    @abstractmethod
    def get_criterion_values(self):
        """
        :return: { alternative_name: criterion_value }
        """
        raise NotImplementedError

class CriterionRequestValueProcessor(CriterionProcessor):
    def __init__(self, criterion_file_path, table_info):
        """
        criterion is file with rules (beginning of the request json that show Jarik)
        """
        self.criterion_file_path = os.path.join(os.path.dirname(__file__), criterion_file_path).replace('\\','/')
        self.table_info = table_info

    def get_criterion_values(self):
        alternatives = TableProcessor.to_dictionary(self.table_info)
        #extract dictionary of values of alternatives
        alternatives_keys = [list(q.keys())[0] for q in alternatives]# list(alternatives[0].keys())[0]
        alternatives_values = [list(q.values())[0] for q in alternatives]
        request_json_dict = {}
        with open(self.criterion_file_path, 'r', encoding="utf8") as criterion_file:
            request_json_dict = json.load(criterion_file)
        request_json_dict.update({RequestKeys.ALTERNATIVES : alternatives_values})

        #response = requests.post(URL, headers={"user-token": USER_TOKEN}, data= json.dumps(request_json_dict, ))
        response = requests.put(URL, headers={"user-token": USER_TOKEN},
                      data={"ws_job[ws_method_id]": 29, "ws_job[input]": json.dumps(request_json_dict)})
        response = json.loads(response.content)
        criterion_values = [alternative_reply['generalized criterion'] for alternative_reply in json.loads(response['output'])]
        return dict(zip(alternatives_keys, criterion_values))


class WeightedCriterionProcessor(CriterionProcessor):
    def __init__(self, table_info):
        self.table_info = table_info

    def get_criterion_values(self):
        res = {}
        alternatives = TableProcessor.to_dictionary(self.table_info)
        optimization_info = TableProcessor.get_optimization_info(table_info)
        for alternative in alternatives:

            #dict
            alternative_properties = list(alternative.values())[0]# alternatives[alternative]
            #Delete:j optimization_info = TableProcessor.get_optimization_info(table_info)
            criterion_value = 0
            for property_name in alternative_properties:


                property_value = alternative_properties[property_name]

                optimization_direction = optimization_info[property_name][Optimization.OPTIMIZATION_DIRECTION]
                weight = optimization_info[property_name][Optimization.COLUMN_WEIGHT]
                max = optimization_info[property_name][Optimization.MAX]
                min = optimization_info[property_name][Optimization.MIN]
                func = self._max_criterion_func if optimization_direction == Optimization.MAX else self._min_citerion_func
                criterion_value += func(property_value, max, min) * weight
            res.update({list(alternative.keys())[0]:criterion_value})
        return res

    def _max_criterion_func(self, value, max, min):
        return (max-value)/(max-min)

    def _min_citerion_func(self, value, max, min):
        return (value-min)/(max-min)


class ProcessedAlternative:
    def __init__(self, alternative, criterion_value):
        self.alternative = alternative
        self.criterion_value = criterion_value

class CriterionWorker:

    def extract_dict_value(self, dict):
        for key, val in enumerate(dict):
            return val

    def find_max_criterion_value_for_table(self, alternatives_with_criterions):
        """

        :param alternatives_with_criterions: [(alternative, criterion_value),..]
        :return: (alternative, criterion_value) . If there are several maxes take 1st
        """
        return alternatives_with_criterions[max(alternatives_with_criterions, key=lambda x: alternatives_with_criterions[x])]

    def find_max_criterions_sum(self, tables):
        """

        :param tables: {hash_of_table: [(alternative1, criterion_value), (alternative2, criterion_value), ..], }
        :return:
        """
        maxes = []
        for table in tables:
            maxes.append(self.find_max_criterion_value_for_table(table))
        max_criterions_sum = reduce((lambda x,y:x+y), maxes)
        return  max_criterions_sum

    def _move_windows(self, windows_movable, list_of_tables, windows_starts, windows_ends, window_size=3):
        for table_index, table in enumerate(list_of_tables):
            table_length = len(table)
            if windows_starts[table_index] + window_size < table_length:
                windows_ends[table_index] += 1
                windows_starts[table_index] += 1
            else:
                windows_movable[table_index] = False

    def _make_combinations(self, criterions_sums, windows_starts, windows_ends, chain_of_alternatives, accumulated_sum, list_of_sorted_tables, curr_table_index):
        """

        :param windows_starts:
        :param windows_ends:
        :param criterions_sums:
        :param chain_of_alternatives:
        :param accumulated_sum:
        :param list_of_sorted_tables: [ [(alternative_key, criterion_value)],[..  ] ]
        :param curr_table_index:
        :return:
        """
        if curr_table_index >= len(list_of_sorted_tables):
            #create copy
            criterions_sums.append((list(chain_of_alternatives), accumulated_sum))
            return
        curr_table = list_of_sorted_tables[curr_table_index]
        start_index = windows_starts[curr_table_index]
        curr_alternative_index = start_index
        end_index = windows_ends[curr_table_index]
        while curr_alternative_index <= end_index:
            chain_of_alternatives.append(curr_table[curr_alternative_index])
            #adding criterion value of curr alternative
            alternative_criterion_value = curr_table[curr_alternative_index][1]
            accumulated_sum += alternative_criterion_value
            self._make_combinations(criterions_sums, windows_starts, windows_ends, chain_of_alternatives, accumulated_sum, list_of_sorted_tables, curr_table_index + 1)
            chain_of_alternatives.pop()
            accumulated_sum -= alternative_criterion_value
            curr_alternative_index += 1

    def make_combinations(self, list_of_sorted_tables, windows_starts, windows_ends):
        """
        Creates all possible combinations and calculates criterion values
        :param list_of_sorted_tables:
        :param windows_starts:
        :param windows_ends:
        :return:
        """
        criterions_sums = []
        self._make_combinations(criterions_sums, windows_starts, windows_ends, [], 0, list_of_sorted_tables, 0)
        return criterions_sums

    def get_nearest_sums(self, list_of_tables, percents, required_output_quantity=3, window_size=3):
###################WORKING ON!!!!!!!!!############################
        windows_starts = [0]*len(list_of_tables)
        windows_ends = [len(table)-1 if len(table) < window_size else window_size - 1 for table in list_of_tables]
        windows_movable = [True]*len(list_of_tables)
        #sort all tables by criterion values
        sorted_tables_by_criterion_values = []
        for table in list_of_tables:
            sorted_tables_by_criterion_values.append(sorted(table.items(), key=lambda x: x[1], reverse=True))
        #max_criterions_sum = self.find_max_criterions_sum(list_of_tables)
        max_criterions_sum = reduce(lambda x,y: x+y, [table[0][1] for table in sorted_tables_by_criterion_values])
        criterions_sums = []
        #while at least any window is movable and not all criterions_sums found
        while reduce(lambda x,y:x or y, windows_movable) and len(criterions_sums) < required_output_quantity:
            #all combinations within windows
            curr_criterions_sums = self.make_combinations(sorted_tables_by_criterion_values, windows_starts, windows_ends)
            curr_criterions_sums = list(filter(lambda x: x[1]<= percents/100 * max_criterions_sum, curr_criterions_sums))
            #sort decreasingly
            curr_criterions_sums.sort(key=lambda x: x[1], reverse=True)
            criterions_sums.extend(curr_criterions_sums)
            self._move_windows(windows_movable, list_of_tables, windows_starts, windows_ends, window_size)
        return criterions_sums[:required_output_quantity]

    def get_criterion_sums_lower_last(self, list_of_tables, output_quantity, percents):
        """
        Searching nearest to 80% variants of list of alternatives (1 alternative from each table)
        :param percents_edge: 80% or other value
        :param tables:
        :return: [ [(alternative1, criterion_value), (alternative2, criterion_value2),..], several more lists as previous]
        """
        res = self.get_nearest_sums(list_of_tables,percents, output_quantity)
        return res

###################WORKING ON!!!!!!!!!############################
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

            # accumulated_sum = 0
            # curr_table_index = 0
            #TODO: check if it's correct
            return
        curr_table = list_of_tables[curr_table_index]
        for alternative_index, processed_alternative_key in enumerate(curr_table):
            chain_of_indices.append(alternative_index)
            #adding criterion value of curr alternative
            alternative_criterion_value = curr_table[processed_alternative_key]
            accumulated_sum += alternative_criterion_value
            self.recursion(criterions_sums, chain_of_indices, accumulated_sum, list_of_tables, curr_table_index + 1)
            chain_of_indices.pop()
            accumulated_sum -= alternative_criterion_value

    def get_all_criterions_sums(self, list_of_tables):
        criterions_sums = []
        self.recursion(criterions_sums, [], 0, list_of_tables, 0)
        return criterions_sums

    def get_criterion_sums_lower(self, list_of_tables, output_quantity, percents):
        """
        Searching nearest to 80% variants of list of alternatives (1 alternative from each table)
        :param percents_edge: 80% or other value
        :param tables:
        :return: [ [(alternative1, criterion_value), (alternative2, criterion_value2),..], several more lists as previous]
        """
        all_criterion_sums = self.get_all_criterions_sums(list_of_tables)
        #(list_of_indices, sum)
        max_criterion_sum = max(all_criterion_sums,key=lambda x:x[1])

        res = filter(lambda x:x < percents/100 * max_criterion_sum[1], all_criterion_sums)
        res.sort(key= lambda x:x[1])
        return res[:output_quantity]


if __name__ == '__main__':
    criterion_values = []

    for table_info in Config.WEIGHTED_SUM_TABLES:
        processor = WeightedCriterionProcessor(table_info)
        criterion_values.append(processor.get_criterion_values())

    for table_and_criterion in Config.REQUEST_TABLES_WITH_CRITERION:
        table_info = table_and_criterion.get("data_table_info")
        criterion_file_path = table_and_criterion.get("criterion_file_path")
        processor = CriterionRequestValueProcessor(criterion_file_path, table_info)
        criterion_values.append(processor.get_criterion_values())



    # CriterionWorker().find_max_criterions_sum()
    # CriterionWorker().get_criterion_sums_lower()
    result = CriterionWorker().get_criterion_sums_lower_last(criterion_values, 3, 80)
    # CriterionWorker().get_all_criterions_sums(criterion_values)
    # max_sum = CriterionWorker().find_max_criterions_sum(criterion_values)
    print("The End.")










