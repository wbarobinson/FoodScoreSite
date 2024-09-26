import json
import logging

# Set up logging to output to a file and console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("nutrient_log.log"),  # Logs to a file
        logging.StreamHandler()  # Logs to the console
    ]
)

# Load the JSON data from the file 'foundationDownload.json'
file_path = 'foundationDownload.json'

try:
    with open(file_path, 'r') as file:
        content = file.read().strip()  # Read and strip any leading/trailing spaces
        if not content:
            raise ValueError("The JSON file is empty.")
        data = json.loads(content)
except FileNotFoundError:
    logging.error("File not found. Make sure 'foundationDownload.json' is in the correct directory.")
    data = None
except ValueError as e:
    logging.error(f"Error: {e}")
    data = None
except json.JSONDecodeError as e:
    logging.error(f"JSON Decode Error: {e}")
    data = None

# Nutrient names and IDs of interest to match various formats
nutrient_keywords = {
    'Protein': ['Protein', 'Proteins', 1003],
    'Fiber': ['Fiber, total dietary', 'Dietary Fiber', 1079],
    'Saturated Fat': ['Fatty acids, total saturated', 'Saturated Fat', 1258],
    'Total Fat': ['Total lipid (fat)', 'Fat', 'Total fat (NLEA)', 1004],
    'Carbohydrates': ['Carbohydrate, by difference', 'Carbs', 'Total Carbohydrate', 1005],
    'Calories': ['Energy', 'Calories', 1008, 'Energy (Atwater General Factors)', 'Energy (Atwater Specific Factors)', 2047, 2048]
}

# Function to match nutrient names or IDs
def match_nutrient(nutrient, keywords):
    name = nutrient['nutrient']['name']
    id_ = nutrient['nutrient']['id']
    return name in keywords or id_ in keywords

# Estimate calories if missing using macronutrient values
def estimate_calories(protein, fat, carbs, food_name):
    estimated_calories = (protein * 4) + (fat * 9) + (carbs * 4)
    logging.debug(f"Estimated calories for {food_name} from macronutrients: Protein={protein}g, Fat={fat}g, Carbs={carbs}g -> Estimated Calories={estimated_calories}")
    return estimated_calories if estimated_calories > 0 else 1  # Ensure it's not zero

# Function to calculate the food score with protein, fiber, and saturated fat scores multiplied by 100 and rounded
def calculate_score(protein, fiber, sat_fat, calories, food_name):
    # Calculate individual scores
    protein_score = round((protein / calories) * 100 / 125 * 100, 1)
    fiber_score = round((fiber / calories) * 100 / 25 * 100, 1)
    sat_fat_score = round(-(sat_fat / calories) * 100 / 15 * 100, 1)
    total_score = round(protein_score + fiber_score + sat_fat_score, 1)

    # Log each calculation step specifically for squash
    if "squash" in food_name.lower():
        logging.debug(f"Calculations for {food_name}:")
        logging.debug(f"Protein: {protein}g, Fiber: {fiber}g, Saturated Fat: {sat_fat}g, Calories: {calories} kcal")
        logging.debug(f"Protein Score Calculation: ({protein} / {calories}) * 100 / 125 * 100 = {protein_score}")
        logging.debug(f"Fiber Score Calculation: ({fiber} / {calories}) * 100 / 25 * 100 = {fiber_score}")
        logging.debug(f"Saturated Fat Score Calculation: -({sat_fat} / {calories}) * 100 / 15 * 100 = {sat_fat_score}")
        logging.debug(f"Total Score: {total_score}")

    return total_score, protein_score, fiber_score, sat_fat_score

# Function to extract nutrients, ensuring essential nutrients are present
def extract_nutrients(food):
    food_name = food.get('description', 'Unknown Food')
    # Allow optional nutrients (e.g., Fiber and Saturated Fat) to be missing
    nutrients = {'Protein': 0, 'Fiber': 0, 'Saturated Fat': 0, 'Calories': 0, 'Total Fat': 0, 'Carbohydrates': 0}

    # Extract each nutrient from food data
    for nutrient in food.get('foodNutrients', []):
        nutrient_name = nutrient['nutrient']['name']
        nutrient_id = nutrient['nutrient']['id']

        # Match nutrients correctly using specified keywords
        for key, keywords in nutrient_keywords.items():
            if match_nutrient(nutrient, keywords):
                nutrients[key] = nutrient.get('amount', 0)  # Use 0 if amount is not present
                break  # Stop further checks once a match is found

    # # Skip foods missing any essential nutrient data (Protein, Total Fat, Carbohydrates, Calories)
    # essential_nutrients = ['Protein', 'Total Fat', 'Carbohydrates', 'Calories']
    # if any(nutrients[n] is None for n in essential_nutrients):
    #     logging.warning(f"Skipping {food_name} due to missing essential nutrient data: {nutrients}")
    #     return None

    # Log the extracted nutrient amounts
    logging.debug(f"Nutrients extracted for {food_name}: {nutrients}")

    # Estimate calories if missing or zero
    if nutrients['Calories'] == 0:
        nutrients['Calories'] = estimate_calories(nutrients['Protein'], nutrients['Total Fat'], nutrients['Carbohydrates'], food_name)

    # Calculate scores and log the calculations
    total_score, protein_score, fiber_score, sat_fat_score = calculate_score(
        nutrients['Protein'], nutrients['Fiber'], nutrients['Saturated Fat'], nutrients['Calories'], food_name
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
    foods_data = [extract_nutrients(food) for food in data.get('FoundationFoods', []) if extract_nutrients(food) is not None]

    # Save the extracted and scored data to a JSON file
    output_file_path = 'foods_data.json'
    try:
        with open(output_file_path, 'w') as output_file:
            json.dump(foods_data, output_file, indent=4)  # Pretty-print with an indent of 4 spaces
        logging.info(f"Data successfully saved to {output_file_path}")
    except Exception as e:
        logging.error(f"Error saving data: {e}")

    # Display sample output
    for food in foods_data[:10]:  # Display first 10 entries as a sample
        print(food)
else:
    logging.error("Failed to extract data due to an error in reading the JSON file.")