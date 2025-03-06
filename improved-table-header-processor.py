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
    header_pattern_found = False
    
    for i, chunk in enumerate(chunks):
        # Check if this chunk starts or contains a table
        contains_pipe = "|" in chunk
        contains_separator = any(line.strip().startswith('|') and '---' in line for line in chunk.split('\n'))
        
        # If we find a header pattern (| column | column |) in this chunk
        header_row = None
        separator_row = None
        
        if contains_pipe:
            lines = chunk.split('\n')
            
            # First, try to find a header row and separator row
            for j in range(len(lines) - 1):
                if '|' in lines[j] and j+1 < len(lines) and '|' in lines[j+1] and '---' in lines[j+1]:
                    header_row = lines[j]
                    separator_row = lines[j+1]
                    header_pattern_found = True
                    break
            
            # If we found header pattern or this is the first chunk with pipes
            if header_pattern_found or (not table_active and contains_pipe):
                # Extract table title - look above the table
                title_line = None
                table_start_index = -1
                
                # Find where the table starts
                for j, line in enumerate(lines):
                    if '|' in line:
                        table_start_index = j
                        break
                
                # Look for the closest header or text above the table
                if table_start_index > 0:
                    for j in range(table_start_index - 1, -1, -1):
                        line = lines[j].strip()
                        if line and not line.startswith('|'):
                            title_line = line
                            # If we found a heading, prefer this as the title
                            if line.startswith('#'):
                                break
                            # Otherwise keep looking for a better title (maybe a heading)
                
                # If we found title and headers, store them
                if title_line and header_row and separator_row:
                    current_table_title = title_line
                    current_table_headers = header_row + '\n' + separator_row
                    table_active = True
                    processed_chunks.append(chunk)
                    continue
                
                # If we found a title but no complete header pattern in this chunk
                if title_line and not (header_row and separator_row) and contains_pipe:
                    # Let's check if this might be the start of a table with incomplete headers
                    table_lines = [line for line in lines if '|' in line]
                    if len(table_lines) >= 1:
                        if i + 1 < len(chunks) and '|' in chunks[i+1] and ('---' in chunks[i+1] or table_lines[-1].count('|') == chunks[i+1].split('\n')[0].count('|')):
                            # This looks like a header row with the separator in the next chunk
                            # We'll process it when we get to the next chunk
                            current_table_title = title_line
                            processed_chunks.append(chunk)
                            continue
            
            # If we're in an active table and this chunk continues it
            if table_active and contains_pipe and not header_pattern_found:
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
                continue
        
        # If we get here, this is not part of an active table, or it's a new table
        if not contains_pipe or header_pattern_found:
            table_active = False if not header_pattern_found else True
            header_pattern_found = False
            if not contains_pipe:
                current_table_headers = None
                current_table_title = None
        
        processed_chunks.append(chunk)
    
    return processed_chunks

# Example usage
if __name__ == "__main__":
    # Your second example with the IDFC FIRST Bank FD rates
    chunks = [
        """### Fixed Deposit Interest Rate
IDFC FIRST Bank offers the best Fixed Deposit rates for general and senior citizens. Senior citizens are given an a dded advantage and can earn 0.50% more as interest. The below table will give you a better idea of the interest off ered to senior and non-senior citizens for deposits under 73 crores. You can use it to decide the tenure of your FD s at IDFC FIRST Bank.
| Tenure | FD rates for Non-Senior Citizens w.e.f November 26, 2024 - Less than INR 3 Crores | FD rates for Senior Citizens w.e.f November 26, 2024 - Less than INR 3 Crores |
| --- | --- | --- |
|7 – 14 days |3.00% | 3.50% |
|15 – 29 days | 3.00% | 3.50% |
|30 – 45 days | 3.00% | 3.50% |
|46 – 90 days |	4.50% | 5.00% |
|91 – 180 days | 4.50% | 5.00% |
|181 days – & less than 1 year | 5.75% | 6.25% |
|1 year | 6.50% | 7.00% |
|1 year 1 day – 370 days | 7.25% | 7.75% |""",
        
        """|371 days – 399 days | 7.50% | 8.00% |
|400 days – 500 days | 7.90% | 8.40% |
|501 days – 2 years	7.25% | 7.75% |
|2 years 1 day – 3 years | 6.80% | 7.30% |
|3 years 1 day – 5 years | 6.75% | 7.25% |
|5 years- 1 day – 10 years |6.50% | 7.00% |"""
    ]
    
    processed_chunks = process_chunks(chunks)
    
    print("PROCESSED CHUNKS:")
    for i, chunk in enumerate(processed_chunks):
        print(f"\nCHUNK {i+1}:")
        print(chunk)

    # First example with Virat Kohli's centuries
    chunks_example1 = [
        """# Virat Kohli - Centuries Virat Kohli is one of the most successful and consistent batsmen in modern-day cricket. Below is a table summarizing his centuries in international cricket (as of March 2025). 
## List of Virat Kohli's Centuries | No. | Format | Opponent | Match Date | Venue | Score | |---------|---------------|-----------------|----------------|---------------------|-----------| | 1 | ODI | Sri Lanka | 2013-07-21 | Colombo | 102* | | 2 | Test | Australia | 2014-12-17 | Adelaide | 115 | | 3 | ODI | West Indies | 2014-10-11 | North Sound | 100 | | 4 | ODI | Sri Lanka | 2014-11-01 | Ranchi | 139 |""",
        
        """| 5 | ODI | South Africa | 2015-10-14 | Kanpur | 138 | | 6 | Test | Sri Lanka | 2017-07-29 | Galle | 103 | | 7 | ODI | New Zealand | 2017-10-22 | Pune | 121 | | 8 | Test | Bangladesh | 2017-02-09 | Hyderabad | 204 | | 9 | ODI | Sri Lanka | 2017-08-21 | Colombo | 103* | | 10 | ODI | Australia | 2019-03-10 | Ranchi | 116 |""",
        
        """| 11 | ODI | West Indies | 2019-08-14 | Port of Spain | 114 | | 12 | Test | Australia | 2018-12-06 | Adelaide | 123 | | 13 | T20I | Sri Lanka | 2016-03-22 | Mohali | 82* | | 14 | Test | West Indies | 2019-08-30 | Kingston | 114 | | 15 | ODI | South Africa | 2018-02-14 | Johannesburg | 160 | This table highlights some of the notable centuries scored by Virat Kohli. He has been an exceptional performer a