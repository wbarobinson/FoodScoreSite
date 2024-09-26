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

# Nutrient names and IDs of interest to match various formats
nutrient_keywords = {
    'Protein': ['Protein', 'Proteins', 1003],
    'Fiber': ['Fiber, total dietary', 'Dietary Fiber', 1079],
    'Saturated Fat': ['Fatty acids, total saturated', 'Saturated Fat', 1258],
    'Calories': ['Energy', 'Calories', 1008, 'Energy (Atwater General Factors)', 'Energy (Atwater Specific Factors)', 2047, 2048]
}

# Function to match nutrient names or IDs
def match_nutrient(nutrient, keywords):
    name = nutrient['nutrient']['name']
    id_ = nutrient['nutrient']['id']
    return name in keywords or id_ in keywords

# Function to calculate the food score with protein, fiber, and saturated fat scores multiplied by 100 and rounded
def calculate_score(protein, fiber, sat_fat, calories):
    protein_score = round((protein / calories) * 100 / 125 * 100, 1) if calories > 0 else 0
    fiber_score = round((fiber / calories) * 100 / 25 * 100, 1) if calories > 0 else 0
    sat_fat_score = round(-(sat_fat / calories) * 100 / 15 * 100, 1) if calories > 0 else 0
    total_score = round(protein_score + fiber_score + sat_fat_score, 1)
    return total_score, protein_score, fiber_score, sat_fat_score

# Extract relevant nutrients from each food item
def extract_nutrients(food):
    food_name = food.get('description', 'Unknown Food')
    nutrients = {'Protein': 0, 'Fiber': 0, 'Saturated Fat': 0, 'Calories': 0}

    for nutrient in food.get('foodNutrients', []):
        # Match each nutrient by its name or ID using the keywords defined above
        for key, keywords in nutrient_keywords.items():
            if match_nutrient(nutrient, keywords):
                nutrients[key] = nutrient.get('amount', 0)

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