from easysql import Select

import unittest

class SelectTestCase(unittest.TestCase):
    def setUp(self):
        self.select = Select().from_('table_name')

class CompileTestCase(SelectTestCase):
    def test_compile_columns(self):
        self.assertEquals(self.select.compile_columns(['*']), ' *')
        self.assertEquals(self.select.compile_columns(['column1']), ' column1')
        self.assertEquals(self.select.compile_columns(['column1', 'column2']), ' column1, column2')

    def test_compile_from(self):
        self.assertEquals(self.select.compile_from('table_name'), ' FROM table_name')

    def test_compile_joins(self):
        self.assertEquals(self.select.compile_joins([['table_name', 'INNER', '1 = 1']]), ' INNER JOIN table_name ON 1 = 1')

    def test_compile_limit(self):
        self.assertEquals(self.select.compile_limit(), '')
        self.assertEquals(self.select.compile_limit([10, None]), ' LIMIT 10')
        self.assertEquals(self.select.compile_limit([20, 10]), ' LIMIT 20, 10')

    def test_compile_order(self):
        self.assertEquals(self.select.compile_order(), '')
        self.assertEquals(self.select.compile_order(['test ASC']), ' ORDER BY test ASC')
        self.assertEquals(self.select.compile_order(['test ASC', 'test2 DESC']), ' ORDER BY test ASC, test2 DESC')

    def test_compile_where(self):
        self.assertEquals(self.select.compile_where(), '')
        self.assertEquals(self.select.compile_where([['column1 IS NULL', None]]), ' WHERE column1 IS NULL')
        self.assertEquals(self.select.compile_where([['column1 = %s', 123]]), ' WHERE column1 = 123')
        self.assertEquals(self.select.compile_where([['column1 = %s', '123']]), ' WHERE column1 = "123"')
        self.assertEquals(self.select.compile_where([['column1 = %s', 123], ['column2 = %s', '456']]), ' WHERE column1 = 123 AND column2 = "456"')

class WhereTestCase(SelectTestCase):
    def test_multi_where(self):
        self.select.where('test = %s', '1234')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name WHERE test = "1234"')

        self.select.where('test2 = %s', '123')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name WHERE test = "1234" AND test2 = "123"')

    def test_null_where(self):
        self.select.where('test IS NULL')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name WHERE test IS NULL')

    def test_where(self):
        self.select.where('test = %s', '123')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name WHERE test = "123"')

    def test_where_like(self):
        self.select.where('test LIKE %s', '123%')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name WHERE test LIKE "123%"')

    def test_where_unicode(self):
        self.select.where('test = %s', u'123')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name WHERE test = "123"')


class LimitTestCase(SelectTestCase):
    def test_single_limit(self):
        self.select.limit(10)

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name LIMIT 10')

    def test_paging_limit(self):
        self.select.limit(20, 10)

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name LIMIT 20, 10')

class JoinTestCase(SelectTestCase):
    def setUp(self):
        self.base_matching_query = 'SELECT table_name.* FROM table_name %s JOIN joined_table ON joined_table.id = table_name.id'

        super(JoinTestCase, self).setUp()

    def test_inner_join_columns(self):
        self.select.inner_join('joined_table', 'joined_table.id = table_name.id', ['sample_column'])

        self.assertEquals(str(self.select), 'SELECT table_name.*, joined_table.sample_column FROM table_name INNER JOIN joined_table ON joined_table.id = table_name.id')

    def test_inner_join(self):
        self.select.inner_join('joined_table', 'joined_table.id = table_name.id', [])

        self.assertEquals(str(self.select), self.base_matching_query % 'INNER')

    def test_right_join(self):
        self.select.right_join('joined_table', 'joined_table.id = table_name.id', [])

        self.assertEquals(str(self.select), self.base_matching_query % 'RIGHT')

    def test_left_join(self):
        self.select.left_join('joined_table', 'joined_table.id = table_name.id', [])

        self.assertEquals(str(self.select), self.base_matching_query % 'LEFT')

    def test_unknown_join(self):
        self.select.join('joined_table', 'joined_table.id = table_name.id', [], 'UNKNOWN')

        self.assertEquals(str(self.select), self.base_matching_query % 'INNER')
        
class GroupByTestCase(SelectTestCase):
    def test_order_by_string(self):
        self.select.group_by('field_name')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name GROUP BY field_name')

    def test_order_by_single_item(self):
        self.select.group_by(['field_name'])

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name GROUP BY field_name')

    def test_order_by_multi_item(self):
        self.select.group_by(['field_name', 'other_field'])

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name GROUP BY field_name, other_field')

class OrderByTestCase(SelectTestCase):
    def test_order_by_string(self):
        self.select.order_by('sort_order ASC')

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name ORDER BY sort_order ASC')

    def test_order_by_single_item(self):
        self.select.order_by(['sort_order ASC'])

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name ORDER BY sort_order ASC')

    def test_order_by_multi_item(self):
        self.select.order_by(['sort_order ASC', 'column_name DESC'])

        self.assertEquals(str(self.select), 'SELECT table_name.* FROM table_name ORDER BY sort_order ASC, column_name DESC')

if __name__ == '__main__':
    unittest.main()