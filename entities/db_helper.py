import logging
import copy

class DBHelper(object):

    def __init__(self, context, table_name, structure):
        self.context = context
        self.table_name = table_name
        self.structure = structure

    @staticmethod
    def safe_float(txt):
        try:
            return float(txt)
        except:
            return -1

    @staticmethod
    def safe_int(txt):
        try:
            return int(float(txt))
        except:
            return -1

    def get_empty_row(self):
        return copy.deepcopy(self.structure)

    @staticmethod
    def format_value(value, type):
        if type == 'TEXT' or type == 'BLOB':
            return '"{}"'.format(value)
        else:
            return value

    @staticmethod
    def gen_select(select_struct):
        select_sql = '*'
        for colname, col in select_struct.items():
            if DBHelper.is_entered(col):
                if select_sql == '*':
                    select_sql = '{} '.format(colname)
                else:
                    select_sql = '{}, {}'.format(select_sql, colname)
        return select_sql

    @staticmethod
    def is_entered(col):
        if type(col['value']) == str:
            if len(col['value']) > 0:
                return True
        else:
            if col['value'] > -1:
                return True
        return False

    @staticmethod
    def gen_where(where_struct):
        where_sql = None
        for colname, col in where_struct.items():
            if DBHelper.is_entered(col):
                if where_sql:
                    where_sql = '{} AND {} = {} '.format(where_sql, colname,
                                                         DBHelper.format_value(col['value'], col['type']))
                else:
                    where_sql = '{} = {}'.format(colname, DBHelper.format_value(col['value'], col['type']))
        return where_sql

    @staticmethod
    def gen_set(where_struct):
        set_sql = None
        for colname, col in where_struct.items():
            if DBHelper.is_entered(col):
                if set_sql:
                    set_sql = '{}, {} = {} '.format(set_sql, colname,
                                                         DBHelper.format_value(col['value'], col['type']))
                else:
                    set_sql = '{} = {}'.format(colname, DBHelper.format_value(col['value'], col['type']))
        return set_sql

    @staticmethod
    def gen_col_list(fields):
        col_sql = None
        for colname, col in fields.items():
            if DBHelper.is_entered(col):
                if col_sql:
                    col_sql = '{}, {}'.format(col_sql, colname)
                else:
                    col_sql = '{}'.format(colname)
        return col_sql

    @staticmethod
    def gen_value_list(fields):
        col_sql = None
        for colname, col in fields.items():
            if DBHelper.is_entered(col):
                if col_sql:
                    col_sql = '{}, {}'.format(col_sql, DBHelper.format_value(col['value'], col['type']))
                else:
                    col_sql = '{}'.format(DBHelper.format_value(col['value'], col['type']))
        return col_sql

    def select(self, where_dict, select_dict={}):
        full_sql = 'SELECT {} FROM {} WHERE {};'.format(DBHelper.gen_select(select_dict),
                                                        self.table_name,
                                                        DBHelper.gen_where(where_dict))
        return self.context.query(full_sql)

    def sql(self, sql):
        return self.context.query(sql)

    def update_insert(self, key, update):
        existing = self.context.query('SELECT * FROM {} WHERE {};'.format(self.table_name, DBHelper.gen_where(key)))
        if len(existing) > 0:
            self.update(key, update)
        else:
            if len(key['id']['value']) < 1:
                new_key = None
                for colname, col in key.items():
                    if len(col['value']) > 0:
                        if new_key:
                            new_key = "{}-{}".format(new_key, col['value'])
                        else:
                            new_key = "{}".format(col['value'])
                key['id']['value'] = new_key
            all_fields = copy.deepcopy(key)   # start with x's keys and values
            for colname, col in all_fields.items():
                if len("{}".format(update[colname]['value'])) > 0:
                    all_fields[colname]['value'] = update[colname]['value']
            insert_sql = 'INSERT INTO {}({}) VALUES({});'.format(self.table_name,
                                                                 DBHelper.gen_col_list(all_fields),
                                                                 DBHelper.gen_value_list(all_fields))
            self.context.query(insert_sql)

    def update(self, key, update):
            update_sql = 'UPDATE {} SET {} WHERE {}'.format(self.table_name,
                                                            DBHelper.gen_set(update),
                                                            DBHelper.gen_where(key))
            self.context.query(update_sql)

    def get_by_id(self, id):
        row_match = self.get_empty_row()
        row_match['id']['value'] = id
        results = self.select(row_match)
        if len(results) > 0:
            rv = {}
            cnt = 0
            for colname, col in self.structure.items():
                rv[colname] = results[0][cnt]
                cnt = cnt + 1
            return rv
        else:
            return None

    def get_by_name(self, name):
        row_match = self.get_empty_row()
        row_match['name']['value'] = name
        results = self.select(row_match)

        if len(results) > 0:
            rv = {}
            cnt = 0
            for colname, col in self.structure.items():
                rv[colname] = results[0][cnt]
                cnt = cnt + 1
            return rv
        else:
            return None

    def dict_from_itter(self, itter):
        result = {}
        cnt = 0
        for colname, col in self.structure.items():
            result[colname] = itter[cnt]
            cnt = cnt + 1
        return result


    def get_all(self):
        db_results = self.sql('select * from {};'.format(self.table_name))
        results = []
        for db_result in db_results:
            results.append(self.dict_from_itter(db_result))
        return results
