import pandas as pd
from pathlib import Path


def load_cocktail_data(file_path: str = "data/cocktails.csv") -> pd.DataFrame:
    """
    Завантажує датасет коктейлів з файлу CSV та виконує очищення даних.

    :param file_path: Шлях до файлу з даними.
    :return: DataFrame з обробленими даними.
    """
    # Завантаження даних
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Файл не знайдено за шляхом: {file_path}")

    df = pd.read_csv(file_path)

    # Перевірка основних колонок
    required_columns = ["name", "ingredients", "category", "glassType", "alcoholic"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"Очікувані колонки: {required_columns}, але отримано: {list(df.columns)}")

    # Очищення та нормалізація інгредієнтів
    df["ingredients"] = df["ingredients"].apply(clean_ingredients)

    # Повертаємо тільки необхідні колонки
    return df[required_columns]


import ast  # Для безпечного перетворення рядків у списки


def clean_ingredients(ingredients: str) -> list:
    """
    Очищає рядок інгредієнтів від зайвих символів і перетворює в список.

    :param ingredients: Рядок із інгредієнтами.
    :return: Список очищених інгредієнтів.
    """
    if not isinstance(ingredients, str):
        return []
    try:
        # Конвертуємо рядок у список
        ingredients_list = ast.literal_eval(ingredients)
        # Приводимо всі елементи до нижнього регістру
        return [ingredient.strip().lower() for ingredient in ingredients_list]
    except (ValueError, SyntaxError):
        # Якщо не вдалося конвертувати, повертаємо порожній список
        return []