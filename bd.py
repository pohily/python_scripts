import sqlite3
from _datetime import datetime
from re import findall


def make_full_lines():
    """ Удаляет лишние переносы строки"""
    with open('../Downloads/bd/spb1.csv', 'r') as file:
        with open('../Downloads/bd/spb.csv', 'a') as rest:
            tmp = ''
            for line in file:
                results = findall(r'000Z,.*$', line)
                if not results:
                    tmp += line.strip()
                else:
                    tmp += line
                    rest.write(tmp)
                    tmp = ''


def moscow():
    # Предварительно удалить все апострофы. Косяки в файле tmp.csv
    with sqlite3.connect(f'spb.db') as connection:
        cursor = connection.cursor()
        cursor.execute("create table data ("
                       "id integer primary key,"
                       "first_name text,"
                       "full_name text,"
                       "email text,"
                       "phone_number text,"
                       "address_city text,"
                       "address_street text,"
                       "address_house text,"
                       "address_entrance text,"
                       "address_floor text,"
                       "address_office text,"
                       "address_comment text,"
                       "location_latitude text,"
                       "location_longitude text,"
                       "amount_charged text,"
                       "user_id text,"
                       "user_agent text,"
                       "created_at text,"
                       "address_doorcode  text);")
        with open('../Downloads/bd/spb.csv', 'r') as file:
            with open('../Downloads/bd/tmp.csv', 'w') as rest:
                for line in file:
                    results = findall(r',"(.+?)",', line.strip())
                    for result in results:
                        tmp = result.replace(',', '')
                        tmp = tmp.replace("'", '')
                        tmp = tmp.replace('"', '')
                        line = line.replace(result, tmp)
                    results = findall(r'000Z,(".+")$', line)
                    for result in results:
                        tmp = result.replace(',', '')
                        tmp = tmp.replace("'", '')
                        tmp = tmp.replace('"', '')
                        line = line.replace(result, tmp)
                    spl = line.split(',')
                    if len(spl) != 19:
                        rest.write(line)
                        continue
                    id, first_name, full_name, email, phone_number, address_city, address_street, address_house, \
                    address_entrance, address_floor, address_office, address_comment, location_latitude, \
                    location_longitude, amount_charged, user_id, user_agent, created_at, address_doorcode = spl
                    id = int(id)
                    query = f"insert into data values ({id},'{first_name}','{full_name}','{email}','{phone_number}'," \
                            f"'{address_city}','{address_street}','{address_house}','{address_entrance}'," \
                            f"'{address_floor}','{address_office}','{address_comment}','{location_latitude}'," \
                            f"'{location_longitude}','{amount_charged}','{user_id}','{user_agent}','{created_at}'," \
                            f"'{address_doorcode}')"
                    try:
                        cursor.execute(query)
                    except:
                        print(line)
        connection.commit()


def join_files():
    from os import listdir
    dirname = '../Downloads/bd/na/'
    files = listdir(dirname)
    with open('../Downloads/bd/phones.csv', 'a') as result:
        for file in files:
            with open(f'../Downloads/bd/na/{file}', 'r') as source:
                for line in source:
                    result.write(line)


def phones():
    # Предварительно удалить все апострофы. Косяки в файле tmp.csv
    with sqlite3.connect(f'phones.db') as connection:
        cursor = connection.cursor()
        cursor.execute("create table data ("
                       "id integer primary key,"
                       "full_name text,"
                       "email text,"
                       "phone_number text);")
        with open('../Downloads/bd/phones.csv', 'r') as file:
            with open('../Downloads/bd/tmp.csv', 'w') as rest:
                for line in file:
                    results = findall(r',\"(.+)\",', line.strip())
                    for result in results:
                        tmp = result.replace(',', '')
                        tmp = tmp.replace("'", '')
                        tmp = tmp.replace('"', '')
                        line = line.replace(result, tmp)
                    spl = line.split(',')
                    if len(spl) != 4:
                        rest.write(line)
                        continue
                    id, full_name, email, phone_number = spl
                    if id == 'id':
                        continue
                    id = int(id)
                    query = f"insert into data values ({id},'{full_name}','{email}','{phone_number.strip()}')"
                    try:
                        cursor.execute(query)
                    except Exception as e:
                        print(e)
                        print(line)
        connection.commit()


if __name__ == '__main__':
    start = datetime.now()
    moscow()
    print(datetime.now() - start)
