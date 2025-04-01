# Portfolio Scripts

This directory contains utility scripts for the portfolio website.

## obsidian_import.py

A script to import Obsidian markdown files to the content directory, handling:
- Markdown frontmatter cleanup
- Image path resolution
- LaTeX formatting fixes
- Proper handling of Obsidian-style links

Usage:
```
python scripts/obsidian_import.py SOURCE_PATH [--vault VAULT_PATH] [--image-folder IMAGE_FOLDER_PATH]
```

## fix_matrix.py

A targeted script to fix LaTeX matrix formatting in a specific markdown file:
- Handles spacing around matrices
- Formats nested matrices correctly
- Properly aligns LaTeX elements

Usage:
```
python scripts/fix_matrix.py [FILE_PATH]
```

Default file path is `content/articles/matrix/matrix.md`.

## direct_fix.py

A script to directly replace specific LaTeX matrix sections with correctly formatted versions:
- Replaces RGB matrices section
- Fixes combined RGB image representation

Usage:
```
python scripts/direct_fix.py
```

## fix_all_latex.py

A script to fix LaTeX formatting in all markdown files in the content directory:
- Scans all markdown files recursively
- Applies general LaTeX formatting fixes
- Special handling for RGB matrix formatting in matrix.md file

Usage:
```
python scripts/fix_all_latex.py
```

## LaTeX Formatting Conventions

To maintain consistent LaTeX formatting in the content:

1. Display math should have empty lines before and after:
```markdown
Text before.

$$
math content
$$

Text after.
```

2. Matrix formatting should use:
```latex
\begin{bmatrix}
value1 & value2 \\
value3 & value4
\end{bmatrix}
```

3. For matrices side-by-side with text commands, use:
```latex
\begin{bmatrix}
...
\end{bmatrix}, \quad \text{Text}
```

4. For nested matrices, keep inner matrices compact:
```latex
\begin{bmatrix}
\begin{bmatrix}
...
\end{bmatrix},
\begin{bmatrix}
...
\end{bmatrix}
\end{bmatrix}
``` 