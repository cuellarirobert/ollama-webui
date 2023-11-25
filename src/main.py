# from fastapi import FastAPI, HTTPException, Request
# from fastapi.middleware.cors import CORSMiddleware
# import json
# import csv
# import os
# import datetime
# import re

# app = FastAPI()

# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allows all origins
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# # Define the desired order of headers
# csv_headers = ["timestamp", "duration", "customer", "task"]
# log_filename = "timelogs.csv"
# log_file_path = os.path.join(os.path.dirname(__file__), log_filename)

# def init_csv_file():
#     # Check if the log file exists, and if not, create a new one with headers
#     if not os.path.isfile(log_file_path):
#         with open(log_file_path, mode='w', newline='') as f:
#             writer = csv.DictWriter(f, fieldnames=csv_headers)
#             writer.writeheader()

# # Call the initialization function on startup
# init_csv_file()


# @app.post("/display-message/")
# async def display_message(request: Request):
#     body = await request.json()  # Parses the incoming JSON object
#     message_text = body.get("text", "").strip()

#     if not message_text:
#         raise HTTPException(status_code=400, detail="No message provided")

#     try:
#         # Attempt to parse the JSON string
#         data_dict = json.loads(message_text)
#     except json.JSONDecodeError:
#         # Fallback to salvage data from incorrectly formatted JSON
#         data_dict = salvage_data(message_text)

#     if not all(key in data_dict for key in ["duration", "task", "customer"]):
#         raise HTTPException(status_code=400, detail="Required data fields missing")

#     data_dict["timestamp"] = str(datetime.datetime.now())

#     # Save the data to a CSV file
#     log_filename = "timelogs.csv"
#     log_file_path = os.path.join(os.path.dirname(__file__), log_filename)

#     # Check if the log file exists, and if not, create a new one with headers
#     file_exists = os.path.isfile(log_file_path)
#     # Save the data to a CSV file without checking if the file exists here
#     with open(log_file_path, mode="a", newline="") as log_file:
#         writer = csv.DictWriter(log_file, fieldnames=csv_headers)
#         # No need to check if file exists or write headers here
#         writer.writerow({field: data_dict.get(field, "") for field in csv_headers})

#     return {"message": f"Received message as dictionary: {data_dict}, and logged to CSV."}



# # Run the application as before...

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import csv
import os
import datetime
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

csv_headers = ["timestamp", "duration", "customer", "task"]
log_filename = "timelogs.csv"
log_file_path = os.path.join(os.path.dirname(__file__), log_filename)

def init_csv_file():
    if not os.path.isfile(log_file_path):
        with open(log_file_path, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()

init_csv_file()

def salvage_data(text):
    # Attempt to clean up the text by removing trailing non-JSON characters
    cleaned_text = re.sub(r'[^}]*$', '', text)

    # Regular expression to extract key-value pairs
    pattern = r'"(duration|task|customer)":\s*("[^"]*"|\d+)'
    matches = re.findall(pattern, cleaned_text)

    return {key: json.loads(value) for key, value in matches}


@app.post("/timelog/")
async def timelog_handler(data: dict):
    data["timestamp"] = str(datetime.datetime.now())
    with open(log_file_path, mode="a", newline="") as log_file:
        writer = csv.DictWriter(log_file, fieldnames=csv_headers)
        writer.writerow({field: data.get(field, "") for field in csv_headers})
    return {"message": "Timelog processed and logged to CSV."}

@app.post("/addition/")
async def addition_handler(data: dict):
    value_1 = data.get("value_1", 0)
    value_2 = data.get("value_2", 0)
    sum_result = value_1 + value_2
    return {"message": f"The sum is {sum_result}."}

@app.post("/multiplication/")
async def multiplication_handler(data: dict):
    value_1 = data.get("value_1", 1)
    value_2 = data.get("value_2", 1)
    product_result = value_1 * value_2
    return {"message": f"The product is {product_result}."}

@app.post("/display-message/")
async def display_message(request: Request):
    body = await request.json()
    text_content = body.get("text", "")

    # First, try to match the JSON within markdown code block syntax
    match = re.search(r'```json\s*\{[\s\S]*\}\s*```', text_content)
    
    if match:
        # Extract JSON string from markdown and remove markdown syntax
        json_str = match.group(0).replace('```json', '').replace('```', '').strip()
    else:
        # If no match, assume the text is a plain JSON string
        json_str = text_content.strip()

    try:
        actual_content = json.loads(json_str)
    except json.JSONDecodeError:
        return {"message": "Invalid JSON format."}

    endpoint = actual_content.get("endpoint")

    if endpoint == "timelog":
        return await timelog_handler(actual_content)
    elif endpoint == "addition":
        return await addition_handler(actual_content)
    elif endpoint == "multiplication":
        return await multiplication_handler(actual_content)

    return {"message": "Endpoint not recognized."}
