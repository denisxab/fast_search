import argparse
import time

from .lib_search import delete_old_indexes

from .lib_search import create_table, index_files, list_index, search_files


def main():
    """
    Консольная утилита для поиска и индексации файлов.

    Список подкоманд:

        index (i): Индексация директории. Индексирует указанную директорию и сохраняет информацию о каждом файле в базе данных. Пример использования: python main.py index /home/user/docs
        search (s): Поиск файла в индексе. Осуществляет поиск файла по его имени в базе данных. Можно использовать опциональный аргумент --type для фильтрации по типу файла. Пример использования: python main.py search myfile.txt --type .txt
        list_index (l): Выводит список всех индексов. Отображает информацию о всех доступных индексах. Пример использования: python main.py list_index
        delete (d): Удаляет индексы, созданные более указанного количества дней назад. Можно использовать опциональный аргумент --days для указания количества дней. По умолчанию удаляются индексы, созданные более 10 дней назад. Пример использования: python main.py delete --days 30

    Аргументы:

        directory: Путь к директории, которую нужно проиндексировать. Пример использования: python main.py index /home/user/docs
        query: Имя файла для поиска. Пример использования: python main.py search myfile.txt

    Опциональные аргументы:

        --type: Тип файла для поиска (расширение файла). Пример использования: python main.py search myfile.txt --type .txt
        --days: Количество дней, для которых нужно оставить индексы. По умолчанию 10 дней. Пример использования: python main.py delete --days 30
    """
    # создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(description="File search utility")

    # добавляем подкоманды
    subparsers = parser.add_subparsers(dest="command", help="Sub-command help")

    # команда index
    index_parser = subparsers.add_parser(
        "i", aliases=["index"], help="Index a directory"
    )
    index_parser.add_argument("directory", help="Directory to index")

    # команда search
    search_parser = subparsers.add_parser(
        "s", aliases=["search"], help="Search the index"
    )
    search_parser.add_argument("query", help="Query string")
    search_parser.add_argument(
        "--type", default="", help="File type to filter the search results"
    )
    # команда list_index
    subparsers.add_parser("l", aliases=["list_index"], help="List Index")

    # команда delete
    delete_parser = subparsers.add_parser(
        "d", aliases=["delete"], help="Delete old indexes"
    )
    delete_parser.add_argument(
        "--days", type=int, default=10, help="Number of days to keep the indexes"
    )

    # парсим аргументы командной строки
    args = parser.parse_args()

    # выполняем соответствующую команду
    if args.command in ["i", "index"]:
        create_table()
        index_files(args.directory, index_time=int(time.time()))
        print("Indexing complete!")
        print("\n".join(list_index()))
    elif args.command in ["l", "list_index"]:
        print("\n".join(list_index()))
    elif args.command in ["d", "delete"]:
        days = args.days
        # Сколько записей было удалено
        deleted_rows = delete_old_indexes(days)
        print(f"Old indexes deleted for {days} days. Delete row: {deleted_rows}")
    elif args.command in ["s", "search"]:
        name_file_or_dir: str = args.query
        file_type: str = args.type
        results = search_files(name_file_or_dir, file_type)
        # выводим результаты поиска
        if len(results) > 0:
            print("{:<10}| {:<50}| {:<10}".format("Type", "Name", "Path"))
            print("{:<10}| {:<50}| {:<10}".format("----", "----", "----"))
            for result in results:
                print("{:<10}| {:<50}| {:<10}".format(result[3], result[1], result[2]))
        else:
            print("No results found.")


if __name__ == "__main__":
    main()
