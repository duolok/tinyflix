import base64
import json
import subprocess
import os

file_path = '../../tinyflix-front/src/assets/easy.mp4'
lambda_function_name = 'TinyflixBackStack-UploadFileFunction8A23BF65-EYGszju1KMDF'

try:
    with open(file_path, 'rb') as file:
        file_content = file.read()
    encoded_content = base64.b64encode(file_content).decode('utf-8')
except FileNotFoundError:
    print(f"File not found: {file_path}")
    exit(1)

# Step 2: Create the event payload
payload = {
    "body": json.dumps({
        "file_name": "example.mp4",
        "file_content": encoded_content
    })
}

# Save the payload to a JSON file
event_json_path = 'event.json'
response_json_path = 'response.json'
with open(event_json_path, 'w') as json_file:
    json.dump(payload, json_file)

# Step 3: Invoke the Lambda function using AWS CLI
try:
    result = subprocess.run([
        'aws', 'lambda', 'invoke',
        '--function-name', lambda_function_name,
        '--payload', f'file://{os.path.abspath(event_json_path)}',
        os.path.abspath(response_json_path)
    ], check=True, capture_output=True, text=True)

    # Check the response
    with open(response_json_path, 'r') as response_file:
        response = json.load(response_file)
    print("Lambda function invoked successfully.")
    print("Response:", json.dumps(response, indent=4))
except subprocess.CalledProcessError as e:
    print("Failed to invoke Lambda function.")
    print("Error message:", e.stderr)

