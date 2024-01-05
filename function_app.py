import json
import azure.functions as func
import logging
from recommendation_logic import generate_recommendations

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="recommendation/dogs", methods=["POST"])
def recommendation_logic(req: func.HttpRequest) -> func.HttpResponse:

    try:
        data = req.get_json()
        breed = data.get('breed', None)
        animalWeight = data.get('animalWeight', None)
        age = data.get('age', None)
        conditions = data.get('conditions', [])
        
        if not isinstance(breed, str):
            return func.HttpResponse("Breed must be a string.", status_code=400)
        else:
            breed = f"breed_{breed}"
            
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
        
        if not (isinstance(age, int) or isinstance(age, float)):
            return func.HttpResponse("Age must be a number.", status_code=400)  
        else:
            if age >= 7:
                age = "lifeStage_Senior"
            elif age >= 2:
                age = "lifeStage_Adult"
            else:
                age = "lifeStage_Puppy"
        if not (isinstance(conditions, list) and all(isinstance(cond, str) for cond in conditions)):
            return func.HttpResponse("Conditions must be an array of strings.", status_code=400)
        else:
            conditions = [f"condition_{condition}" for condition in conditions]
        
        user_preferences = {
            breed: 1,
            animalWeight: 1,
            age: 1
        }
        
        user_preferences.update({condition: 1 for condition in conditions})

        recommendations = generate_recommendations(user_preferences)
        recommendations_json = json.dumps(recommendations, ensure_ascii=False)
        
        return func.HttpResponse(recommendations_json, status_code=200, mimetype="application/json", 
            charset='utf-8')

    except ValueError:
        return func.HttpResponse(
             "Invalid request. Please send a valid JSON.",
             status_code=400
        )