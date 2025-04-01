#!/usr/bin/env python3
import os
import sys
import re
import shutil
import yaml
from pathlib import Path
from datetime import datetime
import argparse
import glob

def slugify(text):
    """Convert text to a URL-friendly slug format."""
    # Remove non-alphanumeric characters and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug

def clean_metadata(frontmatter, filename):
    """Clean and standardize the frontmatter for the project."""
    # Create a standard frontmatter with required fields
    clean_fm = {}
    
    # Set title from original or filename
    if 'title' in frontmatter and frontmatter['title']:
        clean_fm['title'] = frontmatter['title']
    else:
        # Use filename as title if not provided
        name_without_ext = os.path.splitext(filename)[0]
        clean_fm['title'] = name_without_ext.replace('-', ' ').replace('_', ' ').title()
    
    # Set date or use current - ensure ISO format YYYY-MM-DD
    if 'date' in frontmatter and frontmatter['date']:
        date_value = frontmatter['date']
        try:
            # Try to parse the date if it's a string
            if isinstance(date_value, str):
                # Check for common date formats
                date_formats = [
                    '%d-%m-%Y',  # DD-MM-YYYY
                    '%m-%d-%Y',  # MM-DD-YYYY
                    '%Y-%m-%d',  # YYYY-MM-DD (ISO)
                    '%d/%m/%Y',  # DD/MM/YYYY
                    '%m/%d/%Y',  # MM/DD/YYYY
                    '%Y/%m/%d',  # YYYY/MM/DD
                    '%B %d, %Y'  # Month DD, YYYY
                ]
                
                parsed_date = None
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    clean_fm['date'] = parsed_date.strftime('%Y-%m-%d')
                    print(f"Converted date from '{date_value}' to ISO format: {clean_fm['date']}")
                else:
                    # Fallback to current date
                    print(f"Warning: Could not parse date '{date_value}', using current date")
                    clean_fm['date'] = datetime.now().strftime('%Y-%m-%d')
            elif isinstance(date_value, datetime):
                # Already a datetime object
                clean_fm['date'] = date_value.strftime('%Y-%m-%d')
            else:
                # Unknown format, use current date
                print(f"Warning: Unsupported date format: {type(date_value)}, using current date")
                clean_fm['date'] = datetime.now().strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Error processing date: {e}. Using current date.")
            clean_fm['date'] = datetime.now().strftime('%Y-%m-%d')
    else:
        clean_fm['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Handle tags
    if 'tags' in frontmatter and frontmatter['tags']:
        # Ensure tags are in list format
        if isinstance(frontmatter['tags'], str):
            tags = [tag.strip() for tag in frontmatter['tags'].split(',')]
        else:
            tags = frontmatter['tags']
        # Filter out empty tags
        tags = [tag for tag in tags if tag]
        if tags:
            clean_fm['tags'] = tags
    
    # Include description if available
    if 'description' in frontmatter and frontmatter['description']:
        clean_fm['description'] = frontmatter['description']
    else:
        clean_fm['description'] = f"Article about {clean_fm['title']}"
    
    # Add layout - make sure this layout exists in your project
    clean_fm['layout'] = 'layouts/post.njk'
    
    return clean_fm

def fix_latex(content):
    """Fix LaTeX formatting in the content."""
    fixed_content = content
    
    # 1. First, ensure display math has proper newlines before and after
    fixed_content = re.sub(r'([^\n])\n\$\$', r'\1\n\n$$', fixed_content)
    fixed_content = re.sub(r'\$\$\n([^\n])', r'$$\n\n\1', fixed_content)
    fixed_content = re.sub(r'\$\$\s*\n\s*\n', r'$$\n', fixed_content)
    fixed_content = re.sub(r'\n\s*\n\s*\$\$', r'\n$$', fixed_content)
    
    # 2. Fix textcmd spacing - remove newlines after text commands
    fixed_content = re.sub(r'\\text{([^}]+)}\s*\n+', r'\\text{\1} ', fixed_content)
    
    # 3. Fix spacing around \quad commands - keep them on the same line
    fixed_content = re.sub(r',\s*\\quad\s*\n+', r', \\quad ', fixed_content)
    
    # 4. Fix nested matrix formatting - keep inner matrices compact
    fixed_content = re.sub(r'\\begin{bmatrix}\s*\n+\\begin{bmatrix}', r'\\begin{bmatrix}\n\\begin{bmatrix}', fixed_content)
    fixed_content = re.sub(r'\\end{bmatrix}\s*,\s*\n+', r'\\end{bmatrix}, ', fixed_content)
    
    # 5. Special handling for matrix environments
    # Find all display math blocks
    math_blocks = re.findall(r'\$\$(.*?)\$\$', fixed_content, re.DOTALL)
    
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
            fixed_content = fixed_content.replace(f'$${block}$$', f'$$\n{cleaned_block.strip()}\n$$')
    
    # 6. Post-process known problematic patterns for matrices
    
    # Pattern for side-by-side matrices with \quad
    # Fix cases where we have multiple matrices separated by \quad
    quad_pattern = re.compile(r'(\\begin{[a-z]*matrix}.*?\\end{[a-z]*matrix}),\s*\\quad\s*\\text', re.DOTALL)
    fixed_content = re.sub(quad_pattern, r'\1, \\quad \\text', fixed_content)
    
    # Pattern for nested matrices
    # Fix cases where we have matrices within matrices with commas between them
    nested_pattern = re.compile(r'(\\end{[a-z]*matrix}),\s*\n+\\begin', re.DOTALL)
    fixed_content = re.sub(nested_pattern, r'\1,\n\\begin', fixed_content)
    
    return fixed_content

def fix_obsidian_links(content, vault_path):
    """Convert Obsidian wiki links to regular markdown links where appropriate."""
    # Process [[wiki-links]] to standard markdown links or remove as needed
    def replace_wiki_link(match):
        link_text = match.group(1)
        alias_part = None
        
        # Check if link has an alias [[link|alias]]
        if '|' in link_text:
            link_text, alias_part = link_text.split('|', 1)
        
        # If no alias, use the link text itself
        display_text = alias_part if alias_part else link_text
        
        # We're removing internal links, just keep the display text
        return display_text
    
    # Replace wiki links
    content = re.sub(r'\[\[([^\]]+)\]\]', replace_wiki_link, content)
    
    return content

def find_all_images(vault_path, fallback_search_paths=None):
    """Find all image files in the vault and create a mapping for easy lookup."""
    image_map = {}
    search_paths = []
    
    # Add common Obsidian paths where pasted images are stored
    if vault_path:
        # Try standard Obsidian attachment folders
        search_paths.extend([
            vault_path,  # Root of the vault
            os.path.join(vault_path, 'attachments'),
            os.path.join(vault_path, '.obsidian/attachments'),  # Hidden Obsidian folder
            os.path.join(vault_path, 'assets'),
            os.path.join(vault_path, 'images'),
            os.path.join(vault_path, '_resources'),  # Another common location
            os.path.join(vault_path, 'resources'),
        ])
    
    # Add any additional fallback paths
    if fallback_search_paths:
        search_paths.extend(fallback_search_paths)
    
    # Add paths specifically for AI/Mathematics directory and its parent folders
    if vault_path:
        # Try to find the AI/Mathematics folder and check there
        ai_math_path = os.path.join(vault_path, 'AI', 'Mathematics')
        if os.path.exists(ai_math_path):
            search_paths.extend([
                ai_math_path,
                os.path.join(ai_math_path, 'attachments'),
                os.path.join(ai_math_path, 'images'),
            ])
        
        # Also check the AI folder
        ai_path = os.path.join(vault_path, 'AI')
        if os.path.exists(ai_path):
            search_paths.extend([
                ai_path,
                os.path.join(ai_path, 'attachments'),
                os.path.join(ai_path, 'images'),
            ])
    
    print(f"Searching for images in the following locations:")
    for path in search_paths:
        if os.path.exists(path):
            print(f"  - {path}")
    
    # Common image extensions
    extensions = ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']
    
    for path in search_paths:
        if not path or not os.path.exists(path):
            continue
            
        for ext in extensions:
            # Use recursive glob to find all images
            for img_path in glob.glob(f"{path}/**/*.{ext}", recursive=True):
                img_name = os.path.basename(img_path)
                image_map[img_name] = img_path
                # Also store by full path relative to vault
                if vault_path and img_path.startswith(vault_path):
                    rel_path = os.path.relpath(img_path, vault_path)
                    image_map[rel_path] = img_path
    
    # Print found images (limit to 10 for brevity)
    found_images = list(image_map.keys())
    if found_images:
        print(f"Found {len(found_images)} images. First 10:")
        for img in found_images[:10]:
            print(f"  - {img} -> {image_map[img]}")
    else:
        print("No images found.")
    
    return image_map

def process_images(content, source_file_path, target_dir, vault_path, additional_image_paths=None):
    """Find and copy images referenced in the content, updating references."""
    source_dir = os.path.dirname(source_file_path)
    image_dir = os.path.join(target_dir, 'images')
    os.makedirs(image_dir, exist_ok=True)
    
    # Extract all image references from the content for better debugging
    obsidian_image_pattern = r'!\[\[(.*?)\]\]'
    markdown_image_pattern = r'!\[(.*?)\]\((.*?)\)'
    
    obsidian_images = re.findall(obsidian_image_pattern, content)
    markdown_images = re.findall(markdown_image_pattern, content)
    
    print(f"Found {len(obsidian_images)} Obsidian-style image references and {len(markdown_images)} Markdown-style image references")
    print("Obsidian image references:")
    for img in obsidian_images:
        print(f"  - ![[{img}]]")
    
    # Find all images in the vault for easier reference
    fallback_paths = [source_dir]
    if vault_path:
        # Add common Obsidian attachment folders as fallbacks
        fallback_paths.extend([
            os.path.join(os.path.dirname(source_file_path), 'attachments'),
            os.path.join(os.path.dirname(source_file_path), 'assets'),
            os.path.join(os.path.dirname(source_file_path), 'images'),
            # Add parent folders as well
            os.path.dirname(os.path.dirname(source_file_path)),
            os.path.join(os.path.dirname(os.path.dirname(source_file_path)), 'attachments'),
            os.path.join(os.path.dirname(os.path.dirname(source_file_path)), 'images'),
        ])
    
    # Add any additional image paths provided
    if additional_image_paths:
        fallback_paths.extend(additional_image_paths)
    
    image_map = find_all_images(vault_path, fallback_paths)
    
    # Function to process each image reference
    def process_image_link(alt_text, image_path):
        if not image_path:
            return f"![{alt_text}](image-not-found)"
            
        full_image_path = None
        
        # Normalize path (handle both / and \ path separators)
        image_path = image_path.replace('\\', '/')
        
        # Try to find the image using various methods
        if os.path.isabs(image_path) and os.path.exists(image_path):
            # Absolute path that exists
            full_image_path = image_path
        elif os.path.exists(os.path.join(source_dir, image_path)):
            # Relative to source note
            full_image_path = os.path.join(source_dir, image_path)
        elif image_path in image_map:
            # Found in our image map
            full_image_path = image_map[image_path]
        elif os.path.basename(image_path) in image_map:
            # Try just the filename
            full_image_path = image_map[os.path.basename(image_path)]
        
        if full_image_path and os.path.exists(full_image_path):
            # Copy the image to the target directory
            image_filename = os.path.basename(full_image_path)
            target_image_path = os.path.join(image_dir, image_filename)
            print(f"Copying image: {full_image_path} -> {target_image_path}")
            shutil.copy2(full_image_path, target_image_path)
            
            # Update the reference to point to the new location
            return f"![{alt_text}](/articles/{os.path.basename(target_dir)}/images/{image_filename})"
        else:
            print(f"Warning: Image not found: {image_path}")
            print(f"  - Searched in image map with {len(image_map)} entries")
            print(f"  - Tried direct path: {os.path.join(source_dir, image_path)}")
            # Keep the original link but mark it as not found
            return f"![{alt_text}](image-not-found-{os.path.basename(image_path)})"
    
    # Process markdown image syntax: ![alt text](path/to/image)
    def replace_md_image(match):
        alt_text = match.group(1) or ""
        image_path = match.group(2)
        return process_image_link(alt_text, image_path)
    
    content = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_md_image, content)
    
    # Process obsidian image syntax: ![[image.jpg]]
    def replace_obsidian_image(match):
        image_path = match.group(1)
        alt_text = ""
        
        # Check if image has an alias ![[image.jpg|alt text]]
        if '|' in image_path:
            image_path, alt_text = image_path.split('|', 1)
        
        return process_image_link(alt_text, image_path)
    
    content = re.sub(r'!\[\[(.*?)\]\]', replace_obsidian_image, content)
    
    return content

def fix_markdown_issues(content):
    """Fix common markdown issues that might cause 11ty problems."""
    # Fix code blocks that don't have blank lines before them
    content = re.sub(r'([^\n])\n```', r'\1\n\n```', content)
    content = re.sub(r'```\n([^\n])', r'```\n\n\1', content)
    
    # Fix headers that don't have blank lines before them
    content = re.sub(r'([^\n])\n(#{1,6} )', r'\1\n\n\2', content)
    
    # Fix lists that don't have proper spacing
    content = re.sub(r'([^\n])\n(- |\* |[0-9]+\. )', r'\1\n\n\2', content)
    
    # Fix HTML tags that might confuse the parser
    content = re.sub(r'<([a-zA-Z]+)[^>]*>(?!</\1>)', lambda m: f'&lt;{m.group(1)}&gt;', content)
    
    return content

def import_obsidian_file(source_path, target_base_dir, vault_path=None, additional_image_paths=None):
    """Import an Obsidian note to the target project."""
    source_path = os.path.expanduser(source_path)
    
    if not os.path.exists(source_path):
        print(f"Error: Source file does not exist: {source_path}")
        return False
    
    print(f"Processing: {source_path}")
    
    # Read the source file
    try:
        with open(source_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        try:
            # Try with a different encoding if utf-8 fails
            with open(source_path, 'r', encoding='latin1') as file:
                content = file.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    # Extract filename and create slug
    filename = os.path.basename(source_path)
    name_without_ext = os.path.splitext(filename)[0]
    slug = slugify(name_without_ext)
    
    # Create target directory
    target_dir = os.path.join(target_base_dir, slug)
    os.makedirs(target_dir, exist_ok=True)
    
    # Extract frontmatter if it exists
    frontmatter = {}
    content_without_fm = content
    
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if fm_match:
        try:
            frontmatter = yaml.safe_load(fm_match.group(1))
            content_without_fm = fm_match.group(2)
        except yaml.YAMLError as e:
            print(f"Warning: Error parsing frontmatter: {e}")
    
    # Clean the frontmatter
    clean_fm = clean_metadata(frontmatter, filename)
    
    # Process and copy images - do this first to find all images
    content_without_fm = process_images(content_without_fm, source_path, target_dir, vault_path, additional_image_paths)
    
    # Fix LaTeX formatting
    content_without_fm = fix_latex(content_without_fm)
    
    # Process Obsidian links
    content_without_fm = fix_obsidian_links(content_without_fm, vault_path)
    
    # Fix any markdown issues that might cause 11ty problems
    content_without_fm = fix_markdown_issues(content_without_fm)
    
    # Create the new content with clean frontmatter
    new_content = "---\n"
    new_content += yaml.dump(clean_fm, default_flow_style=False, allow_unicode=True)
    new_content += "---\n\n"
    new_content += content_without_fm
    
    # Write the processed content to the target file
    target_file_path = os.path.join(target_dir, f"{slug}.md")
    with open(target_file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print(f"Successfully imported: {source_path} -> {target_file_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Import Obsidian notes to your project.')
    parser.add_argument('source_path', help='Path to the Obsidian markdown file')
    parser.add_argument('--vault', help='Path to the Obsidian vault (for resolving links)', default=None)
    parser.add_argument('--image-folder', help='Specific path to look for images (especially pasted images)', default=None)
    
    args = parser.parse_args()
    
    # Determine the project root and target directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    target_base_dir = os.path.join(project_root, "content", "articles")
    
    # Create the target base directory if it doesn't exist
    os.makedirs(target_base_dir, exist_ok=True)
    
    print(f"Importing from: {args.source_path}")
    print(f"Using vault path: {args.vault}")
    if args.image_folder:
        print(f"Using specific image folder: {args.image_folder}")
    print(f"Target directory: {target_base_dir}")
    
    # If image folder is specified, check if it exists
    if args.image_folder and not os.path.exists(args.image_folder):
        print(f"Warning: Specified image folder does not exist: {args.image_folder}")
    
    # Add image folder to search paths
    additional_paths = []
    if args.image_folder:
        additional_paths.append(args.image_folder)
    
    # Import the file with additional image paths
    success = import_obsidian_file(args.source_path, target_base_dir, args.vault, additional_image_paths=additional_paths)
    
    if success:
        print("Import completed successfully.")
    else:
        print("Import failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 