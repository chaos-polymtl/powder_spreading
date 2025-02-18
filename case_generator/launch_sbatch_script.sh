#!/bin/bash

# Assuming you are currently in the parent directory containing all the folders you want to search in.

# Iterate through each folder in the current directory
for folder in ./*/; do
    if [ -d "$folder" ]; then
        # Check if there are any files in the folder
        if [ -n "$(find "$folder" -maxdepth 1 -type f)" ]; then
            # Check if there are any .sh files in the folder
            sh_files=("$folder"*.sh)
            
            if [ ${#sh_files[@]} -gt 0 ]; then
                # Change into the folder and run sbatch for each .sh file
                echo "$sh_files" 
                (cd "$folder" && sbatch *.sh)
            fi
        else
            echo "Empty folder"
        fi
    fi
done

