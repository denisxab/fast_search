import datetime
import sqlite3
import time
from pathlib import Path
from typing import List
from tqdm import tqdm

fileindex_filename: str = "fileindex.sqlite3"


def create_table():
    """
    Создает таблицу `fileindex` в базе данных с полями id, name, path, type, time_create,
    если таблица не существует.
    Создает индекс по полю name.

    :return: None
    """
    with sqlite3.connect(fileindex_filename) as conn:
        # создаем объект-курсор для выполнения запросов
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS fileindex (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL,
                time_create INTEGER NOT NULL
            );
            """
        )
        c.execute("""CREATE INDEX IF NOT EXISTS fileindex_name ON fileindex (name);""")
        # сохраняем изменения
        conn.commit()


def index_files(root_dir: str, index_time: float):
    """
    Индексирует все файлы в указанной директории и записывает информацию о каждом файле в базу данных.

    :param root_dir: Путь к директории.
    :param index_time: Время создания индекса.
    :return: None
    """
    with sqlite3.connect(fileindex_filename) as conn:
        c = conn.cursor()
        file_paths = list(Path(root_dir).rglob("*"))
        for path in tqdm(file_paths, desc="Indexing files", unit="file"):
            try:
                path_abs = path.resolve()
                c.execute(
                    "INSERT OR IGNORE INTO fileindex (name, path, type, time_create) VALUES (?, ?, ?, ?)",
                    (
                        path.name,
                        str(path_abs),
                        "directory" if path.is_dir() else path.suffix.lower(),
                        index_time,
                    ),
                )
            except (PermissionError, FileNotFoundError) as e:
                print(e)

        conn.commit()


def search_files(name_file_or_dir: str, file_type: str = ""):
    """
    Ищет файлы и папки, в имени которых есть строка name_file_or_dir и с заданным типом файла.

    :param name_file_or_dir: Имя файла или папки для поиска.
    :param file_type: Тип файла для поиска.
    :return: Список кортежей с информацией о найденных файлах.
    """
    if not name_file_or_dir and not file_type:
        return []

    with sqlite3.connect(fileindex_filename) as conn:
        # создаем объект-курсор для выполнения запросов
        c = conn.cursor()
        # формируем запрос в зависимости от параметров
        if name_file_or_dir and file_type:
            c.execute(
                "SELECT * FROM fileindex WHERE name LIKE ? AND type = ?",
                ("%" + name_file_or_dir + "%", file_type),
            )
        elif name_file_or_dir:
            c.execute(
                "SELECT * FROM fileindex WHERE name LIKE ?",
                ("%" + name_file_or_dir + "%",),
            )
        else:
            c.execute("SELECT * FROM fileindex WHERE type = ?", (file_type,))

        # получаем результаты запроса
        results = c.fetchall()

    # возвращаем результаты поиска
    return results


def list_index() -> List[str]:
    """
    Выводит список всех индексов.

    :return: Список строк с информацией о всех доступных индексах.
    """
    res_func = [
        "№\tID\t\t|\tДата\t\t\t|\tCount\t|\tPath\t",
        "-\t--\t\t|\t----\t\t\t|\t-----\t|\t----\t",
    ]
    # устанавливаем соединение с базой данных
    with sqlite3.connect(fileindex_filename) as conn:
        # создаем объект-курсор для выполнения запросов
        c = conn.cursor()
        c.execute("SELECT time_create FROM fileindex GROUP BY time_create")
        # получаем результаты запроса
        results = c.fetchall()
        for i, result in enumerate(results):
            ts = result[0]
            dt = datetime.datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M:%S")
            c.execute(
                "SELECT MIN(path), MAX(path), COUNT(1) FROM fileindex WHERE time_create = ?",
                (ts,),
            )
            p1, p2, count = c.fetchone()
            # Общий путь
            commonpath = Path(p1).resolve().parent
            res_func.append(
                "{})\t{}\t|\t{}\t|\t{}\t|\t{}".format(i + 1, ts, dt, count, commonpath)
            )
    return res_func


def delete_old_indexes(days_old):
    """
    Удаляет все индексы, созданные более `days_old` дней назад.
    """
    deleted_rows = 0
    with sqlite3.connect(fileindex_filename) as conn:
        c = conn.cursor()
        # Удаляем записи из таблицы fileindex, удовлетворяющие условию
        c.execute(
            "DELETE FROM fileindex WHERE time_create <= ?",
            (time.time() - days_old * 86400,),
        )
        deleted_rows = c.rowcount
        # Коммитим изменения в базе данных
        conn.commit()
    return deleted_rows
