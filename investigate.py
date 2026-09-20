## Import the necessary modules
import json
import ollama

## Import the function from the module parse_data
from parse_data import load_items, get_unclaimed_items, save_result



## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
## The model must follow the rules listed in the README file
## The function should return the system prompt and the user prompt.
## You may need to use json.dumps() to convert the available_items list into a JSON string.

def build_prompt(description, available_items):
    system_prompt = '''You are a campus lost-and-found assistant. Your task is to find possible matches for a lost item based on the user's description.

Rules:
- You must use only the given JSON file (the available items list).
- Not all the details of an item must match to be a possible match.
- You must return only JSON, with exactly the following structure:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}
- "matches" contains all the possible matches (item IDs).
- "confidence" measures how confident you are about the matches. It must be exactly one of: LOW, MEDIUM, HIGH.
- If there is no match, you must return an empty list for "matches".
- Do not include any text outside the JSON response.'''
    user_prompt = f'''Description of the lost item: {description}

Available items in the lost-and-found database:
{json.dumps(available_items, indent=2)}

Based on the description and the available items above, return only the JSON response following the rules.'''
    return system_prompt, user_prompt


## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
## The function should return the response from Qwen.
def ask_qwen(system_prompt, user_prompt):
    response = ollama.chat(
        model="qwen",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response["message"]["content"]


## Logic to parse the response from Qwen and return the result. 
## You may need to use json.loads() to convert the response string into a suitable Python data structure.
def parse_response(response_text):
    return json.loads(response_text)
    


## Logic to validate the result returned by Qwen.
## It should check if the result is a dictionary, contains the keys "matches" and "confidence", and that the values are of the correct type.
## If everything is correct, then it should check if the item IDs in the "matches" list are valid IDs .
def validate_result(result, available_items):
    if not isinstance(result, dict):
        return False
    if "matches" not in result or "confidence" not in result:
        return False
    if not isinstance(result["matches"], list):
        return False
    if not all(isinstance(i, str) for i in result["matches"]):
        return False
    if result["confidence"] not in ("LOW", "MEDIUM", "HIGH"):
        return False
    valid_ids = [item["id"] for item in available_items]
    for item_id in result["matches"]:
        if item_id not in valid_ids:
            return False
    return True


## Logic to display the matches found by Qwen in a user-friendly format.
## It should look something like this:
""" 
CAMPUS LOST-AND-FOUND ASSISTANT
==================================================

Describe the item you lost: I lost a black bag somewhere

Searching for possible matches...

MATCH RESULT
--------------------------------------------------
Confidence: MEDIUM

Possible matches:

ID: F101
Item: backpack
Color: black
Location: Library 2nd floor
Date found: 2026-09-15

Result saved to output/match_result.json
 """
## If no matches are found, it should display a message indicating that no matches were found, along with the empty list
def display_matches(result, available_items):
    matches = result.get("matches", [])
    confidence = result.get("confidence", "LOW")
    print("MATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {confidence}")
    print()
    if not matches:
        print("No matches found.")
        print(f"Matches: {matches}")
        return
    print("Possible matches:")
    print()
    items_by_id = {item["id"]: item for item in available_items}
    for item_id in matches:
        item = items_by_id.get(item_id)
        if not item:
            continue
        print(f"ID: {item.get('id', '')}")
        print(f"Item: {item.get('item', '')}")
        print(f"Color: {item.get('color', '')}")
        print(f"Location: {item.get('location', '')}")
        print(f"Date found: {item.get('date', '')}")
        print()
    

## Control center for the entire program.
def main():
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()
    description = input("Describe the item you lost: ")
    print()
    print("Searching for possible matches...")
    print()

    items = load_items("found_items.json")
    available_items = get_unclaimed_items(items)

    system_prompt, user_prompt = build_prompt(description, available_items)
    response_text = ask_qwen(system_prompt, user_prompt)
    result = parse_response(response_text)
    if not validate_result(result, available_items):
        print("The response from Qwen is not valid.")
        return
    display_matches(result, available_items)

    save_result(result, "output/match_result.json")
    print("Result saved to output/match_result.json")


if __name__ == "__main__":
    main()