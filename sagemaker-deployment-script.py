import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker import get_execution_role
import json
import os

def deploy_rerank_model(
    model_data_s3_uri,
    instance_type="ml.g4dn.xlarge",  # GPU instance for faster inference
    model_name="mxbai-rerank-model",
    endpoint_name="mxbai-rerank-endpoint",
    region=None
):
    """
    Deploy a reranking model (mxbai-rerank-base-v2) to a SageMaker endpoint.
    
    Parameters:
    -----------
    model_data_s3_uri : str
        S3 URI to the tar.gz file containing the model artifacts
    instance_type : str
        Instance type for the endpoint
    model_name : str
        Name for the SageMaker model
    endpoint_name : str
        Name for the SageMaker endpoint
    region : str
        AWS region to deploy the model in
    
    Returns:
    --------
    str
        Endpoint name
    """
    # Initialize SageMaker session
    if region:
        boto_session = boto3.Session(region_name=region)
        sagemaker_session = sagemaker.Session(boto_session=boto_session)
    else:
        sagemaker_session = sagemaker.Session()
    
    # Get the execution role
    role = get_execution_role()
    
    # Environment variables for the model
    env = {
        'MODEL_NAME': 'mixedbread-ai/mxbai-rerank-base-v2',
        'MODEL_CACHE_DIR': '/opt/ml/model',
        'TRANSFORMERS_CACHE': '/opt/ml/model'
    }
    
    # Create the model
    model = Model(
        image_uri=get_pytorch_image_uri(),
        model_data=model_data_s3_uri,
        role=role,
        env=env,
        name=model_name,
        sagemaker_session=sagemaker_session
    )
    
    # Deploy the model
    print(f"Deploying model to endpoint: {endpoint_name}")
    predictor = model.deploy(
        initial_instance_count=1,
        instance_type=instance_type,
        endpoint_name=endpoint_name
    )
    
    print(f"Model deployed successfully to endpoint: {endpoint_name}")
    return endpoint_name

def get_pytorch_image_uri():
    """Get the latest PyTorch inference image URI from SageMaker"""
    return sagemaker.image_uris.retrieve(
        framework="pytorch",
        region=boto3.Session().region_name,
        version="1.13.1",
        py_version="py39",
        image_scope="inference",
        instance_type="ml.g4dn.xlarge"
    )

def test_endpoint(endpoint_name, query, documents):
    """
    Test the deployed endpoint with a sample query and documents.
    
    Parameters:
    -----------
    endpoint_name : str
        The name of the deployed SageMaker endpoint
    query : str
        The query text
    documents : list
        List of documents to rerank
    
    Returns:
    --------
    dict
        Reranking results
    """
    runtime = boto3.client('runtime.sagemaker')
    
    # Prepare the payload
    payload = {
        'query': query,
        'documents': documents,
        'return_documents': True,
        'top_k': 3
    }
    
    # Invoke the endpoint
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    # Parse the response
    result = json.loads(response['Body'].read().decode())
    return result

# Example usage
if __name__ == "__main__":
    # Replace with your S3 URI where your model artifacts are stored
    model_data_s3_uri = "s3://your-bucket-name/path/to/model.tar.gz"
    
    # Deploy the model
    endpoint_name = deploy_rerank_model(
        model_data_s3_uri=model_data_s3_uri,
        instance_type="ml.g4dn.xlarge",
        model_name="mxbai-rerank-model",
        endpoint_name="mxbai-rerank-endpoint"
    )
    
    # Example test
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
    results = test_endpoint(endpoint_name, query, documents)
    print(results)
