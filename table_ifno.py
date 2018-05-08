class TableInfo:
    def __init__(self, file_path, sheet_name, header_row_index, quantity_of_records):
        self.file_path = file_path
        self.sheet_name = sheet_name
        self.header_row = header_row_index
        self.start_record = self.header_row + 1
        self.end_record = self.start_record + quantity_of_records - 1