
import csv
from pathlib import Path
from collections.abc import Iterator


class FileIterator:
    """Итератор путей к файлам из CSV-аннотации или папки."""

    def __init__(self, source: str | Path) -> None:
        """Загружает пути из CSV-файла или указанной папки."""
        self.source = Path(source)
        self.file_paths: list[Path] = []

        if self.source.is_dir():
            self.file_paths = sorted(
                path.resolve()
                for path in self.source.iterdir()
                if path.is_file()
            )

        elif (
            self.source.is_file()
            and self.source.suffix.lower() == ".csv"
        ):
            with self.source.open(
                "r",
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:
                reader = csv.DictReader(csv_file)

                if (
                    reader.fieldnames is None
                    or "absolute_path" not in reader.fieldnames
                ):
                    raise ValueError(
                        "В CSV отсутствует столбец absolute_path."
                    )

                for row in reader:
                    file_path = row.get("absolute_path")

                    if file_path:
                        self.file_paths.append(Path(file_path))

        else:
            raise FileNotFoundError(
                f"Не найдена папка или CSV-файл: {self.source}"
            )

        self.index = 0

    def __iter__(self) -> "FileIterator":
        """Возвращает сам объект-итератор."""
        return self

    def __next__(self) -> Path:
        """Возвращает следующий путь или завершает перебор."""
        if self.index >= len(self.file_paths):
            raise StopIteration

        file_path = self.file_paths[self.index]
        self.index += 1

        return file_path

    def __len__(self) -> int:
        """Возвращает количество найденных путей."""
        return len(self.file_paths)
