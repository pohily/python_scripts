import sqlite3
from _datetime import datetime


def main():
    """
    Создание БД для поиска недействительных папортов с
    http://xn--b1afk4ade4e.xn--b1ab2a0a.xn--b1aew.xn--p1ai/info-service.htm?sid=2000
    Размер файла слишком большой - Libre Office не открывает
    grep 6722,067081 ../list_of_expired_passports.csv
    """
    with sqlite3.connect(f'inactive_passports_{datetime.now().strftime("%Y.%m.%d")}.db') as connection:
        cursor = connection.cursor()
        cursor.execute("create table data (_id integer primary key autoincrement, number text not null);")
        with open('../Downloads/list_of_expired_passports.csv', 'r') as file:
            index = 1
            for line in file:
                number = line.strip().replace(',', ' ')
                query = f"insert into data values ({index}, '{number}')"
                index += 1
                cursor.execute(query)
        connection.commit()


if __name__ == '__main__':
    start = datetime.now()
    main()
    print(datetime.now() - start)
