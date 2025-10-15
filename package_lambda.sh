#!/bin/bash

# Create a temporary directory for packaging
mkdir -p package

# Copy the source files
cp -r src/* package/

# Create the zip file
cd package
zip -r ../lambda_function.zip .

# Clean up
cd ..
rm -rf package

echo "Lambda function packaged as lambda_function.zip"
