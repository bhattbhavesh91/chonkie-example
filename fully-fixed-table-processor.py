def process_chunks(chunks):
    """
    Process markdown chunks to ensure table parts maintain their context.
    
    This function identifies tables in markdown chunks, extracts their headers and titles,
    and adds these elements to subsequent chunks that continue the same table.
    
    The function can handle:
    - Multiple tables in the same chunk
    - Tables split across chunks
    - Different table formats and styles
    
    Args:
        chunks (list): List of string chunks from a markdown file
        
    Returns:
        list: Processed chunks with table headers added where needed
    """
    processed_chunks = []
    tables_info = []  # List to store info about active tables
    
    for i, chunk in enumerate(chunks):
        lines = chunk.split('\n')
        chunk_has_table_start = False
        new_tables_found = []
        
        # First pass: identify all tables that start in this chunk
        for j in range(len(lines) - 1):
            # Check for a table header pattern: a line with | followed by a line with | and ---
            if '|' in lines[j] and j+1 < len(lines) and '|' in lines[j+1] and '---' in lines[j+1]:
                # Found a new table header
                header_row = lines[j]
                separator_row = lines[j+1]
                chunk_has_table_start = True
                
                # Find title by looking at text before this table
                title_lines = []
                for k in range(j-1, -1, -1):
                    line = lines[k].strip()
                    if not line:
                        # Stop at empty line (likely separates title from previous content)
                        if title_lines:  # Only break if we've already found title lines
                            break
                    elif '|' in line and ('---' in line or '===' in line):
                        # This is part of a previous table
                        break
                    else:
                        # This is likely part of the title/description
                        title_lines.insert(0, lines[k])
                
                # Look for the end of this table (to know where to search for the next table)
                table_end_index = j + 2  # Start after header and separator
                while table_end_index < len(lines):
                    if not lines[table_end_index].strip() or not '|' in lines[table_end_index]:
                        break
                    table_end_index += 1
                
                # Store this table's information
                table_info = {
                    'title': '\n'.join(title_lines) if title_lines else None,
                    'header': header_row,
                    'separator': separator_row,
                    'start_index': j,
                    'end_index': table_end_index - 1,
                    'last_data_line': lines[table_end_index - 1] if table_end_index > 0 and table_end_index <= len(lines) else ""
                }
                new_tables_found.append(table_info)
                
                # Continue searching from after this table
                j = table_end_index
        
        # If this chunk starts new tables, add them to our tracking list
        if new_tables_found:
            tables_info = new_tables_found
        
        # Check if this chunk continues a table from previous chunk
        if not chunk_has_table_start and i > 0 and tables_info and '|' in chunk:
            first_line = lines[0].strip() if lines else ""
            
            # This chunk likely continues a table if it starts with a line containing |
            if first_line and '|' in first_line and not '---' in first_line:
                # Find where the table continuation ends (if there are multiple tables in this chunk)
                table_end_index = 0
                while table_end_index < len(lines):
                    if not lines[table_end_index].strip() or not '|' in lines[table_end_index]:
                        break
                    table_end_index += 1
                
                # Check if there are new tables after this continuation
                new_tables_after_continuation = []
                for j in range(table_end_index, len(lines) - 1):
                    if '|' in lines[j] and j+1 < len(lines) and '|' in lines[j+1] and '---' in lines[j+1]:
                        # Another table starts after this continuation
                        header_row = lines[j]
                        separator_row = lines[j+1]
                        
                        # Find title for this new table
                        title_lines = []
                        for k in range(j-1, table_end_index, -1):
                            line = lines[k].strip()
                            if not line:
                                if title_lines:  # Only break if we've already found title lines
                                    break
                            elif '|' in line and ('---' in line or '===' in line):
                                break
                            else:
                                title_lines.insert(0, lines[k])
                        
                        # Find end of this new table
                        new_table_end = j + 2
                        while new_table_end < len(lines):
                            if not lines[new_table_end].strip() or not '|' in lines[new_table_end]:
                                break
                            new_table_end += 1
                        
                        # Store this new table's information
                        table_info = {
                            'title': '\n'.join(title_lines) if title_lines else None,
                            'header': header_row,
                            'separator': separator_row,
                            'start_index': j,
                            'end_index': new_table_end - 1,
                            'last_data_line': lines[new_table_end - 1] if new_table_end > 0 and new_table_end <= len(lines) else ""
                        }
                        new_tables_after_continuation.append(table_info)
                        
                        # Continue search from after this table
                        j = new_table_end
                
                # Create enhanced chunk with previous table's headers and this chunk's content
                if tables_info:
                    # Use the first table in our tracking list
                    active_table = tables_info[0]
                    enhanced_chunk = ""
                    
                    # Add title if available
                    if active_table['title']:
                        enhanced_chunk += active_table['title'] + "\n\n"
                    
                    # Add header and separator
                    enhanced_chunk += active_table['header'] + "\n" + active_table['separator'] + "\n"
                    
                    # Add table content up to where new tables start (if any)
                    if new_tables_after_continuation:
                        # Only include lines up to where the next table starts
                        for j in range(min(table_end_index, new_tables_after_continuation[0]['start_index'])):
                            enhanced_chunk += lines[j] + "\n"
                        # Add the rest of the chunk as is
                        for j in range(min(table_end_index, new_tables_after_continuation[0]['start_index']), len(lines)):
                            enhanced_chunk += lines[j] + "\n"
                        # Update our table tracking to the new tables
                        tables_info = new_tables_after_continuation
                    else:
                        # No new tables, add the entire chunk
                        enhanced_chunk += chunk
                        # If this continuation includes the end of the table, clear our tracking
                        if table_end_index < len(lines):
                            tables_info = []
                    
                    processed_chunks.append(enhanced_chunk.rstrip())
                    continue
            
            # If this chunk has a new table after potentially continuing a previous one,
            # update our tracking
            if new_tables_found:
                tables_info = new_tables_found
        
        # If we reach here, either:
        # 1. This chunk starts new tables (which we've already processed and tracked)
        # 2. This chunk doesn't continue or start any tables
        processed_chunks.append(chunk)
    
    return processed_chunks