#!/bin/bash
# Fix only the MOST obvious tokenization artifacts - single letter fragments
# These are patterns like "M OR E" -> "MORE", "SC OR E" -> "SCORE"

find basic/ -name "*.bas" -type f | while read file; do
    # Only process text files
    if file "$file" | grep -q "text"; then
        # Fix patterns with single-letter fragments
        sed -i 's/"M OR E"/"MORE"/g' "$file"
        sed -i 's/"SC OR E"/"SCORE"/g' "$file"
        sed -i 's/"SC OR ED"/"SCORED"/g' "$file"
        sed -i 's/"SC OR ES"/"SCORES"/g' "$file"
        sed -i 's/"ST OR E"/"STORE"/g' "$file"
        sed -i 's/"C AND Y"/"CANDY"/g' "$file"
        sed -i 's/"T OR EAD"/"TOREAD"/g' "$file"
        sed -i 's/"ESC OR T"/"ESCORT"/g' "$file"
        sed -i 's/THE FOR M/THE FORM/g' "$file"
        sed -i 's/STR AND ED/STRANDED/g' "$file"
        sed -i 's/NEVERM OR E/NEVERMORE/g' "$file"
        sed -i 's/\.\.\.EVERM OR E/.\.\.EVERMORE/g' "$file"
        sed -i 's/NOTHING M OR E/NOTHING MORE/g' "$file"
    fi
done

echo "Fixed obvious tokenization artifacts"
