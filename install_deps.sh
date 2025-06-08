#!/bin/bash
# This script installs runtime dependencies and specified type hints.

echo "Installing runtime dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    echo "ERROR: requirements.txt not found!"
    exit 1
fi

echo ""
echo "Installing user-specified type hints (types-botocore, types-boto3) and checking for others with mypy..."
pip3 install types-botocore types-boto3

# Running mypy to install types for E4GL30S1NT.py
# This might download additional type stubs if mypy deems them necessary for the script.
mypy --install-types --non-interactive E4GL30S1NT.py

echo ""
echo "Dependency installation process complete."
echo "Note: If mypy reported installing new stubs, you might want to re-run static analysis or type checking on your environment."
