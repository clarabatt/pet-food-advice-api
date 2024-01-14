import json
import azure.functions as func
import logging
from dog_food import get_food_recommendations, check_if_breed_exists, rank_products

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


def validate_format_breed(breed):
    if not isinstance(breed, str):
        return func.HttpResponse("Breed must be a string.", status_code=400)
    else:
        if not check_if_breed_exists(breed):
            breed = "All"
    return breed


def validate_format_animalWeight(animalWeight):
    if not (isinstance(animalWeight, int) or isinstance(animalWeight, float)):
        return func.HttpResponse("Animal weight must be a number.", status_code=400)
    else:
        if animalWeight >= 70:
            animalWeight = "Giant"
        elif animalWeight >= 50:
            animalWeight = "Large"
        elif animalWeight >= 25:
            animalWeight = "Medium"
        elif animalWeight >= 12:
            animalWeight = "Small"
        else:
            animalWeight = "X-Small"
    return animalWeight


def validate_format_age(age):
    if not (isinstance(age, int) or isinstance(age, float)):
        return func.HttpResponse("Age must be a number.", status_code=400)
    else:
        if age >= 7:
            age = "Senior"
        elif age >= 2:
            age = "Adult"
        else:
            age = "Puppy"
    return age


def validate_format_conditions(conditions):
    condition_mapping = {
        "Allergies or Food Sensitivities": ["Food Allergy", "Sensitive Stomach & Skin"],
        "Food Allergy": ["Food Allergy", "Sensitive Stomach & Skin"],
        "Sensitive Stomach & Skin": ["Food Allergy", "Sensitive Stomach & Skin"],
        "Overweight": ["Overweight"],
        "Skin and Coat Health": ["Skin/Coat problems", "Sensitive Stomach & Skin"],
        "Skin/Coat problems": ["Skin/Coat problems", "Sensitive Stomach & Skin"],
        "Sensitive Stomach & Skin": ["Skin/Coat problems", "Sensitive Stomach & Skin"],
        "Digestive issues": ["Digestive Care"],
        "Digestive Care": ["Digestive Care"],
        "Mobility concerns": ["Joint Care"],
        "Joint Care": ["Joint Care"],
        "Dental issues": ["Dental Care"],
        "Dental Care": ["Dental Care"],
        "Urinary problems": ["Urinary Care"],
        "Urinary Care": ["Urinary Care"],
    }

    if not (
        isinstance(conditions, list)
        and all(isinstance(cond, str) for cond in conditions)
    ):
        return func.HttpResponse(
            "Conditions must be an array of strings.", status_code=400
        )

    formatted_conditions = []

    for condition in conditions:
        if condition not in condition_mapping:
            error_message = (
                f"The condition '{condition}' is not recognized. "
                f"Recognized conditions are: {condition_mapping.keys()}."
            )
            return func.HttpResponse(error_message, status_code=400)
        else:
            formatted_conditions.extend(condition_mapping[condition])

    return formatted_conditions


@app.route(route="recommendation/dogs", methods=["POST"])
def recommendation_logic(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        breed = data.get("breed", None)
        animalWeight = data.get("animalWeight", None)
        age = data.get("age", None)
        conditions = data.get("conditions", [])

        # Validate and formating breed
        breed = validate_format_breed(breed)
        if isinstance(breed, func.HttpResponse):
            return breed

        # Validate and formating animalWeight
        animalWeight = validate_format_animalWeight(animalWeight)
        if isinstance(animalWeight, func.HttpResponse):
            return animalWeight

        # Validate and formating age
        age = validate_format_age(age)
        if isinstance(age, func.HttpResponse):
            return age

        # Validate and formating conditions
        conditions = validate_format_conditions(conditions)
        if isinstance(conditions, func.HttpResponse):
            return conditions

        try:
            recommendations = get_food_recommendations(
                breed, animalWeight, age, conditions
            )

            top_recommendations = rank_products(
                recommendations, conditions, animalWeight, age, breed
            )[:3]

            top_recommendations_dict = [
                dog_food.to_dict() for dog_food in top_recommendations
            ]
            recommendations_json = json.dumps(
                top_recommendations_dict, ensure_ascii=False
            )
        except Exception as e:
            logging.error(e)
            return func.HttpResponse(
                "Something went wrong getting recommendations.", status_code=500
            )

        return func.HttpResponse(
            recommendations_json,
            status_code=200,
            mimetype="application/json",
            charset="utf-8",
        )

    except ValueError:
        return func.HttpResponse(
            "Invalid request. Please send a valid JSON.", status_code=400
        )
