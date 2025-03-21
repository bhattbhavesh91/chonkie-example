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
    
    # Check if there's a local version of the model in the container
    model_path = os.path.join(model_dir, "model")
    if os.path.exists(model_path):
        print(f"Loading model from local path: {model_path}")
        model = MxbaiRerankV2(model_path)
    else:
        # Fall back to loading from Hugging Face Hub
        print("Loading model from Hugging Face Hub")
        model = MxbaiRerankV2("mixedbread-ai/mxbai-rerank-base-v2")
    
    return model

def input_fn(request_body, request_content_type):
    """
    Parse input data from the request
    """
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        return input_data
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Make a prediction using the input data
    """
    query = input_data.get("query", "")
    documents = input_data.get("documents", [])
    return_documents = input_data.get("return_documents", True)
    top_k = input_data.get("top_k", 3)
    
    if not query or not documents:
        return {"error": "Both query and documents are required"}
    
    results = model.rank(
        query=query,
        documents=documents,
        return_documents=return_documents,
        top_k=top_k
    )
    
    return results

def output_fn(prediction, response_content_type):
    """
    Format the prediction response
    """
    if response_content_type == 'application/json':
        return json.dumps(prediction)
    else:
        raise ValueError(f"Unsupported content type: {response_content_type}")
