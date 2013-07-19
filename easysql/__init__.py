class Select(object):
    JOIN_TYPES  = ['INNER', 'LEFT', 'RIGHT']
    NULL_VALUE  = 'NULL'

    def __init__(self):
        self.reset()

    def __repr__(self):
        return 'SELECT' \
            + self.compile_columns(self.parts['columns']) \
            + self.compile_from(self.parts['from']) \
            + self.compile_joins(self.parts['joins']) \
            + self.compile_where(self.parts['where']) \
            + self.compile_order(self.parts['order']) \
            + self.compile_limit(self.parts['limit'])

    def compile_columns(self, columns):
        """Compiles a list of columns"""
        return ' ' + ', '.join(columns)

    def compile_from(self, from_):
        """Compiles the FROM statement of the query"""
        return ' FROM ' + from_

    def compile_joins(self, joins):
        """Compiles any joins that exist in the query"""
        query = ''

        for join_table, join_type, join_condition in joins:
            query += ' ' + join_type + ' JOIN ' + join_table + ' ON ' + join_condition

        return query

    def compile_limit(self, limit = None):
        """Compiles the LIMIT statement of the query"""
        if not len(limit or []):
            return ''

        if limit[1]:
            return ' LIMIT ' + ', '.join(map(str, limit))

        return ' LIMIT ' + str(limit[0])

    def compile_order(self, order = None):
        """Compiles the ORDER BY statement of the query"""
        if not len(order or []):
            return ''

        return ' ORDER BY ' + ', '.join(order)

    def compile_where(self, where = None):
        """Compiles the WHERE statement of the query

        Arguments:
        where - An iterable containing [condition, value] elements
        """
        if not len(where or []):
            return ''

        where_parts = []

        for condition, value in where:
            if value is None:
                value = Select.NULL_VALUE
            elif isinstance(value, str):
                value = '"' + value.replace('"', '\\"') + '"'

            try:
                where_parts.append(condition % (value, ))
            except TypeError:
                where_parts.append(condition)

        return ' WHERE ' + ' AND '.join(where_parts)

    def format_columns(self, table_name, table_columns):
        """Associate the table name to each column passed in

        Arguments:
        table_name - String with the name of the column's parent table
        table_columns - An iterable of column names
        """
        return ['%s.%s' % (table_name, x, ) for x in table_columns]

    def from_(self, table_name, table_columns = None):
        table_columns = table_columns or ['*']

        self.parts['from'] = table_name
        self.parts['columns'].extend(self.format_columns(table_name, table_columns))

        return self

    def join(self, join_table, join_condition, join_columns, join_type):
        if join_type not in self.JOIN_TYPES:
            join_type = self.JOIN_TYPES[0]

        self.parts['joins'].append([join_table, join_type, join_condition])
        self.parts['columns'].extend(self.format_columns(join_table, join_columns))

        return self

    def inner_join(self, join_table, join_condition, join_columns):
        return self.join(join_table, join_condition, join_columns, 'INNER')

    def right_join(self, join_table, join_condition, join_columns):
        return self.join(join_table, join_condition, join_columns, 'RIGHT')

    def left_join(self, join_table, join_condition, join_columns):
        return self.join(join_table, join_condition, join_columns, 'LEFT')

    def limit(self, from_, to_ = None):
        self.parts['limit'] = [from_, to_]

        return self

    def order_by(self, order):
        if not hasattr(order, '__iter__'):
            order = [order]

        self.parts['order'] = order

        return self

    def reset(self):
        self.parts = {
            'from'      : '',
            'columns'   : [],
            'joins'     : [],
            'limit'     : [],
            'order'     : [],
            'where'     : []
        }

    def where(self, condition, value = None):
        self.parts['where'].append([condition, value])

        return self