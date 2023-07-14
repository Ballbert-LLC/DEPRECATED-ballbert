#!/bin/bash

# Function to recursively traverse directories and run files
run_files() {
    local current_directory=$1
    local current_file=$2

    # Loop through each file in the current directory
    for file in "$current_directory"/*; do
        if [ -f "$file" ]; then
            if [[ "$file" == *.py ]]; then
                if [[ "$file" != "$current_file" && "$file" != */_* ]]; then
                    echo "Running Python file: $file"
                    if python "$file"; then
                        echo -e "\e[32mFinished running $file\e[0m"
                    else
                        echo -e "\e[31m$file: Failed\e[0m"
                    fi
                    echo ""
                fi
            elif [[ "$file" == *.sh ]]; then
                if [[ "$file" != "$current_file" && "$file" != */_* ]]; then
                    echo "Running Bash file: $file"
                    if bash "$file"; then
                        echo -e "\e[32mFinished running $file\e[0m"
                    else
                        echo -e "\e[31m$file: Failed\e[0m"
                    fi
                    echo ""
                fi
            fi
        elif [ -d "$file" ]; then
            run_files "$file" "$current_file" # Recursively call the function for subdirectories
        fi

        sleep 1 # Add a delay of 1 second between running each file
    done
}

# Specify the directory containing Python and Bash files
directory="./tests"

# Get the current script file
current_file="./tests/run.sh"

# Run files in the specified directory and its subdirectories
run_files "$directory" "$current_file"
