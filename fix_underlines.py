#!/usr/bin/env python3
import re
import os

def fix_underlines(filename):
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find all titles without proper underlines
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line looks like a title (starts with capital letter, no underline)
        if (re.match(r'^[A-Z][A-Za-z\s]+$', line.strip()) and 
            i + 1 < len(lines) and 
            not lines[i + 1].strip().startswith('=') and
            not lines[i + 1].strip().startswith('-') and
            not lines[i + 1].strip().startswith('~')):
            
            # Add appropriate underline based on title length
            if len(line) <= 20:
                underline = '=' * len(line)
            elif len(line) <= 40:
                underline = '-' * len(line)
            else:
                underline = '~' * len(line)
            
            new_lines.append(line)
            new_lines.append(underline)
        else:
            new_lines.append(line)
        
        i += 1
    
    with open(filename, 'w') as f:
        f.write('\n'.join(new_lines))

# Fix all RST files
for filename in ['source/async_runner.rst', 'source/getting_started.rst', 'source/index.rst', 'source/api_reference.rst']:
    if os.path.exists(filename):
        print(f"Fixing {filename}")
        fix_underlines(filename) 