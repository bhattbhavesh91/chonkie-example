def process_chunks(chunks):
    """
    Process markdown chunks to ensure table parts maintain their context.
    
    If a chunk contains the beginning of a table (headers), this function will
    identify the table title and headers. It will then prepend these to any
    subsequent chunks that continue the same table but lack headers.
    
    Args:
        chunks (list): List of string chunks from a markdown file
        
    Returns:
        list: Processed chunks with table headers added where needed
    """
    processed_chunks = []
    current_table_title = None
    current_table_headers = None
    table_active = False
    
    for i, chunk in enumerate(chunks):
        # Check if this chunk contains a table
        contains_pipe = "|" in chunk
        
        if contains_pipe:
            lines = chunk.split('\n')
            
            # Determine if this chunk contains a table header
            header_row = None
            separator_row = None
            has_header = False
            
            for j in range(len(lines) - 1):
                if '|' in lines[j] and j+1 < len(lines) and '|' in lines[j+1] and '---' in lines[j+1]:
                    header_row = lines[j]
                    separator_row = lines[j+1]
                    has_header = True
                    break
            
            if has_header:
                # This chunk contains a table header
                # Extract title - look for text above the table
                title_text = []
                table_start_index = -1
                
                # Find where the table starts
                for j, line in enumerate(lines):
                    if '|' in line and (j+1 < len(lines) and '|' in lines[j+1]):
                        table_start_index = j
                        break
                
                # Collect all non-empty lines above the table as potential title/description
                if table_start_index > 0:
                    for j in range(table_start_index - 1, -1, -1):
                        line = lines[j].strip()
                        if line:
                            title_text.insert(0, line)  # Insert at beginning to maintain order
                
                current_table_title = "\n".join(title_text) if title_text else None
                current_table_headers = header_row + '\n' + separator_row
                table_active = True
                processed_chunks.append(chunk)
            
            elif table_active and not has_header:
                # This chunk continues a table without headers
                # Create a new chunk with the title and headers prepended
                enhanced_chunk = ""
                
                # Add the title if available
                if current_table_title:
                    enhanced_chunk += current_table_title + "\n\n"
                
                # Add the headers
                if current_table_headers:
                    enhanced_chunk += current_table_headers + "\n"
                
                # Add the original chunk content
                enhanced_chunk += chunk
                
                processed_chunks.append(enhanced_chunk)
            
            else:
                # This is either a new table without a proper header pattern,
                # or not a table at all (just contains pipe characters)
                processed_chunks.append(chunk)
        
        else:
            # This chunk doesn't contain pipe characters, so it's not part of a table
            table_active = False
            current_table_headers = None
            current_table_title = None
            processed_chunks.append(chunk)
    
    return processed_chunks