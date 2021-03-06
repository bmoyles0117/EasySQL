class Select(object):
    JOIN_TYPES  = ['INNER', 'LEFT', 'RIGHT']
    NULL_VALUE  = 'NULL'

    def __init__(self):
        self.reset()

    def __repr__(self):
        """Build out the actual SQL query when this object is represented"""
        return 'SELECT' \
            + self.compile_columns(self.parts['columns']) \
            + self.compile_from(self.parts['from']) \
            + self.compile_joins(self.parts['joins']) \
            + self.compile_where(self.parts['where']) \
            + self.compile_group_by(self.parts['group_by']) \
            + self.compile_order(self.parts['order']) \
            + self.compile_limit(self.parts['limit'])

    def __str__(self):
        return self.__repr__()

    def compile_columns(self, columns):
        """Compiles a list of columns"""
        return ' ' + ', '.join(columns)

    def compile_from(self, from_):    
        """Compiles the FROM statement of the query"""
        return ' FROM ' + self.compile_table_name(from_)

    def compile_group_by(self, group_by = None):
        """Compiles the GROUP BY statement of the query"""
        if not len(group_by or []):
            return ''

        return ' GROUP BY ' + ', '.join(group_by)

    def compile_joins(self, joins):
        """Compiles any joins that exist in the query"""
        query = ''

        for join_table, join_type, join_condition in joins:
            query += ' ' + join_type + ' JOIN ' + self.compile_table_name(join_table) + ' ON ' + join_condition

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
    
    def compile_table_name(self, table_name):    
        table_name = self.format_table_name(table_name)
        
        if table_name[0] != table_name[1]:
            return table_name[1] + ' AS ' + table_name[0]
        else:
            return table_name[0]

    def compile_where(self, where = None):
        """Compiles the WHERE statement of the query

        Keyword Arguments:
        where - An iterable containing [condition, value] elements
        """
        if not len(where or []):
            return ''

        where_parts = []

        for condition, value in where:
            if value is None:
                value = Select.NULL_VALUE
            elif isinstance(value, (str, unicode, )):
                value = '"' + value.replace('"', '\\"') + '"'

            try:
                where_parts.append(condition % (value, ))
            except TypeError:
                where_parts.append(condition)

        return ' WHERE ' + ' AND '.join(where_parts)

    def format_columns(self, table_alias, table_columns):
        """Associate the table name to each column passed in

        Keyword Arguments:
        table_alias - String with the name of the column's parent table alias
        table_columns - An iterable of column names
        """
        return ['%s.%s' % (table_alias, x, ) for x in table_columns]
    
    def format_table_name(self, table_name):
        """Transform string table names into an (alias, name) tuple
        
        Keyword Arguments:
        table_name - String or tuple with the name of the table
        """
        if not isinstance(table_name, (tuple, list, )):
            table_name = (table_name, table_name, )
        
        if len(table_name) != 2:
            raise ValueError('Tuples or lists passed as table names MUST be limited to two items')
        
        return table_name

    def from_(self, table_name, table_columns = None):
        """Build the FROM parts

        Keyword Arguments:
        table_name - String or tuple with the name of the column's parent table
        table_columns - An iterable of column names
        """
        if table_columns is None:
            table_columns = ['*']
        
        table_name = self.format_table_name(table_name)

        self.parts['from'] = table_name
        self.parts['columns'].extend(self.format_columns(table_name[0], table_columns))

        return self

    def group_by(self, group_by):
        """Build the GROUP BY parts

        Keyword Arguments:
        grouping - An iterable of GROUP BY conditions that will be compiled in order
        """
        if not hasattr(group_by, '__iter__'):
            group_by = [group_by]

        self.parts['group_by'] = group_by

        return self

    def join(self, join_table, join_condition, join_columns, join_type):
        """Build the JOIN parts

        Default to whatever the first join type is in the event that
        the specified join type does not exist.

        Keyword Arguments:
        join_table - String or tuple with the name of the table being joined
        join_condition - String containing the operational condition of this join
        join_columns - An iterable of column names
        join_type - A string containing one of Select.JOIN_TYPES
        """
        if join_type not in self.JOIN_TYPES:
            join_type = self.JOIN_TYPES[0]
        
        join_table = self.format_table_name(join_table)

        self.parts['joins'].append([join_table, join_type, join_condition])
        self.parts['columns'].extend(self.format_columns(join_table[0], join_columns))

        return self

    def inner_join(self, join_table, join_condition, join_columns):
        """Proxy to join with INNER as the join_type"""
        return self.join(join_table, join_condition, join_columns, 'INNER')

    def right_join(self, join_table, join_condition, join_columns):
        """Proxy to join with RIGHT as the join_type"""
        return self.join(join_table, join_condition, join_columns, 'RIGHT')

    def left_join(self, join_table, join_condition, join_columns):
        """Proxy to join with LEFT as the join_type"""
        return self.join(join_table, join_condition, join_columns, 'LEFT')

    def limit(self, from_, to = None):
        """Build the LIMIT parts

        Keyword Arguments:
        from_ - An integer containing the starting point or the total records
        to - An integer that states the total records starting at from_
        """
        self.parts['limit'] = [from_, to]

        return self

    def order_by(self, order):
        """Build the ORDER parts

        Keyword Arguments:
        order - An iterable of ORDER BY conditions that will be compiled in order
        """
        if not hasattr(order, '__iter__'):
            order = [order]

        self.parts['order'] = order

        return self

    def reset(self):
        """Reset all of the parts back to their original values"""
        self.parts = {
            'from'      : '',
            'columns'   : [],
            'joins'     : [],
            'limit'     : [],
            'group_by'  : [],
            'order'     : [],
            'where'     : []
        }

    def where(self, condition, value = None):
        """Build a WHERE part

        This method is able to chain with multiple calls to build up various conditionals

        Keyword Arguments:
        condition - A string containing the WHERE condition
        value - A value to be populated via string substitution
        """

        self.parts['where'].append([condition, value])

        return self