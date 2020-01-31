## Отправка письма о релизе
Отправка письма о релизе производится командой из коммандной строки, вводя актуальное название релиза:
> **python send_notifications.py ru.5.6.7**

## Создание сборочной задачи
Отправка письма о релизе производится командой из коммандной строки, вводя актуальное название релиза:
> **python build.py ru.5.6.7**

В выбранном релизе создастся сборочная задача, в которую подтянутся все задачи из релиза в статусах выше "Passed QA",
с указанием мердж реквестов из этих задач.

### To Do
В задачу будут добавлены пред- и постдеплойные действия для релиза.
В каждом проекте, входящем в релиз, создастся сборочная верка RC, либо будет указание решить мердж конфликты.


## Установка и настройка

**1** Склонировать репозиторий командой
> **git clone git@gitlab.4slovo.ru:4slovo.ru/python-scripts.git**

**2** Установить pip: 
> **sudo apt install python-pip**

**3** Установить python3-distutils: 
> **sudo apt-get install python3-distutils**

**4** Включить venv в PyCharm:
    
    Запуск проекта в PyCharm командой:

> **File/Open... /python-tests -> tap OK**

    затем выбрать

> **file / settings / project: Python-tests/ Python interpreter / настройки (шестеренка) / Show all / добавить (+) / Virtualenv Environment/ New environment**
                           
   **или** создать новый Virtualenv Environment командой:
                           
> **python3 -m venv env**

> **активировать его можно командой: source venv/bin/activate**

> **деактивировать: deactivate**
                         

**5** Убедиться, что созданный Virtualenv Environment включен: перед приглашением в теминале должно появиться 
    название нашего Virtualenv Environment в скобках:
                           
> **(venv) m.pohilyj@pohilyj-ws:~/python-tests$**

**6** Установить зависимости: 
> **pip install -r requirements.txt**


