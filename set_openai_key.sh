#!/bin/bash

# Script to set OpenAI API key
# This will add the key to your .env file and optionally export it for the current session

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}OpenAI API Key Setup${NC}"
echo "===================="
echo ""

# Get the project root directory (where this script is located)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ENV_FILE="$SCRIPT_DIR/.env"

# Prompt for API key (hidden input)
echo -e "${YELLOW}Enter your OpenAI API key:${NC}"
read -s API_KEY

# Validate that key was entered
if [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: API key cannot be empty${NC}"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    touch "$ENV_FILE"
fi

# Check if OPENAI_API_KEY already exists in .env
if grep -q "^OPENAI_API_KEY=" "$ENV_FILE"; then
    # Update existing key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|" "$ENV_FILE"
    else
        # Linux
        sed -i "s|^OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|" "$ENV_FILE"
    fi
    echo -e "${GREEN}✓ Updated existing OPENAI_API_KEY in .env file${NC}"
else
    # Add new key
    echo "" >> "$ENV_FILE"
    echo "# OpenAI API Key" >> "$ENV_FILE"
    echo "OPENAI_API_KEY=$API_KEY" >> "$ENV_FILE"
    echo -e "${GREEN}✓ Added OPENAI_API_KEY to .env file${NC}"
fi

# Export for current session
export OPENAI_API_KEY="$API_KEY"
echo -e "${GREEN}✓ Exported OPENAI_API_KEY for current terminal session${NC}"

echo ""
echo -e "${GREEN}Setup complete!${NC}"
echo ""
echo "The API key has been:"
echo "  • Saved to: $ENV_FILE"
echo "  • Exported for this terminal session"
echo ""
echo -e "${YELLOW}Note:${NC} You may need to restart your backend server for the changes to take effect."
echo ""

