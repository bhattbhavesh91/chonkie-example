import os
import json
import torch
from mxbai_rerank import MxbaiRerankV2

# Load the model once when the container starts
model = None
device = "cuda" if torch.cuda.is_available() else "cpu"

def model_fn(model_dir):
    """
    Load the model for inference
    """
    global model
    
    # Get model name from environment variable or use default
    model_name = os.environ.get("MODEL_NAME", "mixedbread-ai/mxbai-rerank-base-v2")
    
    # Initialize the model
    print(f"Loading model {model_name} on {device}")
    model = MxbaiRerankV2(model_name, device=device)
    
    return model

def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Apply model to the input data
    """
    query = input_data.get('query')
    documents = input_data.get('documents', [])
    return_documents = input_data.get('return_documents', True)
    top_k = input_data.get('top_k', 3)
    
    # Perform reranking
    results = model.rank(
        query=query, 
        documents=documents, 
        return_documents=return_documents, 
        top_k=top_k
    )
    
    return results

def output_fn(prediction, response_content_type):
    """
    Serialize and prepare the prediction output
    """
    if response_content_type == 'application/json':
        return json.dumps(prediction)
    else:
        return json.dumps(prediction)
