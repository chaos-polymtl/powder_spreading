# Check if the user provided an input file
if [ -z "$1" ]; then
    echo "Usage: $0 <input_file>"
    exit 1
fi

# Input SLURM file provided as a command-line argument
input_file="$1"
# Output file to store the extracted data
output_file="$2"

# Check if input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: Input file '$input_file' not found."
    exit 1
fi

# Clear the output file if it exists
> "$output_file"
echo "time kinetic_energy" >> "$output_file"

# Extract and store the time step and average translational kinetic energy
while read -r line; do
    # Extract the line containing the transient iteration (where the time step is defined)
    if [[ $line =~ "Transient iteration" ]]; then
        # Extract the time step using regex
        time_step=$(echo "$line" | grep -oP 'Time: \K[0-9]+\.[0-9]+')
    fi
    
    # Extract the line containing the Translational kinetic energy
    if [[ $line =~ "| Translational kinetic energy" ]]; then
        # Extract the average kinetic energy using regex
        avg_kinetic_energy=$(echo "$line" | awk '{print $10}')
        
        # Write the time step and average kinetic energy to the output file
        echo "$time_step $avg_kinetic_energy" >> "$output_file"
    fi

done < "$input_file"

# Print completion message
echo "Extraction complete. Data saved to '$output_file'."
