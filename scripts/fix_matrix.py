#!/usr/bin/env python3
import re
import os
import sys

def fix_matrix_file(filepath):
    """Specifically fixes LaTeX matrix formatting in the matrix.md file."""
    print(f"Fixing LaTeX matrices in: {filepath}")
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Manually fix the problematic RGB matrices section
    rgb_matches = re.search(r'\$\$\s*\\text{R}\s*=.*?\\end{bmatrix}\s*\n\$\$', content, re.DOTALL)
    if rgb_matches:
        # Replace with the correctly formatted string
        rgb_section = """$$
\\text{R}  =
\\begin{bmatrix}
255 & 128 \\\\
64 & 0
\\end{bmatrix}, \\quad
\\text{G}  =
\\begin{bmatrix}
0 & 64 \\\\
128 & 255
\\end{bmatrix}, \\quad
\\text{B}  =
\\begin{bmatrix}
128 & 255 \\\\
64 & 0
\\end{bmatrix}
$$"""
        content = content.replace(rgb_matches.group(0), rgb_section)
    
    # 2. Manually fix the combined RGB image section
    img_matches = re.search(r'\$\$\s*\\text{Image}\s*=.*?\\end{bmatrix}\s*\n\$\$', content, re.DOTALL)
    if img_matches:
        # Replace with the correctly formatted string
        combined_section = """$$
\\text{Image}  =
\\begin{bmatrix}
\\begin{bmatrix}
255 & 128 \\\\
64 & 0
\\end{bmatrix},
\\begin{bmatrix}
0 & 64 \\\\
128 & 255
\\end{bmatrix},
\\begin{bmatrix}
128 & 255 \\\\
64 & 0
\\end{bmatrix}
\\end{bmatrix}
$$"""
        content = content.replace(img_matches.group(0), combined_section)
    
    # 3. Fix any remaining individual matrices
    matrix_pattern = re.compile(r'(\\begin{[a-z]*matrix})(.*?)(\\end{[a-z]*matrix})', re.DOTALL)
    
    def format_matrix(match):
        begin_tag = match.group(1)
        matrix_content = match.group(2)
        end_tag = match.group(3)
        
        # Clean the matrix content
        matrix_content = clean_matrix_content(matrix_content)
        
        return f"{begin_tag}\n{matrix_content}\n{end_tag}"
    
    content = matrix_pattern.sub(format_matrix, content)
    
    # Write the fixed content back to the file
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Successfully fixed: {filepath}")
    return True

def clean_matrix_content(content):
    """Helper function to clean matrix content."""
    content = content.strip()
    
    # Format rows properly
    if '\\\\' in content:
        rows = [row.strip() for row in content.split('\\\\')]
        # Filter out empty rows
        rows = [row for row in rows if row.strip()]
        # Join with proper formatting
        return ' \\\\\n'.join(rows)
    else:
        # If no row separators, just clean up the spacing
        return content

def main():
    # Default path to the matrix.md file
    matrix_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "content", "articles", "matrix", "matrix.md")
    
    # Allow specifying a different file
    if len(sys.argv) > 1:
        matrix_file = sys.argv[1]
    
    if not os.path.exists(matrix_file):
        print(f"Error: File does not exist: {matrix_file}")
        sys.exit(1)
    
    success = fix_matrix_file(matrix_file)
    
    if success:
        print("LaTeX matrix formatting fixed successfully.")
    else:
        print("Failed to fix LaTeX matrix formatting.")
        sys.exit(1)

if __name__ == "__main__":
    main() 