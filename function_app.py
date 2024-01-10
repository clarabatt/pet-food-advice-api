import json
import azure.functions as func
import logging
from recommendation_logic import generate_recommendations, check_breed

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

def validate_format_breed(breed):
    if not isinstance(breed, str):
        return func.HttpResponse("Breed must be a string.", status_code=400)
    else:
        if check_breed(breed):
            breed = f"breed_{breed}"
        else:
            breed = "breed_All"
    return breed

def validate_format_animalWeight(animalWeight):
    if not (isinstance(animalWeight, int) or isinstance(animalWeight, float)):
        return func.HttpResponse("Animal weight must be a number.", status_code=400)
    else:
        if animalWeight >= 70:
            animalWeight = "animalSize_Giant"
        elif animalWeight >= 50:
            animalWeight = "animalSize_Large"
        elif animalWeight >= 25:
            animalWeight = "animalSize_Medium"
        elif animalWeight >= 12:
            animalWeight = "animalSize_Small"
        else:
            animalWeight = "animalSize_X-Small"
    return animalWeight

def validate_format_age(age):
    if not (isinstance(age, int) or isinstance(age, float)):
        return func.HttpResponse("Age must be a number.", status_code=400)  
    else:
        if age >= 7:
            age = "lifeStage_Senior"
        elif age >= 2:
            age = "lifeStage_Adult"
        else:
            age = "lifeStage_Puppy"
    return age

def validate_format_conditions(conditions):
    condition_mapping = {
        'Food Allergy': 'Allergies or Food Sensitivities',
        'Sensitive Stomach & Skin': 'Allergies or Food Sensitivities',
        'Overweight': 'Overweight',
        'Skin and Coat Health': 'Skin/Coat problems',
        'Digestive Care': 'Digestive issues',
        'Joint Care': 'Mobility concerns',
        'Dental Care': 'Dental issues',
    }
    
    recognized_conditions = ', '.join(set(condition_mapping.keys()).union(set(condition_mapping.values())))

    if not (isinstance(conditions, list) and all(isinstance(cond, str) for cond in conditions)):
            return func.HttpResponse("Conditions must be an array of strings.", status_code=400)

    formatted_conditions = []

    for condition in conditions:
        if condition in condition_mapping:
            formatted_conditions.append(f"condition_{condition}")
        elif condition in condition_mapping.values():
            key = [k for k, v in condition_mapping.items() if v == condition][0]
            formatted_conditions.append(f"condition_{key}")
        else:
            error_message = (f"The condition '{condition}' is not recognized. "
                            f"Recognized conditions are: {recognized_conditions}.")
            return func.HttpResponse(error_message, status_code=400)

    return formatted_conditions

@app.route(route="recommendation/dogs", methods=["POST"])
def recommendation_logic(req: func.HttpRequest) -> func.HttpResponse:

    try:
        data = req.get_json()
        breed = data.get('breed', None)
        animalWeight = data.get('animalWeight', None)
        age = data.get('age', None)
        conditions = data.get('conditions', [])
        
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
        
        # Mount user preferences dictionary
        user_preferences = {
            breed: 1,
            animalWeight: 1,
            age: 1
        }
        
        # Complete user preferences with conditions
        user_preferences.update({condition: 1 for condition in conditions})

        try:
            recommendations = generate_recommendations(user_preferences)
            recommendations_json = json.dumps(recommendations, ensure_ascii=False)
        except Exception as e:
            logging.error(e)
            return func.HttpResponse(
                "Something went wrong getting recommendations.",
                status_code=500
            )
        
        return func.HttpResponse(recommendations_json, status_code=200, mimetype="application/json", 
            charset='utf-8')

    except ValueError:
        return func.HttpResponse(
             "Invalid request. Please send a valid JSON.",
             status_code=400
        )