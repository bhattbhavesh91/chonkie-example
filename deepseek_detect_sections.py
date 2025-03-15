import re

# ------------------------------
# Table Handling (Original Logic)
# ------------------------------
def find_first_table(lines):
    for i in range(len(lines) - 1):
        if lines[i].startswith('|') and lines[i+1].startswith('|') and '---' in lines[i+1]:
            j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            return (lines[:i], lines[i], lines[i+1], lines[i:j], lines[j:])
    return None

def process_tables(chunks):
    current_table = None  # Tracks table headers/descriptions
    processed_chunks = []
    
    for chunk in chunks:
        lines = [line.strip() for line in chunk.split('\n') if line.strip()]
        if current_table and lines and lines[0].startswith('|') and not any('---' in line for line in lines[:2]):
            new_lines = current_table['description'] + [current_table['header'], current_table['separator']] + lines
            processed, current_table = _rebuild_table_content(new_lines)
            processed_chunks.append('\n'.join(processed))
        else:
            processed, current_table = _rebuild_table_content(lines)
            processed_chunks.append('\n'.join(processed))
    
    return processed_chunks

def _rebuild_table_content(lines):
    tables = []
    remaining = lines.copy()
    current_table = None
    
    while True:
        result = find_first_table(remaining)
        if not result:
            break
        desc, header, sep, body, remaining = result
        tables.append((desc, header, sep, body))
    
    processed = []
    for desc, header, sep, body in tables:
        processed.extend(desc)
        processed.append(header)
        processed.append(sep)
        processed.extend(body[2:])
    
    if tables:
        last_desc, last_header, last_sep, last_body = tables[-1]
        current_table = {'description': last_desc, 'header': last_header, 'separator': last_sep}
    else:
        current_table = None
    
    processed.extend(remaining)
    return processed, current_table

# ------------------------------
# Section Header Handling (New)
# ------------------------------
def is_list_item(line):
    return re.match(r'^(\s*[-*+]|\s*\d+\.)\s+', line) is not None

def process_sections(chunks):
    current_section = None  # Tracks {'description': [], 'is_active': bool}
    processed_chunks = []
    
    for chunk in chunks:
        lines = [line.rstrip() for line in chunk.split('\n') if line.strip()]
        
        # Check if chunk continues a previous section's list
        if current_section and lines and is_list_item(lines[0]):
            lines = current_section['description'] + lines
            current_section['is_active'] = True  # Assume continuation until proven otherwise
        else:
            current_section = None
        
        # Detect new section headers with lists
        new_section = None
        for i, line in enumerate(lines):
            if is_list_item(line):
                header_lines = [l for l in lines[:i] if i > 0 else []
                new_section = {
                    'description': header_lines,
                    'is_active': any(is_list_item(l) for l in lines[i:])
                }
                break
        
        if new_section:
            current_section = new_section
        
        processed_chunks.append('\n'.join(lines))
    
    return processed_chunks

# ------------------------------
# Combined Processing
# ------------------------------
def process_all_chunks(chunks):
    # First process tables
    table_processed = process_tables(chunks)
    # Then process section headers
    final_chunks = process_sections(table_processed)
    return final_chunks

# ------------------------------
# Example Usage
# ------------------------------
chunk1 = """### Key Features
- Monthly/quarterly interest pay-out option
- Higher interest for senior citizens
- Up to 7.90% per annum

IDFC FIRST Bank offers the best FD rates:
| Tenure | Rates... |
| --- | --- |
|7–14 days |3.00% |"""

chunk2 = """|371 days |7.50% |
|400 days |7.90% |

### Benefits (Split Across Chunks)
- Benefit 1: Flexible tenure
- Benefit 2: High liquidity"""

chunk3 = """- Benefit 3: Tax savings
- Benefit 4: Senior citizen perks"""

final_chunks = process_all_chunks([chunk1, chunk2, chunk3])
for i, chunk in enumerate(final_chunks):
    print(f"Processed Chunk {i+1}:\n{chunk}\n{'-'*50}\n")