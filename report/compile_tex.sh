#!/bin/bash

# Script to compile LaTeX document with bibliography handling
# Usage: ./compile_tex.sh filename.tex

# Check if the input filename is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 filename.tex"
    exit 1
fi

# Input file and output directory
TEXFILE=$1
OUTDIR="out"

# Check if the file exists
if [ ! -f "$TEXFILE" ]; then
    echo "Error: File '$TEXFILE' not found!"
    exit 1
fi

# Extract the base filename (without extension)
BASENAME=$(basename "$TEXFILE" .tex)

# Create output directory if it doesn't exist
mkdir -p "$OUTDIR"

# Step 1: Run pdflatex (first pass to generate .bcf)
pdflatex -interaction=nonstopmode -output-directory="$OUTDIR" "$TEXFILE"
if [ $? -ne 0 ]; then
    echo "Error: pdflatex failed on the first pass."
    exit 1
fi

# Step 2: Run biber (process bibliography)
biber "$OUTDIR/$BASENAME"
if [ $? -ne 0 ]; then
    echo "Error: biber failed to process the bibliography."
    exit 1
fi

# Step 3: Run pdflatex (second pass to include bibliography)
pdflatex -interaction=nonstopmode -output-directory="$OUTDIR" "$TEXFILE"
if [ $? -ne 0 ]; then
    echo "Error: pdflatex failed on the second pass."
    exit 1
fi

# Step 4: Run pdflatex (third pass to resolve cross-references)
pdflatex -interaction=nonstopmode -output-directory="$OUTDIR" "$TEXFILE"
if [ $? -ne 0 ]; then
    echo "Error: pdflatex failed on the third pass."
    exit 1
fi

# Step 5: Move the generated PDF to the main directory
mv "$OUTDIR/$BASENAME.pdf" .

# Step 5: Open the generated PDF automatically
xdg-open "$BASENAME.pdf" &
