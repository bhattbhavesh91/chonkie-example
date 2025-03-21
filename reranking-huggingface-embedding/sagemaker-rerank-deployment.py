import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker import image_uris

# Initialize SageMaker session
sagemaker_session = sagemaker.Session()
region = boto3.session.Session().region_name
role = sagemaker.get_execution_role()

# S3 location of your model artifacts
model_data = "s3://your-bucket-name/path/to/model.tar.gz"

# Hugging Face container configuration
huggingface_container = image_uris.retrieve(
    framework="huggingface",
    region=region,
    version="4.26.0",  # You might need to adjust this based on your requirements
    image_scope="inference",
    base_framework_version="pytorch1.13.1",  # Adjust based on the model requirements
)

# Define environment variables for the container
environment = {
    "HF_MODEL_ID": "mixedbread-ai/mxbai-rerank-base-v2",
    "HF_TASK": "feature-extraction",  # For embedding/reranking models
    "SAGEMAKER_PROGRAM": "inference.py",  # Path to your inference script
    "SAGEMAKER_SUBMIT_DIRECTORY": "/opt/ml/model/code",  # Where your code will be in the container
    "MAX_SEQUENCE_LENGTH": "512",  # Adjust based on your requirements
    "MAX_CONCURRENT_REQUESTS": "4"  # Adjust based on your requirements
}

# Create Hugging Face Model
huggingface_model = HuggingFaceModel(
    model_data=model_data,
    role=role,
    image_uri=huggingface_container,
    env=environment,
    name="mxbai-rerank-model"
)

# Deploy the model to create an endpoint
predictor = huggingface_model.deploy(
    initial_instance_count=1,
    instance_type="ml.g4dn.xlarge",  # Choose an appropriate instance type based on your needs
    endpoint_name="mxbai-rerank-endpoint"
)

print(f"Endpoint deployed: {predictor.endpoint_name}")

# Example of how to use the endpoint
def query_endpoint(query, documents):
    client = boto3.client('sagemaker-runtime')
    
    # Prepare payload in the format expected by your inference.py
    payload = {
        "query": query,
        "documents": documents,
        "return_documents": True,
        "top_k": 3
    }
    
    # Send request to the endpoint
    response = client.invoke_endpoint(
        EndpointName="mxbai-rerank-endpoint",
        ContentType="application/json",
        Body=json.dumps(payload)
    )
    
    # Parse the response
    result = json.loads(response['Body'].read().decode())
    return result

# Example usage
if __name__ == "__main__":
    import json
    
    query = "Who wrote 'To Kill a Mockingbird'?"
    documents = [
        "'To Kill a Mockingbird' is a novel by Harper Lee published in 1960. It was immediately successful, winning the Pulitzer Prize, and has become a classic of modern American literature.",
        "The novel 'Moby-Dick' was written by Herman Melville and first published in 1851. It is considered a masterpiece of American literature and deals with complex themes of obsession, revenge, and the conflict between good and evil.",
        "Harper Lee, an American novelist widely known for her novel 'To Kill a Mockingbird', was born in 1926 in Monroeville, Alabama. She received the Pulitzer Prize for Fiction in 1961.",
        "Jane Austen was an English novelist known primarily for her six major novels, which interpret, critique and comment upon the British landed gentry at the end of the 18th century.",
        "The 'Harry Potter' series, which consists of seven fantasy novels written by British author J.K. Rowling, is among the most popular and critically acclaimed books of the modern era.",
        "'The Great Gatsby', a novel written by American author F. Scott Fitzgerald, was published in 1925. The story is set in the Jazz Age and follows the life of millionaire Jay Gatsby and his pursuit of Daisy Buchanan."
    ]
    
    try:
        results = query_endpoint(query, documents)
        print("Reranked results:")
        print(results)
    except Exception as e:
        print(f"Error querying endpoint: {e}")
