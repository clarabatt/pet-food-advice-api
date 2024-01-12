import json
import pandas as pd
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

def load_data(file_name):
    file_path = f'./{file_name}'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def check_breed(breed):
    dog_food_data = load_data('db-food.json')
    df = pd.DataFrame(dog_food_data)
    breeds_list = df['breed'].unique()
    if breed not in breeds_list:
        return False
    return True

def generate_recommendations(preferred_breed, preferred_animal_size, preferred_life_stage, preferred_conditions):

    print(preferred_breed, preferred_animal_size, preferred_life_stage, preferred_conditions)

    df = pd.DataFrame(load_data('db-food.json'))
    clean_df = df.drop(['picture', 'name', 'brand', 'packageWeight_kg', 'packageWeight_lb', 'price', 'calories'], axis=1)

    df_encoded = pd.get_dummies(clean_df, columns=['breed', 'animalSize', 'lifeStage', 'condition'])

    # Filter animalSize and lifeStage

    filter_condition = (
        (df_encoded['animalSize_' + preferred_animal_size] == 1) | (df_encoded['animalSize_All'] == 1)
    ) & (
        (df_encoded['lifeStage_' + preferred_life_stage] == 1) | (df_encoded['lifeStage_All'] == 1)
    )
    if preferred_breed:
        filter_condition &= (df_encoded['breed_' + preferred_breed] == 1) | (df_encoded['breed_All'] == 1)
    else:
        filter_condition &= (df_encoded['breed_All'] == 1)
        
    filtered_df_encoded = df_encoded[filter_condition]

    # Filter for conditions
    if len(preferred_conditions) > 0:
        for condition in preferred_conditions:
            filter_condition = (df_encoded[f'condition_{condition}'] == 1)
            filtered_df_encoded = filtered_df_encoded[filter_condition]
    else:
        condition_cols = df_encoded.filter(regex='condition_').columns
        filtered_df_encoded = df_encoded[(df_encoded[condition_cols] != 1).all(axis=1)]

    # ------------

    weights = {
        "breed": 2,
        "animalSize": 1,
        "lifeStage": 1,
        "condition": 2 
    }

    user_preferences = {feature: 0 for feature in df_encoded.columns.tolist()}

    user_preferences[f'animalSize_{preferred_animal_size}'] = 1
    user_preferences[f'lifeStage_{preferred_life_stage}'] = 1
    
    if len(preferred_conditions) > 0:
        for condition in preferred_conditions:
            user_preferences[f'condition_{condition}'] = weights['condition']

    for key, value in user_preferences.items():
        category = key.split('_')[0] if '_' in key else key
        weight = weights.get(category, 1.0)
        user_preferences[key] = value * weight

    # Convert to a vector
    user_preferences_vector = np.array(list(user_preferences.values())).reshape(1, -1)

    # Compute similarities
    similarities = cosine_similarity(filtered_df_encoded, user_preferences_vector)

    index_list = np.argsort(similarities.flatten())[::-1]
    top_n = 2
    top_recommendations_indices = index_list[:top_n]

    recommended_foods = df.loc[filtered_df_encoded.index[top_recommendations_indices]]
    recommended_list = recommended_foods.to_dict(orient='records')
        
    return recommended_list
