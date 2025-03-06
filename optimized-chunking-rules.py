from chonkie.chunkers import RecursiveChunker
from chonkie.rules import RecursiveRules, RecursiveLevel

# Optimized rules for better context retention between headers and subheaders
rules = RecursiveRules(
    levels=[
        # Level 1: Split on major section boundaries (H1 and H2)
        # This ensures larger logical sections stay together
        RecursiveLevel(delimiters=["#", "##"], include_delim="next"),
        
        # Level 2: Split on minor headers (H3 to H6)
        # These will only be considered if the chunk is still too large after major headers
        RecursiveLevel(delimiters=["###", "####", "#####", "######"], include_delim="next"),
        
        # Level 3: Split on paragraph boundaries
        # Different paragraph separators for various line ending styles
        RecursiveLevel(delimiters=["\n\n", "\r\n\r\n"]),
        
        # Level 4: Split on markdown tables
        RecursiveLevel(delimiters=["\n|"], include_delim="next"),
        
        # Level 5: Split on sentence boundaries
        RecursiveLevel(delimiters=[". ", "? ", "! ", "; ", ": "]),
        
        # Level 6: Character-level splitting as a last resort
        RecursiveLevel(),
    ],
    
    # Optional: You can add these parameters for better control
    min_chunk_size=100,  # Prevent extremely small chunks
    chunk_overlap=50,    # Add overlap between chunks for context continuity
)

# Initialize the chunker with the new rules
chunker = RecursiveChunker(
    rules=rules, 
    chunk_size=384,
    # Optionally add a separator to clearly mark where chunks were split
    separator="\n---\n"
)
