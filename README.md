# Синхронный парсер PEP-документации

## **Описание:**

Проект парсинга создан в учебных целях и демонстрирует
возможности сбора информации с web-ресурсов, её обработка и 
вывод (на экран, в файл)

Среди возможностей проекта:
- Формирование списка ссылок на статьи о нововведениях в Python;
- Формирование списка версий Python;
- Скачивание файлов;
- Сбор статусов документации PEP;
- Ведение логов работы парсинга.

### Технологии
Python, BeautifulSoup, HTML

### **Установка:**

1. Клонировать репозиторий и перейти в него в командной строке:

2. Cоздать и активировать виртуальное окружение:

```
python -m venv env

source env/bin/activate
```

3. Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

### **Поддерживаемые комманды парсера:**

1. Для получения справки
```
python main.py pep -h
```
```
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```
2. Список ссылок на статьи Python:
```
python main.py whats-new
```

3. Список версий Python:
```
python main.py latest-versions
```

4. Скачивание архива:
```
python main.py download
```

5. Список количества статусов документов PEP:
```
python main.py pep
```

### Авторы
Максим и команда Практикума
