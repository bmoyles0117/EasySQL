EasySQL
====

This library's purpose is to remove the need to manually build a SQL query as a string with multiple conditions of potential WHERE, ORDER, LIMIT, or any other kind of statement.

    import easysql, random

    select = easysql.Select().from_('my_table', ['*']).limit(20)

    this_is_awesome = random.randint(0, 10) > 5

    if this_is_awesome:
        select = select.where('my_column = %s', 'awesome')
    else:
        select = select.order_by('my_column DESC')

    print select

We can all hope that 50% of the time we will see something like...

    SELECT my_table.* FROM my_table WHERE my_column = "awesome" LIMIT 20

and that the other 50% of the time we will certainly see

    SELECT my_table.* FROM my_table ORDER BY my_column DESC LIMIT 20
