#!/bin/bash

# Define the directory to start from
dir=/$INVENIO_RECORD_IMPORTER_LOCAL_DATA_DIR/"humcore"

# Use find to get all files with quote characters in their names
# find "$dir" -type f -name "*[“”‘’]*"

# Use find to get all files, and then rename them
find "$dir" -type f -name "*[“”‘’]*" -print0 | while IFS= read -r -d '' file; do
    echo $file
    newname=$(echo "$file" | sed "s/[“”‘’]//g")
    if [ "$file" != "$newname" ]; then
        mv "$file" "$newname"
    fi
    echo $newname
done
