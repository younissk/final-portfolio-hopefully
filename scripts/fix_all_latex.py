#!/usr/bin/env python3
import os
import re
import sys
import glob
from pathlib import Path

def clean_matrix_content(content):
    """Clean and format matrix content properly."""
    # Remove excess whitespace and format rows
    rows = [row.strip() for row in content.split('\\\\')]
    # Filter out empty rows
    rows = [row for row in rows if row.strip()]
    # Join with proper formatting
    return ' \\\\\n'.join(rows)

def fix_matrix_formatting(file_path):
    """Fix LaTeX matrix formatting in a markdown file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin1') as file:
                content = file.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return False

    original_content = content
    
    # Check for matrix content to avoid unnecessary processing
    if "\\begin{matrix}" not in content and "\\begin{bmatrix}" not in content and "\\begin{pmatrix}" not in content:
        print(f"No LaTeX matrices found in: {file_path}")
        return True
    
    # Fix LaTeX formatting using regex patterns
    
    # 1. First, ensure display math has proper newlines before and after
    content = re.sub(r'([^\n])\n\$\$', r'\1\n\n$$', content)
    content = re.sub(r'\$\$\n([^\n])', r'$$\n\n\1', content)
    content = re.sub(r'\$\$\s*\n\s*\n', r'$$\n', content)
    content = re.sub(r'\n\s*\n\s*\$\$', r'\n$$', content)
    
    # 2. Fix textcmd spacing - remove newlines after text commands
    content = re.sub(r'\\text{([^}]+)}\s*\n+', r'\\text{\1} ', content)
    
    # 3. Fix spacing around \quad commands - keep them on the same line
    content = re.sub(r',\s*\\quad\s*\n+', r', \\quad ', content)
    
    # 4. Fix nested matrix formatting - keep inner matrices compact
    content = re.sub(r'\\begin{bmatrix}\s*\n+\\begin{bmatrix}', r'\\begin{bmatrix}\n\\begin{bmatrix}', content)
    content = re.sub(r'\\end{bmatrix}\s*,\s*\n+', r'\\end{bmatrix}, ', content)
    
    # 5. Special handling for matrix environments
    # Find all display math blocks
    math_blocks = re.findall(r'\$\$(.*?)\$\$', content, re.DOTALL)
    
    for block in math_blocks:
        cleaned_block = block
        
        # Check if this block contains a matrix environment
        if '\\begin{bmatrix}' in block or '\\begin{matrix}' in block or '\\begin{pmatrix}' in block:
            # Process all matrix environments in this block
            matrix_pattern = re.compile(r'(\\begin{[a-z]*matrix})(.*?)(\\end{[a-z]*matrix})', re.DOTALL)
            
            def format_matrix(m):
                begin_tag = m.group(1)
                matrix_content = m.group(2).strip()
                end_tag = m.group(3)
                
                # Format rows properly
                if '\\\\' in matrix_content:
                    rows = [row.strip() for row in matrix_content.split('\\\\')]
                    # Filter out empty rows
                    rows = [row for row in rows if row.strip()]
                    # Join with proper formatting
                    formatted_content = ' \\\\\n'.join(rows)
                    return f"{begin_tag}\n{formatted_content}\n{end_tag}"
                else:
                    # If no row separators, just clean up the spacing
                    return f"{begin_tag}\n{matrix_content}\n{end_tag}"
            
            cleaned_block = matrix_pattern.sub(format_matrix, cleaned_block)
            
            # Replace the original block with the cleaned version
            content = content.replace(f'$${block}$$', f'$$\n{cleaned_block.strip()}\n$$')
    
    # 6. Post-process known problematic patterns for matrices
    
    # Pattern for side-by-side matrices with \quad
    # Fix cases where we have multiple matrices separated by \quad
    quad_pattern = re.compile(r'(\\begin{[a-z]*matrix}.*?\\end{[a-z]*matrix}),\s*\\quad\s*\\text', re.DOTALL)
    content = re.sub(quad_pattern, r'\1, \\quad \\text', content)
    
    # Pattern for nested matrices
    # Fix cases where we have matrices within matrices with commas between them
    nested_pattern = re.compile(r'(\\end{[a-z]*matrix}),\s*\n+\\begin', re.DOTALL)
    content = re.sub(nested_pattern, r'\1,\n\\begin', content)
    
    # 7. Special case for specific matrix files
    # Check if this is the matrix file we need to fix
    if "matrix.md" in str(file_path) and "RGB image" in content:
        # Check and fix the RGB matrices section
        if "combined RGB image" in content:
            print(f"Found RGB matrices section in {file_path}, applying direct fix...")
            
            # Use string replacement instead of regex for the complex section
            rgb_fix_content = """For a small $2 \\times 2$ RGB image, we would have:

$$
\\text{R} = 
\\begin{bmatrix}
255 & 128 \\\\
64 & 0
\\end{bmatrix}, \\quad \\text{G} = 
\\begin{bmatrix}
0 & 64 \\\\
128 & 255
\\end{bmatrix}, \\quad \\text{B} = 
\\begin{bmatrix}
128 & 255 \\\\
64 & 0
\\end{bmatrix}
$$

The combined RGB image would be represented by combining these matrices:

$$
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
            
            # Find the start of the RGB section
            rgb_start = content.find("For a small")
            if rgb_start != -1:
                # Find the end of the section after "combined RGB image"
                combined_pos = content.find("combined RGB image")
                if combined_pos != -1:
                    # Find the next $$ after "combined RGB image"
                    rgb_end = content.find("$$", combined_pos)
                    if rgb_end != -1:
                        # Find the end of the matrix block
                        matrix_end = content.find("$$", rgb_end + 2)
                        if matrix_end != -1:
                            # Add a bit more to make sure we get the closing $$
                            matrix_end += 2
                            # Replace the section
                            content = content[:rgb_start] + rgb_fix_content + content[matrix_end:]
                            print(f"Successfully replaced RGB matrix section in {file_path}")
                        else:
                            print(f"Warning: Could not find end of matrix block in {file_path}")
                    else:
                        print(f"Warning: Could not find $$ after 'combined RGB image' in {file_path}")
                else:
                    print(f"Warning: Could not find 'combined RGB image' in {file_path}")
            else:
                print(f"Warning: Could not find start of RGB section in {file_path}")
    
    # Only write to file if content changed
    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Successfully fixed: {file_path}")
            return True
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            return False
    else:
        print(f"No changes needed for: {file_path}")
        return True

def main():
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define the content directory
    content_dir = os.path.join(project_root, "content")
    
    # Check if the content directory exists
    if not os.path.exists(content_dir):
        print(f"Error: Content directory not found: {content_dir}")
        return 1
    
    # Find all markdown files in the content directory
    md_files = []
    for extension in ['md', 'markdown']:
        md_files.extend(list(Path(content_dir).glob(f'**/*.{extension}')))
    
    if not md_files:
        print("No markdown files found in the content directory.")
        return 0
    
    print(f"Found {len(md_files)} markdown files to process.")
    
    # Process each markdown file
    success_count = 0
    failure_count = 0
    
    for file_path in md_files:
        print(f"Processing: {file_path}")
        if fix_matrix_formatting(file_path):
            success_count += 1
        else:
            failure_count += 1
    
    # Report results
    print(f"\nResults: Successfully processed {success_count} files. Failed: {failure_count}.")
    
    if failure_count > 0:
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main()) 