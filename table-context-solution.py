import re
from typing import List, Dict, Tuple, Optional

def process_markdown_chunks(chunks: List[str]) -> List[str]:
    """
    Process markdown chunks to preserve table context across chunks.
    
    This function specifically looks at adjacent chunks to identify if a table
    spans across them, and ensures the table headers and description are properly
    maintained in subsequent chunks.
    
    Args:
        chunks: List of markdown text chunks
        
    Returns:
        List of processed chunks with table context preserved
    """
    if not chunks:
        return []
        
    processed_chunks = chunks.copy()
    
    # Process consecutive pairs of chunks
    for i in range(len(chunks) - 1):
        current_chunk = chunks[i]
        next_chunk = chunks[i + 1]
        
        # Check if the first chunk has a table with headers
        table_headers = extract_table_headers(current_chunk)
        
        if table_headers and is_table_continuation(next_chunk):
            # Extract the table description above the table in the first chunk
            table_description = extract_table_description(current_chunk)
            
            # Prepare the table context to prepend to the second chunk
            context_to_add = ""
            if table_description:
                context_to_add += table_description + "\n\n"
                
            # Add the table headers
            context_to_add += "\n".join(table_headers) + "\n"
            
            # Add the enhanced context to the beginning of the second chunk
            processed_chunks[i + 1] = context_to_add + next_chunk
    
    return processed_chunks

def extract_table_headers(chunk: str) -> List[str]:
    """
    Extract the table headers (column headers and separator line) from a chunk.
    
    Args:
        chunk: Markdown chunk that might contain a table
        
    Returns:
        List of strings containing the header row and separator row, or empty list if not found
    """
    lines = chunk.split('\n')
    for i in range(len(lines) - 1):
        # Check for a table separator line (| --- | --- |)
        if '|' in lines[i] and re.search(r'\| *--- *\|', lines[i + 1]):
            # Return the header row and the separator row
            return [lines[i], lines[i + 1]]
    return []

def is_table_continuation(chunk: str) -> bool:
    """
    Check if a chunk appears to be a continuation of a table but without headers.
    
    Args:
        chunk: Markdown chunk to check
        
    Returns:
        Boolean indicating if chunk is likely a table continuation
    """
    if not chunk:
        return False
        
    lines = chunk.split('\n')
    
    # Check if the first line is a table row but not a header or separator
    if lines and '|' in lines[0]:
        # Make sure it's not a separator line (| --- |)
        if not re.search(r'\| *--- *\|', lines[0]):
            return True
            
    return False

def extract_table_description(chunk: str) -> str:
    """
    Extract the table description from above the table in a markdown chunk.
    
    Args:
        chunk: Markdown chunk containing a table
        
    Returns:
        String containing the table description or empty string if not found
    """
    lines = chunk.split('\n')
    
    # Find where the table starts (header line)
    table_start_idx = -1
    for i in range(len(lines) - 1):
        if '|' in lines[i] and re.search(r'\| *--- *\|', lines[i + 1]):
            table_start_idx = i
            break
            
    if table_start_idx <= 0:
        return ""
        
    # Work backwards from the table header to find the description
    description_lines = []
    idx = table_start_idx - 1
    
    # Collect lines above the table
    while idx >= 0 and lines[idx].strip():
        description_lines.insert(0, lines[idx])
        idx -= 1
    
    # If we didn't find any description, return empty string
    if not description_lines:
        return ""
        
    # Return the description as a single string
    return "\n".join(description_lines)

# Example of how to use the functions
def main():
    # Example chunks from the problem statement
    chunk1 = """- Monthly/quarterly interest pay-out option or quarterly compounding. You choose what is beneficial to you. You can opt to get a comparatively lower sum every month, or you could choose to get paid every three months with a sizable amount.
- Get 0.5% higher interest for senior citizens with IDFC FIRST Bank's Fixed Deposit account
- Get up to 7.90% per annum on your idle funds.
IDFC FIRST Bank offers the best Fixed Deposit rates for general and senior citizens. Senior citizens are given an added advantage and can earn 0.50% more as interest. The below table will give you a better idea of the interest offered to senior and non-senior citizens for deposits under 83 crores. You can use it to decide the tenure of your FDs at IDFC FIRST Bank.
| Tenure | FD rates for Non-Senior Citizens w.e.f November 26, 2024 - Less than INR 3 Crores | FD rates for Senior Citizens w.e.f November 26, 2024 - Less than INR 3 Crores |
| --- | --- | --- |
|7 – 14 days |3.00% | 3.50% |
|15 – 29 days | 3.00% | 3.50% |
|30 – 45 days | 3.00% | 3.50% |
|46 – 90 days |	4.50% | 5.00% |
|91 – 180 days | 4.50% | 5.00% |
|181 days – & less than 1 year | 5.75% | 6.25% |
|1 year | 6.50% | 7.00% |
|1 year 1 day – 370 days | 7.25% | 7.75% |"""

    chunk2 = """|371 days – 399 days | 7.50% | 8.00% |
|400 days – 500 days | 7.90% | 8.40% |
|501 days – 2 years	7.25% | 7.75% |
|2 years 1 day – 3 years | 6.80% | 7.30% |
|3 years 1 day – 5 years | 6.75% | 7.25% |
|5 years- 1 day – 10 years |6.50% | 7.00% |
**Tax Saver Deposit (Only for Domestic Deposits) **
| Tenure | Rate of Interest (sp.a.) w.e.f November 26, 2024 Less than INR 3 Crores |
| --- | --- |
| 5 years | 6.75% |

**Green Deposits (Only for Domestic Deposits) **
| Tenure | Rate of Interest (%p.a.) w.e.f November 26, 2024 Less than INR 3 Crores |
| --- | --- |
| 725 days | 7.25% |"""

    # Process the chunks
    processed_chunks = process_markdown_chunks([chunk1, chunk2])
    
    # Display the results
    print("PROCESSED CHUNK 2:")
    print(processed_chunks[1])
    
    return processed_chunks

if __name__ == "__main__":
    main()
