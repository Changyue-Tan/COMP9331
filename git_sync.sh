#!/bin/bash

# Prompt the user to enter a commit message
echo "Enter commit message: "
read commit_message

# Add changes, commit with the provided message, and push to the main branch
git add .
git commit -m "$commit_message"
git push origin main
