import json
import pandas as pd

DB_PATH = "./db-food.json"


class DogFood:
    def __init__(
        self,
        _id,
        name,
        brand,
        condition,
        packageWeight_lb,
        packageWeight_kg,
        price,
        calories,
        breed,
        animalSize,
        lifeStage,
        picture,
    ):
        self._id = _id
        self.name = name
        self.brand = brand
        self.condition = condition
        self.packageWeight_lb = packageWeight_lb
        self.packageWeight_kg = packageWeight_kg
        self.price = price
        self.calories = calories
        self.breed = breed
        self.animalSize = animalSize
        self.lifeStage = lifeStage
        self.picture = picture

    def to_dict(self):
        return {
            "id": self._id,
            "name": self.name,
            "brand": self.brand,
            "condition": self.condition,
            "packageWeight_lb": self.packageWeight_lb,
            "packageWeight_kg": self.packageWeight_kg,
            "price": self.price,
            "calories": self.calories,
            "breed": self.breed,
            "animalSize": self.animalSize,
            "lifeStage": self.lifeStage,
            "picture": self.picture,
        }


def load_data(file_name):
    file_path = f"./{file_name}"
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def check_if_breed_exists(breed):
    dog_food_data = load_data(DB_PATH)
    df = pd.DataFrame(dog_food_data)
    breeds_list = df["breed"].unique()
    if breed not in breeds_list:
        return False
    return True


def get_food_recommendations(breed, size, life_stage, health_conditions):
    data = load_data(DB_PATH)
    foods_list = [DogFood(**item) for item in data]

    recommended_foods = []

    for food in foods_list:
        breed_match = food.breed == breed or food.breed == "All"
        size_match = food.animalSize == size or food.animalSize == "All"
        life_stage_match = food.lifeStage == life_stage or food.lifeStage == "All"
        health_condition_match = (
            food.condition is None or food.condition in health_conditions
        )

        if breed_match and size_match and life_stage_match and health_condition_match:
            recommended_foods.append(food)

    return recommended_foods


def rank_products(recommended_foods, health_conditions, size, life_stage, breed):
    if not isinstance(health_conditions, list):
        health_conditions = [health_conditions] if health_conditions else []

    for food in recommended_foods:
        food.score = 0

        if (food.condition is None and not health_conditions) or (
            food.condition is not None and food.condition in health_conditions
        ):
            food.score += 3

        if food.animalSize == size or food.lifeStage == life_stage:
            food.score += 2

        if food.breed == breed:
            food.score += 1

        if food.breed == "All":
            food.score += 0.5

    recommended_foods.sort(key=lambda food: food.score, reverse=True)
    return recommended_foods
