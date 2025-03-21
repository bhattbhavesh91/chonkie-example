import json
import boto3

def test_reranker_endpoint(
    endpoint_name,
    query,
    documents,
    top_k=3,
    return_documents=True
):
    """Test the deployed reranker endpoint
    
    Args:
        endpoint_name (str): Name of the SageMaker endpoint
        query (str): Query text
        documents (list): List of document texts
        top_k (int): Number of top documents to return
        return_documents (bool): Whether to include documents in result
        
    Returns:
        dict: Response from the endpoint
    """
    # Create a SageMaker runtime client
    runtime = boto3.client('sagemaker-runtime')
    
    # Prepare the payload
    payload = {
        "query": query,
        "documents": documents,
        "top_k": top_k,
        "return_documents": return_documents
    }
    
    # Invoke the endpoint
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    # Parse and return the response
    result = json.loads(response['Body'].read().decode())
    return result

# Example usage
if __name__ == "__main__":
    # Example query and documents
    query = "Who wrote 'To Kill a Mockingbird'?"
    documents = [
        "'To Kill a Mockingbird' is a novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature.",
        "The novel 'Moby-Dick' was written by Herman Melville and first published in 1851. It is considered a masterpiece of American literature and deals with complex themes of obsession, revenge, and the conflict between good and evil.",
        "Harper Lee, an American novelist widely known for her novel 'To Kill a Mockingbird', was born in 1926 in Monroeville, Alabama. She received the Pulitzer Prize for Fiction in 1961.",
        "Jane Austen was an English novelist known primarily for her six major novels, which interpret, critique and comment upon the British landed gentry at the end of the 18th century.",
        "The 'Harry Potter' series, which consists of seven fantasy novels written by British author J.K. Rowling, is among the most popular and critically acclaimed books of the modern era.",
        "'The Great Gatsby', a novel written by American author F. Scott Fitzgerald, was published in 1925. The story is set in the Jazz Age and follows the life of millionaire Jay Gatsby and his pursuit of Daisy Buchanan."
    ]
    
    # Test the endpoint
    result = test_reranker_endpoint(
        endpoint_name="mxbai-rerank-endpoint",
        query=query,
        documents=documents,
        top_k=3
    )
    
    print(json.dumps(result, indent=2))
