
from file_iterator import FileIterator


print("Проверка CSV:")

csv_iterator = FileIterator("annotation.csv")

for file_path in csv_iterator:
    print(file_path)

print(f"Всего файлов в CSV: {len(csv_iterator)}")

print("\nПроверка папки:")

folder_iterator = FileIterator("downloads")

for file_path in folder_iterator:
    print(file_path)

print(f"Всего файлов в папке: {len(folder_iterator)}")
