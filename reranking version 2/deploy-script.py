import boto3
import sagemaker
from sagemaker.pytorch import PyTorchModel
from sagemaker import get_execution_role

def deploy_reranker_model(
    model_data_s3_uri,
    role_arn=None,
    instance_type="ml.g4dn.xlarge",
    instance_count=1,
    endpoint_name="mxbai-reranker-endpoint",
    pytorch_version="2.0.1",
    py_version="py310",
    model_environment=None
):
    """
    Deploy a reranking model to SageMaker
    
    Args:
        model_data_s3_uri (str): S3 URI to the model tar.gz file
        role_arn (str): ARN of the IAM role with SageMaker permissions
        instance_type (str): SageMaker instance type
        instance_count (int): Number of instances
        endpoint_name (str): Name of the endpoint
        pytorch_version (str): PyTorch version
        py_version (str): Python version
        model_environment (dict): Environment variables for the model
    
    Returns:
        str: Endpoint name
    """
    # Get the execution role if not provided
    if not role_arn:
        role_arn = get_execution_role()
    
    # Set up default environment variables if needed
    if model_environment is None:
        model_environment = {
            "SAGEMAKER_CONTAINER_LOG_LEVEL": "20",
            "SAGEMAKER_PROGRAM": "inference.py"
        }
    
    # Create a SageMaker session
    session = sagemaker.Session()
    
    # Create the PyTorch model object
    pytorch_model = PyTorchModel(
        model_data=model_data_s3_uri,
        role=role_arn,
        entry_point="inference.py",
        framework_version=pytorch_version,
        py_version=py_version,
        env=model_environment,
        sagemaker_session=session
    )
    
    # Deploy the model to create an endpoint
    print(f"Deploying model to endpoint: {endpoint_name}")
    predictor = pytorch_model.deploy(
        initial_instance_count=instance_count,
        instance_type=instance_type,
        endpoint_name=endpoint_name
    )
    
    print(f"Model successfully deployed to endpoint: {endpoint_name}")
    return endpoint_name

# Example usage
if __name__ == "__main__":
    # Replace with your S3 URI
    model_s3_uri = "s3://your-bucket-name/path/to/model.tar.gz"
    
    # Optional: Specify a role ARN, otherwise it will use the execution role
    # role_arn = "arn:aws:iam::123456789012:role/SageMakerRole"
    
    # Deploy the model
    endpoint_name = deploy_reranker_model(
        model_data_s3_uri=model_s3_uri,
        instance_type="ml.g4dn.xlarge",  # GPU instance for better performance
        endpoint_name="mxbai-rerank-endpoint"
    )
