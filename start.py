from DataBaseConnection import DBconnection
import datetime


def add_meal(dbo, meal_name, meal_type):
    """
    Adds a meal to the meal lookup table
    :param dbo: database connection
    :param meal_name: name of meal to be added
    :param meal_type: lunch / dinner etc
    :return: None
    """
    cur = dbo.conn.cursor()
    cur.execute('''
                    INSERT INTO "FoodApp"."Meals" ("MealName", "MealType")
                    values ('{0}', '{1}')
                '''.format(meal_name, meal_type))
    dbo.conn.commit()
    cur.execute('''
                SELECT COUNT(*) from "FoodApp"."Meals" where "MealType" = '{0}'
                '''.format(meal_type))
    meal_count = cur.fetchone()[0]
    print 'Added {0} ({1})\nThere are now {2} meals in the {1} catagory'.format(meal_name, meal_type, meal_count)
    del cur


def log_meal(dbo, meal_name, meal_type, meal_date):
    cur = dbo.conn.cursor()
    cur.execute('''
                        INSERT INTO "FoodApp"."Meal_Log" ("MealName", "MealType", "DateEaten")
                        values ('{0}', '{1}', '{2}')
                    '''.format(meal_name, meal_type, meal_date))
    dbo.conn.commit()
    print '\nMeal {0} logged for {1}\n'.format(meal_name, meal_date)
    del cur


def get_last_meal(dbo):
    cur = dbo.conn.cursor()
    cur.execute('''
                SELECT "MealName", "DateEaten" from "FoodApp"."Meal_Log" order by "DateEaten" desc limit 1
                ''')
    m, d = cur.fetchone()
    del cur
    return m, d


def get_ideas(dbo, meal_type=None):
    days = 7
    if meal_type:
        add = """ and "MealType" = '{0}'""".format(meal_type.upper())
    else:
        add = ''
    cur = dbo.conn.cursor()
    dte = datetime.datetime.now()
    dte = datetime.date(dte.year, dte.month, dte.day - days)
    cur.execute('''
                SELECT "MealName", min(now()::date - "DateEaten") as days_since_eaten
                from "FoodApp"."Meal_Log"
                where "DateEaten" < '{0}' {1}
                group by "MealName"
                order by min(now()::date - '{0}'::date) desc
                '''.format(dte.strftime('%Y-%m-%d'), add))
    ideas = list()
    for row in cur.fetchall():
        # print row
        ideas.append(row)
    del cur
    return ideas


def get_meals(dbo, meal_type=None):
    if meal_type:
        add = """ where "MealType" = '{0}'""".format(meal_type.upper())
    else:
        add = ''
    meals = set()
    cur = dbo.conn.cursor()
    cur.execute('SELECT DISTINCT "MealName" from "FoodApp"."Meals" {0}'.format(add))
    for i in cur.fetchall():
        # print i[0]
        meals.add(i[0].title())
    del cur
    return meals


def router(dbo, opt):
    if opt == 'Add a meal':
        n = raw_input('\nEnter the name of the meal:\n\t').upper()
        t = raw_input('Enter the type of the meal:\n\t').upper()
        add_meal(dbo, n, t)
    if opt == 'Log a meal':
        n = raw_input('\nEnter the name of the meal:\n\t').upper()
        if n not in get_meals(dbc):
            print 'Meal does not exist, please add it'
            t = raw_input('Enter the type of the meal:\n\t').upper()
            add_meal(dbo, n, t)
        else:
            t = raw_input('Enter the type of the meal:\n\t').upper()
        d = raw_input("Enter the date [YYYY-MM-DD] or type 'today' for today's date\n\t")
        if d.upper() == 'TODAY':
            d = datetime.datetime.now().strftime('%Y-%m-%d')
        log_meal(dbo, n, t, d)
    if opt == 'Get Ideas':
        if raw_input('Narrow by type? (Y/N)\n\t').upper() == 'Y':
            t = raw_input('\nEnter the type of the meal you are looking for:\n\t')
            x = get_ideas(dbo, t)
        else:
            x = get_ideas(dbo)
        for i in x:
            print "you haven't eaten {0} for {1} days".format(i[0].title(), i[1])
        raw_input('\nHit <Enter> when done with list')
    if opt == 'Get all meals':
        if raw_input('Narrow by type? (Y/N)\n\t').upper() == 'Y':
            t = raw_input('\nEnter the type of the meal you are looking for:\n\t')
            m = get_meals(dbo, t)
        else:
            m = get_meals(dbo)
        for i in m:
            print i
        raw_input('\nHit <Enter> when done with list')

def test(dbo):
    add_meal(dbo, 'Tahini Chicken with cucumber noodles', 'Diner')
    add_meal(dbo, 'Hamburgers', 'Diner')
    add_meal(dbo, 'Pesto', 'Diner')
    add_meal(dbo, 'Carnitas', 'Diner')
    add_meal(dbo, 'Carnitas with rice and beans', 'Lunch')

    log_meal(dbo, 'Pesto', 'Diner', datetime.datetime.now().strftime('%Y-%m-%d'))
    log_meal(dbo, 'Hamburgers', 'Diner', '2017-03-11')
    log_meal(dbo, 'Carnitas', 'Diner', '2017-01-11')
    log_meal(dbo, 'Tahini Chicken with cucumber noodles', 'Diner', '2017-03-01')

    print get_last_meal(dbo)
    idea_list = get_ideas(dbo, "Diner", 7)
    for i in idea_list:
        print "you haven't eaten {0} for {1} days".format(i[0], i[1])


if __name__ == '__main__':
    dbc = DBconnection('postgres')
    option = {'0': 'None',
              '1': 'Add a meal',
              '2': 'Log a meal',
              '3': 'Get Ideas',
              '4': 'Get all meals',
              '5': 'Exit'
              }

    choice = '0'
    while option[choice] != 'Exit':
        print '-'*25
        print 'What do you want to do?'
        print '\t1: Add a meal'
        print '\t2: Log a meal'
        print '\t3: Get Ideas'
        print '\t4: Get all meals'
        print '\t5: Exit'
        choice = raw_input('\n\t')
        if choice not in option.keys():
            print '%s not an option, try again' % choice
            choice = '0'
        router(dbc, option[choice])
