from urllib.parse import urljoin
from pathlib import Path
import csv
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sound-effects.ru/"
TIMEOUT = 15

def get_all_download_links(start_url: str) -> list[str]:
    """Собирает уникальные ссылки на звуки с нескольких страниц каталога.
    :param start_url: адрес первой страницы
    :return: список ссылок на скачивание
    """
    all_download_urls = []
    visited_pages = set()
    page_url = start_url
    max_pages = 5

    with requests.Session() as session:
        while page_url and len(visited_pages) < max_pages:
            if page_url in visited_pages:
                break

            visited_pages.add(page_url)
            print(f"страница: {page_url}", flush=True)

            response = session.get(page_url, timeout=(5, 15))
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", class_="downloadlink", href=True):
                download_url = urljoin(page_url, link["href"])

                if download_url not in all_download_urls:
                    all_download_urls.append(download_url)

            next_link = soup.find("a", string=lambda text: text and "Далее" in text)

            if next_link and next_link.get("href"):
                next_page = urljoin(page_url, next_link["href"])
                if next_page in visited_pages:
                    break
                page_url = next_page
            else:
                page_url = ""
    print(f"всего найдено ссылок: {len(all_download_urls)}")
    return all_download_urls

def get_file_size(download_url: str) -> int:
    """
    Получает размер файла в байтах по ссылке.

    :param download_url: адрес скачивания
    :return: размер файла в байтах
    :raises ValueError: если сервер не сообщил размер файла
    """
    response = requests.get(download_url, timeout=TIMEOUT, stream=True)
    try:
        response.raise_for_status()

        content_length = response.headers.get("Content-Length")

        if content_length is None:
            raise ValueError("Сервер не сообщил размер файла")

        return int(content_length)
    finally:
        response.close()

def download_file(download_url: str, file_path: Path) -> int:
    """
    Скачивает звуковой файл и сохраняет его на диск
    :param download_url: ссылка на скачивание
    :param file_path: путь, по которому сохранить файл
    :return: фактический размер скачанного файла в байтах
    """
    response = requests.get(
        download_url,
        timeout=TIMEOUT,
        stream=True,
    )
    try:
        response.raise_for_status()
        file_path.parent.mkdir(parents=True, exist_ok=True)

        total_size = 0

        with file_path.open("wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    total_size += len(chunk)

        return total_size

    except (requests.RequestException, OSError):
        file_path.unlink(missing_ok=True)
        raise
    finally:
        response.close()


def write_annotation(file_paths: list[Path], output_dir: Path, annotation_path: Path) -> None:
    """Записывает абсолютные и относительные пути файлов в CSV.
    :param file_paths: список скачанных файлов
    :param output_dir: папка с загруженными файлами
    :param annotation_path: путь к CSV-аннотации
    """
    annotation_path.parent.mkdir(parents=True, exist_ok=True)
    with annotation_path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=["absolute_path", "relative_path"],
        )
        writer.writeheader()

        for file_path in file_paths:
            writer.writerow({
                "absolute_path": str(file_path.resolve()),
                "relative_path": str(file_path.relative_to(output_dir)),
            })





