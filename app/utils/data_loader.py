import pandas as pd
from pathlib import Path
import ast

def load_cocktail_data(file_path: str = "data/cocktails.csv") -> pd.DataFrame:

    if not Path(file_path).exists():
        raise FileNotFoundError(f"No matches: {file_path}")

    df = pd.read_csv(file_path)

    required_columns = ["name", "ingredients", "category", "glassType", "alcoholic"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError(f"Required columns: {required_columns}, but got: {list(df.columns)}")

    df["ingredients"] = df["ingredients"].apply(clean_ingredients)

    return df[required_columns]

def clean_ingredients(ingredients: str) -> list:

    if not isinstance(ingredients, str):
        return []
    try:
        ingredients_list = ast.literal_eval(ingredients)
        return [ingredient.strip().lower() for ingredient in ingredients_list]
    except (ValueError, SyntaxError):
        return []
