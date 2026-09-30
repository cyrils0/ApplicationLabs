import re

def read_file(filename: str) -> str:
    """читает файл и возвращает его содержимое"""
    with open(filename, "r", encoding="utf-8") as file:
        return file.read()

def split(text: str) -> list[str]:
    """разделяет содержимое файла на отдельные анкеты"""
    return re.split(r"\n\s*\n", text.strip())

def parse(anketa: str) -> dict[str, str]:
    """разбирает одну анкету на поля"""
    res = {}
    for line in anketa.splitlines():
        if not line.strip():
            continue
        if re.fullmatch(r"\d+\)", line.strip()):
            continue

        key, value = line.split(":", 1)
        res[key.strip()] = value.strip()
    return res

def is_phone(phone: str) -> bool:
    """проверяет, соответствует ли номер допустимому формату."""
    pattern = (
        r"^(8\d{10})$"
        r"|^(8 \(\d{3}\) \d{3}-\d{2}-\d{2})$"
        r"|^(8 \d{3} \d{3}-\d{2}-\d{2})$"
        r"|^(8 \(\d{3}\) \d{3} \d{2} \d{2})$"
        r"|^(8 \d{3} \d{3} \d{2} \d{2})$"
        r"|^(\+7 \d{3} \d{3}-\d{2}-\d{2})$"
        r"|^(\+7 \(\d{3}\) \d{3}-\d{2}-\d{2})$"
        r"|^(\+7 \(\d{3}\) \d{3} \d{2} \d{2})$"
    )

    return bool(re.fullmatch(pattern, phone))

def normalize(phone: str) -> str:
    """убирает из номера все символы, кроме цифр"""
    return re.sub(r"\D", "", phone)

def find_duplicates(ankety: list[str]) -> dict[str, list[str]]:
    """находит анкеты с одинаковыми номерами телефонов"""
    phones = {}

    for anketa in ankety:
        data = parse(anketa)
        phone_or_email = data["Номер телефона или email"]

        if is_phone(phone_or_email):
            phone = normalize(phone_or_email)

            if phone not in phones:
                phones[phone] = []
            phones[phone].append(anketa)
    duplicates = {}
    for phone, anketas_with_phone in phones.items():
        if len(anketas_with_phone) > 1:
            duplicates[phone] = anketas_with_phone
    return duplicates