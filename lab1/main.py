import sys
from parser import *

def main() -> None:
    """запускает программу"""
    filename = sys.argv[1]

    try:
        text = read_file(filename)
        ankety = split(text)
        print("кол-во анкет: ", len(ankety))

        duplicates = find_duplicates(ankety)

        for phone, ankety_with_phone in duplicates.items():
            print(f"дубликаты номера: , {phone}")

            for anketa in ankety_with_phone:
                print(anketa)
    except FileNotFoundError:
        print(f"файл не найден: {filename}")


if __name__ == "__main__":
    main()