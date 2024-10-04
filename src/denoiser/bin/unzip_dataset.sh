#!/bin/bash

# Function to unzip tar archives
function unzip_tar() {
    local input_file="$1"
    local output_dir="$2"
    tar -xf "$input_file" -C "$output_dir"
}

# Path to the dataset folder
dataset_folder="./dataset"

# Check if the dataset folder exists
if [ ! -d "$dataset_folder" ]; then
    echo "Dataset folder not found."
    exit 1
fi

# Go through the dataset folder and unzip all .tar archives
echo "Unzipping .tar archives in the dataset folder..."
for file in "$dataset_folder"/*.tar; do
    filename=$(basename "$file")
    dirname="${filename%.*}"
    output_dir="$dataset_folder/$dirname"
    mkdir -p "$output_dir"
    echo "Unzipping $filename to $output_dir..."
    unzip_tar "$file" "$output_dir"
    rm "$file"
done

echo "Unzipping completed."