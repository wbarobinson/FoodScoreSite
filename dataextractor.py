import json

# Load the JSON data from the file 'foundationDownload.json'
file_path = 'foundationDownload.json'

try:
    with open(file_path, 'r') as file:
        content = file.read().strip()  # Read and strip any leading/trailing spaces
        if not content:
            raise ValueError("The JSON file is empty.")
        data = json.loads(content)
except FileNotFoundError:
    print("File not found. Make sure 'foundationDownload.json' is in the correct directory.")
    data = None
except ValueError as e:
    print(f"Error: {e}")
    data = None
except json.JSONDecodeError as e:
    print(f"JSON Decode Error: {e}")
    data = None

# Function to calculate the food score
def calculate_score(protein, fiber, sat_fat, calories):
    protein_score = (protein / calories) * 100 / 125 if calories > 0 else 0
    fiber_score = (fiber / calories) * 100 / 25 if calories > 0 else 0
    sat_fat_score = -(sat_fat / calories) * 100 / 15 if calories > 0 else 0
    total_score = (protein_score + fiber_score + sat_fat_score) * 100
    return round(total_score, 1), round(protein_score, 4), round(fiber_score, 4), round(sat_fat_score, 4)

# Extract relevant nutrients from each food item
def extract_nutrients(food):
    food_name = food.get('description', 'Unknown Food')
    nutrients = {'Protein': 0, 'Fiber': 0, 'Saturated Fat': 0, 'Calories': 0}

    for nutrient in food.get('foodNutrients', []):
        nutrient_name = nutrient['nutrient']['name']
        nutrient_amount = nutrient.get('amount', 0)
        if nutrient_name == 'Protein':
            nutrients['Protein'] = nutrient_amount
        elif nutrient_name == 'Fiber, total dietary':
            nutrients['Fiber'] = nutrient_amount
        elif nutrient_name == 'Fatty acids, total saturated':
            nutrients['Saturated Fat'] = nutrient_amount
        elif nutrient_name == 'Energy':
            nutrients['Calories'] = nutrient_amount

    total_score, protein_score, fiber_score, sat_fat_score = calculate_score(
        nutrients['Protein'], nutrients['Fiber'], nutrients['Saturated Fat'], nutrients['Calories']
    )
    
    return {
        'Food': food_name,
        'Total Score': total_score,
        'Protein Score': protein_score,
        'Fiber Score': fiber_score,
        'Saturated Fat Score': sat_fat_score
    }

# Extract and calculate scores for each food item
if data:
    foods_data = [extract_nutrients(food) for food in data.get('FoundationFoods', [])]

    # Save the extracted and scored data to a JSON file
    output_file_path = 'foods_data.json'
    try:
        with open(output_file_path, 'w') as output_file:
            json.dump(foods_data, output_file, indent=4)  # Pretty-print with an indent of 4 spaces
        print(f"Data successfully saved to {output_file_path}")
    except Exception as e:
        print(f"Error saving data: {e}")

    # Display sample output
    for food in foods_data[:10]:  # Display first 10 entries as a sample
        print(food)
else:
    print("Failed to extract data due to an error in reading the JSON file.")