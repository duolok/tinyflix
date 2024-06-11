
#!/bin/zsh

# Define file paths
FILE_PATH="../../tinyflix-front/src/assets/Vince Staples - Home (Spider-Man_ Into the Spider-Verse).mp4"
PAYLOAD_FILE="payload.json"

# Encode the file content to base64
FILE_CONTENT=$(base64 -w 0 "$FILE_PATH")

# Create the payload JSON
jq -n --arg file_name 'Vince Staples - Home (Spider-Man_ Into the Spider-Verse).mp4' --arg file_content "$FILE_CONTENT" '{body: {file_name: $file_name, file_content: $file_content}}' > $PAYLOAD_FILE
