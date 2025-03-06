def find_first_table(lines):
    for i in range(len(lines) - 1):
        if lines[i].startswith('|') and lines[i+1].startswith('|') and '---' in lines[i+1]:
            # Found potential header and separator
            header_line = lines[i]
            separator_line = lines[i+1]
            # Find the end of the table
            j = i + 2
            while j < len(lines) and lines[j].startswith('|'):
                j += 1
            table_body = lines[i:j]
            description_lines = lines[:i]
            remaining_lines = lines[j:]
            return (description_lines, header_line, separator_line, table_body, remaining_lines)
    return None

def process_chunks(chunks):
    current_table = None  # Holds 'description', 'header', 'separator' of the last table
    processed_chunks = []
    
    for chunk in chunks:
        lines = [line.strip() for line in chunk.split('\n') if line.strip() != '']
        
        # Check if this chunk is a continuation of the previous table
        if current_table and lines and lines[0].startswith('|') and not any('---' in line for line in lines[:2]):
            # Prepend the previous table's description, header, and separator
            new_lines = current_table['description'] + [current_table['header'], current_table['separator']] + lines
            tables = []
            remaining = new_lines
            while True:
                result = find_first_table(remaining)
                if not result:
                    break
                desc, header, sep, body, remaining = result
                tables.append((desc, header, sep, body))
            
            # Rebuild the processed lines
            processed_lines = []
            for desc, header, sep, body in tables:
                processed_lines.extend(desc)
                processed_lines.append(header)
                processed_lines.append(sep)
                processed_lines.extend(body[2:])  # Skip header and separator as they are already added
            processed_lines.extend(remaining)
            
            # Update current_table with the last table in this chunk
            if tables:
                last_desc, last_header, last_sep, last_body = tables[-1]
                current_table = {
                    'description': last_desc,
                    'header': last_header,
                    'separator': last_sep
                }
            else:
                current_table = None
            
            processed_chunks.append('\n'.join(processed_lines))
        else:
            # Process the chunk normally
            tables = []
            remaining = lines
            while True:
                result = find_first_table(remaining)
                if not result:
                    break
                desc, header, sep, body, remaining = result
                tables.append((desc, header, sep, body))
            
            # Rebuild the processed lines
            processed_lines = []
            for desc, header, sep, body in tables:
                processed_lines.extend(desc)
                processed_lines.append(header)
                processed_lines.append(sep)
                processed_lines.extend(body[2:])  # Skip header and separator
            processed_lines.extend(remaining)
            
            # Update current_table with the last table in this chunk
            if tables:
                last_desc, last_header, last_sep, last_body = tables[-1]
                current_table = {
                    'description': last_desc,
                    'header': last_header,
                    'separator': last_sep
                }
            else:
                current_table = None
            
            processed_chunks.append('\n'.join(processed_lines))
    
    return processed_chunks