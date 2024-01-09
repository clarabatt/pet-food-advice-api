# Dog Food Recommendation Azure Function

This project contains an Azure Function that provides dog food recommendations based on a dog's breed, weight, age, and health conditions. The function is accessible via an HTTP POST request which expects a json and returns a list of recommended dog food options.

## Features

- **POST Endpoint**: `recommendation/dogs` to get dog food recommendations.
- **Input Parameters**: Breed, Animal Weight, Age, Health Conditions.

  ```json
  // Input Example
  {
    "breed": "German Shepherd",
    "animalWeight": 30,
    "age": 5,
    "conditions": ["Joint Care", "Food Allergy"]
  }
  ```

- **Output**: A list of recommended dog foods based on the input criteria.

```json
// Output Example
[
  {
    "name": "Royal Canin® Breed Health Nutrition® German Shepherd Adult Dry Dog Food",
    "brand": "Royal Canin",
    "price": 122.99,
    "calories": 327
  },
  {
    "name": "Blue Buffalo® Basics™ Small Breed Adult Dry Dog Food - Natural, Turkey",
    "brand": "Blue Buffalo",
    "price": 30.99,
    "calories": 453
  },
  {
    "name": "Royal Canin® Size Health Nutrition Large Adult 5+ Dry Dog Food",
    "brand": "Royal Canin",
    "price": 122.99,
    "calories": 414
  }
]
```

## Getting Started

### Running Locally

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Create a new virtual environment:

```bash
python -m venv .venv
```

4. Activate the virtual environment:

```bash
# Windows
.venv\Scripts\activate

# Linux / MacOS
source .venv/bin/activate
```

5. Install the dependencies:

```bash
pip install -r requirements.txt
```

6. Start the function locally by running:

```bash
func start
```

7. The function will be available at `http://localhost:7071/api/recommendation/dogs`.

### Testing the Function

You can test the function using this CURL command:

```bash
curl -X POST http://localhost:7071/api/recommendation/dogs \
-H "Content-Type: application/json" \
-d '{"breed": "German Shepherd", "animalWeight": 30, "age": 5, "conditions": ["Joint Care", "Food Allergy"]}'
```
