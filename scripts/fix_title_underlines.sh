#!/bin/bash

# Fix title underlines in RST files

fix_underlines() {
    local file="$1"
    echo "Fixing underlines in $file"
    
    # Create a temporary file
    temp_file=$(mktemp)
    
    # Process the file line by line
    while IFS= read -r line; do
        echo "$line" >> "$temp_file"
        
        # Check if this line is a title underline
        if [[ "$line" =~ ^-+$ ]] || [[ "$line" =~ ^=+$ ]] || [[ "$line" =~ ^~+$ ]]; then
            # Get the previous line (title)
            prev_line=$(tail -n 2 "$temp_file" | head -n 1)
            
            # Calculate the length needed
            title_length=${#prev_line}
            
            # Create underline of correct length
            if [[ "$line" =~ ^=+$ ]]; then
                new_underline=$(printf '=%.0s' $(seq 1 $title_length))
            elif [[ "$line" =~ ^~+$ ]]; then
                new_underline=$(printf '~%.0s' $(seq 1 $title_length))
            else
                new_underline=$(printf -- '-%.0s' $(seq 1 $title_length))
            fi
            
            # Replace the last line in temp file
            sed -i '$d' "$temp_file"
            echo "$new_underline" >> "$temp_file"
        fi
    done < "$file"
    
    # Replace original file
    mv "$temp_file" "$file"
}

# Fix all RST files
for file in /home/infernus007/Projects/Personal/logicPWN/docs/source/*.rst; do
    fix_underlines "$file"
done

echo "Title underlines fixed!"
