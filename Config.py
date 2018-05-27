from table_info import TableInfo


class Config:
    REQUEST_TABLES_WITH_CRITERION = [
                                     {"data_table_info": TableInfo(r"Элементы СКС_для_Жени.xlsx", "Сплайс кассеты", 0, 10), "criterion_file_path": r"Criterion for Сплайс кассеты.txt"},
                                     {"data_table_info": TableInfo(r"Элементы СКС_для_Жени.xlsx", "KVM консоли", 0, 1), "criterion_file_path": r"Criterion for KVM консоли.txt"},
                                     {"data_table_info": TableInfo(r"Элементы СКС_для_Жени.xlsx", "Оптические кроссы", 0, 1), "criterion_file_path": r"Criterion for Оптические кроссы.txt"},
                                    ]
    WEIGHTED_SUM_TABLES = [
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "ВОЛС", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Адаптерные панели", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Шнуры ВОЛС", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Коннекторы", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Межсетевые экраны", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "ИБП", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Коммутаторы", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Блок розеток", 0, 10, True),
        TableInfo(r"Элементы СКС_для_Жени.xlsx", "Серверы", 0, 10, True),
        # TableInfo(r"Элементы СКС_для_Жени.xlsx", 12, 0, 10),
    ]