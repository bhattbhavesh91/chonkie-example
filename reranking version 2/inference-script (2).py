import json
import os
import torch
from mxbai_rerank import MxbaiRerankV2

# Load the model once when the container starts
def model_fn(model_dir):
    """
    Load the model for inference
    """
    print(f"Loading model from {model_dir}")
    # Load the model - you can either use the local files or the HF model name
    # If you've included the model files in your tar.gz, use:
    model = MxbaiRerankV2(model_dir)
    # If you want to download from HF:
    # model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")
    return model

# Deserialize the incoming request and prepare the data
def input_fn(request_body, request_content_type):
    """
    Parse input data
    """
    print(f"Received request with content type: {request_content_type}")
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

# Perform inference and return the results
def predict_fn(input_data, model):
    """
    Apply model to the input data and return predictions
    """
    query = input_data.get('query', '')
    documents = input_data.get('documents', [])
    top_k = input_data.get('top_k', 3)
    return_documents = input_data.get('return_documents', True)
    
    print(f"Processing query: {query}")
    print(f"Number of documents: {len(documents)}")
    
    # Return empty list if documents is empty
    if not documents:
        return {"results": []}
    
    # Get the ranking results
    results = model.rank(
        query, 
        documents, 
        return_documents=return_documents, 
        top_k=top_k
    )
    
    return {"results": results}

# Serialize the prediction result into the desired response content type
def output_fn(prediction, response_content_type):
    """
    Serialize the prediction result
    """
    if response_content_type == 'application/json':
        return json.dumps(prediction), response_content_type
    else:
        raise ValueError(f"Unsupported content type: {response_content_type}")
