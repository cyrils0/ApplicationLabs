import argparse
from pathlib import Path
import requests
from parser import (
    BASE_URL,
    download_file,
    get_all_download_links,
    get_file_size,
    write_annotation,
)

def parse_arguments() -> argparse.Namespace:
    """Получает параметры программы из командной строки."""
    argument_parser = argparse.ArgumentParser(
        description="Скачивание звуков с фильтрацией по размеру."
    )

    argument_parser.add_argument(
        "--min-size",
        type=int,
        required=True,
        help="Минимальный размер файла в байтах.",
    )
    argument_parser.add_argument(
        "--max-size",
        type=int,
        required=True,
        help="Максимальный размер файла в байтах.",
    )
    argument_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("downloads"),
        help="Папка для скачанных файлов.",
    )
    argument_parser.add_argument(
        "--annotation",
        type=Path,
        default=Path("annotation.csv"),
        help="Путь к CSV-аннотации.",
    )

    args = argument_parser.parse_args()

    if args.min_size < 0 or args.max_size < 0:
        argument_parser.error(
            "Размеры файлов не могут быть отрицательными."
        )

    if args.min_size > args.max_size:
        argument_parser.error(
            "Минимальный размер не может превышать максимальный."
        )

    return args


def main() -> None:
    """Скачивает звуки подходящего размера и создаёт аннотацию."""
    args = parse_arguments()

    min_size = args.min_size
    max_size = args.max_size
    output_dir = args.output_dir
    annotation_path = args.annotation
    target_count = 30

    downloaded_files: list[Path] = []
    checked_urls: set[str] = set()

    try:
        download_urls = get_all_download_links(BASE_URL)

        for download_url in download_urls:
            if len(downloaded_files) >= target_count:
                break

            if download_url in checked_urls:
                continue

            checked_urls.add(download_url)

            try:
                size = get_file_size(download_url)

                if not min_size <= size <= max_size:
                    continue

                file_path = (
                    output_dir
                    / f"sound_{len(downloaded_files) + 1:03}.mp3"
                )

                actual_size = download_file(download_url, file_path)

                if not min_size <= actual_size <= max_size:
                    file_path.unlink(missing_ok=True)
                    continue

                downloaded_files.append(file_path)

                print(
                    f"Скачан {file_path.name}: "
                    f"{actual_size} байт"
                )

            except (
                requests.RequestException,
                OSError,
                ValueError,
            ) as error:
                print(
                    f"Не удалось обработать {download_url}: {error}"
                )
        write_annotation(downloaded_files, output_dir, annotation_path)
        print(f"Всего скачано файлов: {len(downloaded_files)}")
        print(f"Аннотация сохранена: {annotation_path.resolve()}")
        if len(downloaded_files) < target_count:
            print(
                "Внимание: удалось скачать меньше 30 файлов. "
                "Проверьте дополнительные страницы каталога."
            )
    except requests.RequestException as error:
        print(f"Ошибка при обращении к сайту: {error}")


if __name__ == "__main__":
    main()
