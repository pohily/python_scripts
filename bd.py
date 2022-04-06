import sqlite3
from _datetime import datetime
from re import findall


def make_full_lines():
    with open('../Downloads/msc.csv', 'r') as file:
        with open('../Downloads/tmp.csv', 'a') as rest:
            tmp = ''
            for line in file:
                results = findall(r'000Z,.*$', line)
                if not results:
                    tmp += line.strip()
                else:
                    tmp += line
                    rest.write(tmp)
                    tmp = ''


def main():
    # Предварительно удалить все апострофы. Косяки в файле tmp.csv
    with sqlite3.connect(f'moscow.db') as connection:
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
        with open('../Downloads/msc.csv', 'r') as file:
            with open('../Downloads/tmp.csv', 'w') as rest:
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


if __name__ == '__main__':
    start = datetime.now()
    main()
    print(datetime.now() - start)
