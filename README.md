# fast_search / flsr

`flsr` - Данная программа представляет собой консольную утилиту для индексации и поиска файлов. При индексации указанной директории, информация о каждом файле сохраняется в базе данных. Поиск осуществляется по имени файла в базе данных.

## Зависимости

Для запуска утилиты необходимо наличие интерпретатора Python 3 и установленных библиотек argparse, datetime, sqlite3 и pathlib.

## Использование

### Команды

Утилита поддерживает следующие команды:

- `index (i)` - Индексация директории. Индексирует указанную директорию и сохраняет информацию о каждом файле в базу данных.
- `search (s)` - Поиск файла в индексе по имени. Может использовать необязательный аргумент `--type`, чтобы фильтровать по типу файла.
- `list_index (l)` - Выводит список всех индексов. Отображает информацию о всех доступных индексах.
- `delete (d)` - Удаляет все индексы, созданные более указанного количества дней назад.

### Аргументы

Утилита принимает следующие аргументы:

- `directory` - Путь к директории, которую нужно проиндексировать. Пример использования: `python search.py index /home/user/docs`
- `query` - Имя файла для поиска. Пример использования: `python search.py search myfile.txt`
- `days` - Количество дней, после которых необходимо удалить индексы. Пример использования: `python search.py delete 30`

## Функции

### create_table()

Функция создает таблицу `fileindex` в базе данных `fileindex.sqlite3` с полями `id, name, path, type, time_create`. Поле `id` является первичным ключом и генерируется автоматически. Поле name хранит имя файла, `path` - полный путь к файлу, `type` - тип файла (расширение), `time_create` - время создания файла в формате `timestamp`.

### index_files(root_dir: str, time_created: int)

Функция производит индексацию директории root_dir. Для каждого файла в директории и ее поддиректориях создается запись в таблице `fileindex`. Запись содержит информацию о имени файла, его пути, типе и времени создания (time_create). Время создания устанавливается переданным параметром `time_created`.

### search_files(name_file_or_dir: str)

Функция осуществляет поиск файла в базе данных по его имени name_file_or_dir. Поиск производится с помощью оператора `LIKE`, что позволяет искать файлы и папки, в имени которых есть заданная строка. Функция возвращает список записей из таблицы `fileindex`, соответствующих запросу поиска. Каждая запись представляет собой кортеж из пяти элементов: `id, name, path, type и time_creat`e.

### list_index()

Функция выводит список всех индексов, содержащихся в базе данных `fileindex.sqlite3`. Для каждого индекса выводится номер, дата создания, количество файлов и общий путь. Для вывода используется таблица в формате markdown.

### delete_old_indexes(days: int) -> int

Функция удаляет все индексы, созданные более `days` дней назад из базы данных `fileindex.sqlite3`. Она принимает на вход параметр `days` - количество дней, после которых необходимо удалить индексы. Функция возвращает количество удаленных записей.

### main()

Основная функция, которая выполняет соответствующую команду в зависимости от переданных аргументов командной строки. Функция парсит аргументы командной строки с помощью модуля `argparse`, и выполняет соответствующую команду (index, search, list_index) с помощью функций create_table(), index_files(), search_files() и list_index(). Вывод результатов осуществляется на консоль.

## Примеры использования

### Индексация директории

Для индексации директории необходимо выполнить команду `index (i)` и указать путь к директории, которую нужно проиндексировать:

```bash
python search.py index /home/user/docs
```

### Поиск файла

Для поиска файла в индексе необходимо выполнить команду `search (s)` и указать имя файла для поиска:

```bash
python search.py search myfile.txt
```

Также возможно выполнить поиск файлов по типу с помощью аргумента `--type` (расширения файла). Например, чтобы найти все файлы с расширением `.pdf`, нужно выполнить следующую команду:

```bash
python search.py search myfile.txt --type '.pdf;
```

Аргумент `--type` является необязательным. Если он не указан, то поиск будет осуществляться по всем файлам.

### Вывод списка индексов

Для вывода списка всех индексов необходимо выполнить команду `list_index (l)`:

```bash
python search.py list_index
```

### Удаление старых индексов

В данном примере будут удалены все индексы, созданные более 30 дней назад:

```bash
python search.py delete --days 30
```

## Заключение

Данный код представляет собой пример консольной утилиты для индексации и поиска файлов. Он может быть использован как основа для создания более сложных инструментов для работы с файловой системой.