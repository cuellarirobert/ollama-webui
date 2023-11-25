from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import csv
import os
import datetime
import re

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Define the desired order of headers
csv_headers = ["timestamp", "duration", "customer", "task"]
log_filename = "timelogs.csv"
log_file_path = os.path.join(os.path.dirname(__file__), log_filename)

def init_csv_file():
    # Check if the log file exists, and if not, create a new one with headers
    if not os.path.isfile(log_file_path):
        with open(log_file_path, mode='w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()

# Call the initialization function on startup
init_csv_file()


@app.post("/display-message/")
async def display_message(request: Request):
    body = await request.json()  # Parses the incoming JSON object
    message_text = body.get("text", "").strip()

    if not message_text:
        raise HTTPException(status_code=400, detail="No message provided")

    try:
        # Attempt to parse the JSON string
        data_dict = json.loads(message_text)
    except json.JSONDecodeError:
        # Fallback to salvage data from incorrectly formatted JSON
        data_dict = salvage_data(message_text)

    if not all(key in data_dict for key in ["duration", "task", "customer"]):
        raise HTTPException(status_code=400, detail="Required data fields missing")

    data_dict["timestamp"] = str(datetime.datetime.now())

    # Save the data to a CSV file
    log_filename = "timelogs.csv"
    log_file_path = os.path.join(os.path.dirname(__file__), log_filename)

    # Check if the log file exists, and if not, create a new one with headers
    file_exists = os.path.isfile(log_file_path)
    # Save the data to a CSV file without checking if the file exists here
    with open(log_file_path, mode="a", newline="") as log_file:
        writer = csv.DictWriter(log_file, fieldnames=csv_headers)
        # No need to check if file exists or write headers here
        writer.writerow({field: data_dict.get(field, "") for field in csv_headers})

    return {"message": f"Received message as dictionary: {data_dict}, and logged to CSV."}

def salvage_data(text):
    # Attempt to clean up the text by removing trailing non-JSON characters
    cleaned_text = re.sub(r'[^}]*$', '', text)

    # Regular expression to extract key-value pairs
    pattern = r'"(duration|task|customer)":\s*("[^"]*"|\d+)'
    matches = re.findall(pattern, cleaned_text)

    return {key: json.loads(value) for key, value in matches}


# Run the application as before...
