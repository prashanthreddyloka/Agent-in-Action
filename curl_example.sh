#!/bin/bash

# 1. Start the Triage Process
echo "1. Invoking Triage..."
RESPONSE=$(curl -s -X POST "http://localhost:8000/triage/invoke" \
     -H "Content-Type: application/json" \
     -d '{
           "ticket_text": "I ordered a toaster but received a blender. Order #55555"
         }')

echo "Response: $RESPONSE"

# Extract thread_id (requires jq, or we just print it)
# For demo purposes, we'll just print instructions.
echo ""
echo "---------------------------------------------------"
echo "Check the 'thread_id' in the JSON response above."
echo "Then, to approve the response, run:"
echo ""
echo "curl -X POST 'http://localhost:8000/triage/approve' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"thread_id\": \"<YOUR_THREAD_ID>\", \"approved\": true}'"
echo "---------------------------------------------------"
