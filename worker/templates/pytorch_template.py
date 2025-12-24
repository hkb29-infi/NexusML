import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
import json
import os
from pathlib import Path
import requests
from datetime import datetime

# Job configuration
JOB_ID = "{job_id}"
API_URL = os.getenv("API_URL", "http://backend:8000")

# Training configuration
MODEL_NAME = "{model}"
DATASET = "{dataset}"
EPOCHS = {epochs}
BATCH_SIZE = {batch_size}
LEARNING_RATE = {learning_rate}
OPTIMIZER = "{optimizer}"

def log_metric(step, metric_name, metric_value):
    """Log metric to API."""
    try:
        requests.post(
            f"{{API_URL}}/api/jobs/{{JOB_ID}}/metrics",
            json={{
                "step": step,
                "metric_name": metric_name,
                "metric_value": metric_value,
                "timestamp": datetime.utcnow().isoformat()
            }}
        )
    except Exception as e:
        print(f"Failed to log metric: {{e}}")

def get_model():
    """Load model based on config."""
    if MODEL_NAME == "resnet50":
        return models.resnet50(pretrained=False)
    elif MODEL_NAME == "resnet18":
        return models.resnet18(pretrained=False)
    else:
        raise ValueError(f"Unknown model: {{MODEL_NAME}}")

def get_dataset():
    """Load dataset based on config."""
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    if DATASET == "cifar10":
        train_dataset = datasets.CIFAR10(
            root='./data',
            train=True,
            download=True,
            transform=transform
        )
        return train_dataset
    else:
        raise ValueError(f"Unknown dataset: {{DATASET}}")

def train():
    """Main training loop."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {{device}}")
    
    # Load model and dataset
    model = get_model().to(device)
    dataset = get_dataset()
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=4)
    
    # Setup optimizer and loss
    criterion = nn.CrossEntropyLoss()
    if OPTIMIZER == "adam":
        optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    elif OPTIMIZER == "sgd":
        optimizer = optim.SGD(model.parameters(), lr=LEARNING_RATE, momentum=0.9)
    else:
        raise ValueError(f"Unknown optimizer: {{OPTIMIZER}}")
    
    # Training loop
    global_step = 0
    for epoch in range(EPOCHS):
        model.train()
        epoch_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            # Calculate accuracy
            _, predicted = output.max(1)
            total += target.size(0)
            correct += predicted.eq(target).sum().item()
            
            epoch_loss += loss.item()
            global_step += 1
            
            # Log metrics every 10 batches
            if batch_idx % 10 == 0:
                log_metric(global_.step, "train_loss", loss.item())
                log_metric(global_step, "train_accuracy", 100. * correct / total)
                
                print(f"Epoch: {{epoch+1}}/{{EPOCHS}} | Batch: {{batch_idx}}/{{len(dataloader)}} | "
                      f"Loss: {{loss.item():.4f}} | Acc: {{100.*correct/total:.2f}}%")
        
        # Log epoch metrics
        avg_loss = epoch_loss / len(dataloader)
        accuracy = 100. * correct / total
        log_metric(global_step, "epoch_loss", avg_loss)
        log_metric(global_step, "epoch_accuracy", accuracy)
        
        print(f"Epoch {{epoch+1}} completed: Avg Loss: {{avg_loss:.4f}}, Accuracy: {{accuracy:.2f}}%")
        
        # Save checkpoint
        checkpoint_dir = Path("./checkpoints")
        checkpoint_dir.mkdir(exist_ok=True)
        torch.save({{
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'loss': avg_loss,
        }}, checkpoint_dir / f"checkpoint_epoch_{{epoch+1}}.pt")
    
    # Save final model
    output_dir = Path("./output")
    output_dir.mkdir(exist_ok=True)
    torch.save(model.state_dict(), output_dir / "final_model.pt")
    print("Training completed!")

if __name__ == "__main__":
    train()
