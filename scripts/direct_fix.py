#!/usr/bin/env python3
import re
import os
import sys

def fix_matrix_formatting(file_path):
    print(f"Fixing matrix formatting in: {file_path}")
    
    # Read the content of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find and fix matrices
    
    # First, find the RGB matrices section
    rgb_section = r"""$$
\text{R}  =
\begin{bmatrix}
255 & 128 \\
64 & 0
\end{bmatrix}, \quad
\text{G}  =
\begin{bmatrix}
0 & 64 \\
128 & 255
\end{bmatrix}, \quad
\text{B}  =
\begin{bmatrix}
128 & 255 \\
64 & 0
\end{bmatrix}
$$"""
    
    # Find the RGB matrices
    start_index = content.find("For a small  $2 \\times 2$ RGB image:")
    if start_index != -1:
        # Find the start of the RGB section
        start_block = content.find("$$", start_index)
        if start_block != -1:
            # Find the end of the RGB matrices block
            end_block = content.find("$$", start_block + 2)
            if end_block != -1:
                # Replace the entire block
                end_block += 2  # Include the closing $$
                content = content[:start_block] + rgb_section + content[end_block:]
    
    # Fix the combined RGB section
    combined_section = r"""$$
\text{Image}  =
\begin{bmatrix}
\begin{bmatrix}
255 & 128 \\
64 & 0
\end{bmatrix},
\begin{bmatrix}
0 & 64 \\
128 & 255
\end{bmatrix},
\begin{bmatrix}
128 & 255 \\
64 & 0
\end{bmatrix}
\end{bmatrix}
$$"""
    
    # Find the combined RGB section
    start_index = content.find("The combined RGB image is:")
    if start_index != -1:
        # Find the start of the combined section
        start_block = content.find("$$", start_index)
        if start_block != -1:
            # Find the end of the combined block
            end_block = content.find("$$", start_block + 2)
            if end_block != -1:
                # Replace the entire block
                end_block += 2  # Include the closing $$
                content = content[:start_block] + combined_section + content[end_block:]
    
    # Write the updated content back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Successfully fixed matrix formatting in: {file_path}")
    return True

def main():
    # Path to the matrix.md file
    matrix_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               "content", "articles", "matrix", "matrix.md")
    
    # Allow specifying a different file
    if len(sys.argv) > 1:
        matrix_file = sys.argv[1]
    
    if not os.path.exists(matrix_file):
        print(f"Error: File does not exist: {matrix_file}")
        sys.exit(1)
    
    success = fix_matrix_formatting(matrix_file)
    
    if success:
        print("LaTeX matrix formatting fixed successfully.")
    else:
        print("Failed to fix LaTeX matrix formatting.")
        sys.exit(1)

if __name__ == "__main__":
    main() 