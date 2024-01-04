import json
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def load_data(file_name):
    file_path = f'./{file_name}'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_recommendations(preferences):
    dog_food_data = load_data('db-food.json')

    df = pd.DataFrame(dog_food_data)
    print(df.head())

    clean_df = df.drop(['picture', 'name', 'brand', 'packageWeight_kg', 'packageWeight_lb', 'price', 'calories'], axis=1)

    df_encoded = pd.get_dummies(clean_df, columns=['breed', 'animalSize', 'lifeStage', 'condition'])

    print(df_encoded.head())

    X = df_encoded.drop('_id', axis=1)
    y = df_encoded['_id']

    clf = DecisionTreeClassifier()

    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    weights = {
        "breed": 1.0,
        "animalSize": 2.0,
        "lifeStage": 1.5,
        "condition": 3.0 
    }

    # Initialize user_preferences with all zeros
    features_from_dataset = df_encoded.columns.tolist()
    user_preferences = {feature: 0 for feature in features_from_dataset}

    user_preferences.update(preferences)

    for key, value in user_preferences.items():
        category = key.split('_')[0] if '_' in key else key
        weight = weights.get(category, 1.0)
        user_preferences[key] = value * weight

    # Convert to a vector
    user_preferences_vector = np.array(list(user_preferences.values())).reshape(1, -1)

    # Compute similarities
    similarities = cosine_similarity(df_encoded, user_preferences_vector)

    index_list = np.argsort(similarities.flatten())[::-1]
    top_n = 3
    top_recommendations_indices = index_list[:top_n]

    recommended_dog_foods = df.iloc[top_recommendations_indices]
    recommended_list = recommended_dog_foods[['name', 'brand', 'animalSize']].values.tolist()
    
    print(recommended_list)
    return recommended_list

generate_recommendations({
        "breed_German Shepherd": 1,
        "animalSize_Large": 1,
        "lifeStage_Senior": 1,
        "condition_Joint Care": 1
    })