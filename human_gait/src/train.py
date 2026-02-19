
import argparse
import os
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import time

from tqdm import tqdm
from torch.optim import AdamW
from torch.utils.data import DataLoader
from torchmetrics.classification import MulticlassF1Score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from src.models.cnn_1d import CNN1D
from src.dataset import GaitDataset

def accuracy_fn(y_true, y_pred):
    """Calculates accuracy between truth labels and predictions.

    Args:
        y_true (torch.Tensor): Truth labels for predictions.
        y_pred (torch.Tensor): Predictions to be compared to predictions.

    Returns:
        [torch.float]: Accuracy value between y_true and y_pred, e.g. 78.45
    """
    
    correct = (y_pred.argmax(dim=1) == y_true).sum().item()
    return correct / len(y_true) * 100

def train(model, device, num_epoch, optimizer, loss_fn, class_data, train_dataloader, test_dataloader):
    # Define model size and send to CPU
    model.to(device)

    # setup F1 score 
    f1 = MulticlassF1Score(num_classes=len(class_data)).to(device)

    # Create empty lists to track values
    train_loss_values = []
    train_acc_values = []
    test_loss_values = []
    test_acc_values = []
    test_f1_values = []

    # Use tqdm iterator to show real-time training statistics
    # Three-line tqdm display: stats on top, progress bar below.
    stats_bar = tqdm(
        total=0,
        desc="",
        position=0,
        bar_format="{desc}",
        dynamic_ncols=True,
        leave=True,
    )
    timing_bar = tqdm(
        total=0,
        desc="",
        position=1,
        bar_format="{desc}",
        dynamic_ncols=True,
        leave=True,
    )
    progress_bar = tqdm(
        total=num_epoch,
        desc="Training",
        unit="epoch",
        position=2,
        dynamic_ncols=True,
        colour="cyan",
        leave=True,
    )

    ###############################
    # Start the main training loop 
    ###############################
    for epoch in range(num_epoch):
        epoch_start = time.perf_counter()
        ### Training
        model.train()
        train_loss = 0
        train_acc = 0

        # Add a loop to loop through training batches
        train_data_time = 0.0
        train_step_time = 0.0
        prev_end = time.perf_counter()
        
        for X, y in train_dataloader:
            data_start = time.perf_counter()
            train_data_time += data_start - prev_end
            # 1. Forward pass
            X = X.to(device)
            # Keep target as 1D [batch] even when batch_size == 1.
            y = y.long().to(device).view(-1)
            
            step_start = time.perf_counter()
            y_pred = model(X)

            # 2. Calculate loss and accuracy (per batch)  
            loss = loss_fn(y_pred, y)
            train_acc += accuracy_fn(y_true=y, y_pred=y_pred)

            # 3. Optimizer zero grad
            optimizer.zero_grad()

            # 4. Loss backward
            loss.backward()

            # 5. Optimizer step 
            optimizer.step()

            train_step_time += time.perf_counter() - step_start

            # 6. Accumulatively add up the loss per epoch 
            train_loss += loss.item()

            prev_end = time.perf_counter()

        # Divide total train loss by length of train dataloader (average loss per batch per epoch)
        train_loss /= len(train_dataloader)
        train_acc /= len(train_dataloader)

        ### Testing
        # Setup variables for accumulatively adding up loss and accuracy 
        test_loss, test_acc = 0, 0
        model.eval()

        all_preds = []
        all_labels = []
        distance = 0

        # Calculations on test metrics should happen inside torch.inference_mode()
        test_data_time = 0.0
        test_step_time = 0.0
        prev_end = time.perf_counter()

        with torch.inference_mode():
            for X, y in test_dataloader:
                data_start = time.perf_counter()
                test_data_time += data_start - prev_end
                # 1. Forward pass   
                X = X.to(device)
                # Keep target as 1D [batch] even when batch_size == 1.
                y = y.long().to(device).view(-1)
                
                step_start = time.perf_counter()
                test_pred = model(X)

                # 2. Calculate loss (accumulatively)
                loss = loss_fn(test_pred, y)
                test_loss += loss.item() # accumulatively add up the loss per epoch

                # 3. Calculate accuracy
                test_acc += accuracy_fn(y_true=y, y_pred=test_pred)

                # Convert logits to class labels
                predicted_labels = torch.argmax(test_pred, dim=1)

                # Store predictions and true labels
                all_preds.extend(predicted_labels.cpu().tolist())
                all_labels.extend(y.cpu().tolist())

                test_step_time += time.perf_counter() - step_start
                prev_end = time.perf_counter()

                # Calculate Hamming Distance Between predictions and correct categories
                distance += (predicted_labels != y).sum().item()

            # Divide total test loss by length of test dataloader (per batch)
            test_loss /= len(test_dataloader)

            # Divide total accuracy by length of test dataloader (per batch)
            test_acc /= len(test_dataloader)

        # Calculate F1 score for the test set
        epoch_f1 = f1(torch.tensor(all_preds).to(device), torch.tensor(all_labels).to(device))

        epoch_total = time.perf_counter() - epoch_start

        # Track epoch metrics
        train_acc_values.append(train_acc)
        test_acc_values.append(test_acc)
        test_f1_values.append(float(epoch_f1) if hasattr(epoch_f1, "item") else epoch_f1)

        # Print out what's happening in the epoch loop
        metrics = (
            f"Train Loss={train_loss:.4f}, "
            f"Train Acc={train_acc:.2f}, "
            f"Test Loss={test_loss:.4f}, "
            f"Test Acc={test_acc:.2f}, "
            f"Test F1={epoch_f1:.4f}"
        )
        stats_bar.set_description_str(f"Epoch {epoch + 1}/{num_epoch} | {metrics}")
        stats_bar.refresh()
        timing = (
            f"Timing | Train Data={train_data_time:.2f}s, Train Step={train_step_time:.2f}s, "
            f"Test Data={test_data_time:.2f}s, Test Step={test_step_time:.2f}s, "
            f"Epoch Total={epoch_total:.2f}s"
        )
        timing_bar.set_description_str(timing)
        timing_bar.refresh()
        progress_bar.update(1)

        # keep a history to view loss curves.
        train_loss_values.append(train_loss)
        test_loss_values.append(test_loss)

    return {
        "train_loss_values": train_loss_values,
        "train_acc_values": train_acc_values,
        "test_loss_values": test_loss_values,
        "test_acc_values": test_acc_values,
        "test_f1_values": test_f1_values,
        "all_preds": all_preds,
        "all_labels": all_labels,
    }

def parse_args():
    parser = argparse.ArgumentParser(description="Train and save the Pytorch model and results for human gait recognition.")
    
    # Training Hyperparameters
    parser.add_argument("-lr", "--learning-rate", type=float, default=0.001, 
                        help="Learning rate for the optimizer (default: 0.001)")
    
    parser.add_argument("-e", "--epochs", type=int, default=1000, 
                        help="Number of training epochs (default: 1000)")
    
    parser.add_argument("-b", "--batch-size", type=int, default=32, 
                        help="Batch size for training and testing (default: 32)")
    
    parser.add_argument("-wd", "--weight-decay", type=float, default=1e-4, 
                        help="Weight decay (L2 penalty) for the optimizer (default: 0.0001)")

    # Data Configuration
    parser.add_argument("-d", "--data-dir", type=str, default="data/processed", 
                        help="Path to the directory containing processed data (default: data/processed)")
    
    parser.add_argument("-t", "--train-split", type=float, default=0.8, 
                        help="Fraction of data to use for training (default: 0.8)")
    
    parser.add_argument("-nspf", "--no-split-by-file", dest="split_by_file", action="store_false",
                        help="Do not split the train and test dataset by file")

    # System & Output Configuration
    parser.add_argument("-dev", "--device", type=str, default="cpu", 
                        help="Computation device to use (e.g., 'cpu', 'cuda', 'cuda:0', 'mps'). Default: cpu")
    
    parser.add_argument("-s", "--model-save-dir", type=str, default="output/", 
                        help="File path where the best trained model files will be saved (default: output/)")
    
    parser.add_argument("--seed", type=int, default=42, 
                        help="Random seed for reproducibility (default: 42)")
    
    parser.add_argument("-l", "--label", type=str, default="", 
                        help="Label for the output directory name (default: '')")

    return parser.parse_args()

def save_results(model, stats, save_dir, args):
    if not save_dir:
        return 

    os.makedirs(save_dir, exist_ok=True)

    # Create a unique run folder to avoid overwriting previous results
    run_name = time.strftime("train_%Y%m%d_%H%M%S")
    if args.label:
        run_name += "_" + args.label

    run_dir = os.path.join(save_dir, run_name)
    os.makedirs(run_dir, exist_ok=True)

    # Save the training command used for this run (include all args)
    cmd_path = os.path.join(run_dir, "run_command.sh")    
    cmd_parts = ["python", "-m", "src.train"]
    for key, value in vars(args).items():
        if key == "split_by_file":
            if value is False:
                cmd_parts.append("--no-split-by-file")
            continue

        flag = "--" + key.replace("_", "-")
        cmd_parts.append(flag)
        cmd_parts.append(str(value))

    cmd = " ".join(cmd_parts)
    with open(cmd_path, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(cmd + "\n")

    # Save weights only
    weights_path = os.path.join(run_dir, "gait_model_weights.pt")
    torch.save(model.state_dict(), weights_path)

    # Save full model (architecture + weights)
    full_model_path = os.path.join(run_dir, "gait_model_full.pt")
    torch.save(model, full_model_path)

    train_loss_values = stats.get("train_loss_values", [])
    train_acc_values = stats.get("train_acc_values", [])
    test_loss_values = stats.get("test_loss_values", [])
    test_acc_values = stats.get("test_acc_values", [])
    test_f1_values = stats.get("test_f1_values", [])

    # Save per-epoch metrics to CSV
    metrics_path = os.path.join(run_dir, "metrics.csv")
    with open(metrics_path, "w", newline="", encoding="utf-8") as f:
        f.write("epoch,train_loss,train_acc,test_loss,test_acc,test_f1\n")
        max_len = max(
            len(train_loss_values),
            len(train_acc_values),
            len(test_loss_values),
            len(test_acc_values),
            len(test_f1_values),
        )
        for epoch in range(max_len):
            row = [
                str(epoch + 1),
                str(train_loss_values[epoch]) if epoch < len(train_loss_values) else "",
                str(train_acc_values[epoch]) if epoch < len(train_acc_values) else "",
                str(test_loss_values[epoch]) if epoch < len(test_loss_values) else "",
                str(test_acc_values[epoch]) if epoch < len(test_acc_values) else "",
                str(test_f1_values[epoch]) if epoch < len(test_f1_values) else "",
            ]
            f.write(",".join(row) + "\n")

    # Confusion matrix plot
    all_labels = stats.get("all_labels", [])
    all_preds = stats.get("all_preds", [])
    if len(all_labels) > 0 and len(all_preds) > 0:
        cm = confusion_matrix(all_labels, all_preds)
        fig_cm, ax_cm = plt.subplots(figsize=(6, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm)
        disp.plot(cmap="Blues", ax=ax_cm, colorbar=False)
        ax_cm.set_title("Confusion Matrix")
        cm_plot_path = os.path.join(run_dir, "confusion_matrix.png")
        fig_cm.tight_layout()
        fig_cm.savefig(cm_plot_path, dpi=200)
        plt.close(fig_cm)

    # Accuracy plot
    if len(train_acc_values) > 0 or len(test_acc_values) > 0:
        fig_acc, ax_acc = plt.subplots()
        if len(train_acc_values) > 0:
            ax_acc.plot(train_acc_values, label="Train acc")
        if len(test_acc_values) > 0:
            ax_acc.plot(test_acc_values, label="Test acc")
        ax_acc.set_title("Accuracy Curves")
        ax_acc.set_xlabel("Epoch")
        ax_acc.set_ylabel("Accuracy")
        ax_acc.legend()
        acc_plot_path = os.path.join(run_dir, "accuracy.png")
        fig_acc.tight_layout()
        fig_acc.savefig(acc_plot_path, dpi=200)
        plt.close(fig_acc)

    # Loss plot
    if len(train_loss_values) > 0 or len(test_loss_values) > 0:
        fig_loss, ax_loss = plt.subplots()
        if len(train_loss_values) > 0:
            ax_loss.plot(train_loss_values, label="Train loss")
        if len(test_loss_values) > 0:
            ax_loss.plot(test_loss_values, label="Test loss")
        ax_loss.set_title("Loss Curves")
        ax_loss.set_xlabel("Epoch")
        ax_loss.set_ylabel("Loss")
        ax_loss.legend()
        loss_plot_path = os.path.join(run_dir, "loss.png")
        fig_loss.tight_layout()
        fig_loss.savefig(loss_plot_path, dpi=200)
        plt.close(fig_loss)

    print(f"Saved run artifacts to {run_dir}")

def main():
    args = parse_args()

    # Set fixed random seed for determinism  
    torch.manual_seed(args.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)

    # Define datasets and loaders
    train_set = GaitDataset(
        args.data_dir,
        train_split=args.train_split,
        split_by_file=args.split_by_file,
        split_seed=args.seed,
    )
    test_set = GaitDataset(
        args.data_dir,
        is_train=False,
        train_split=args.train_split,
        split_by_file=args.split_by_file,
        split_seed=args.seed,
    )

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    test_loader = DataLoader(test_set, batch_size=args.batch_size, shuffle=True)

    # Define model     
    model = CNN1D(num_features=train_set.feature_count, output_size=len(train_set.classes))
    optimizer = AdamW(params=model.parameters(), lr=args.learning_rate, weight_decay=args.weight_decay)
    loss_fn = nn.CrossEntropyLoss()   

    # Start the training loop
    results = train(
        model,
        args.device,
        args.epochs,
        optimizer,
        loss_fn,
        train_set.classes,
        train_loader,
        test_loader,
    )

    save_results(model, results, args.model_save_dir, args)

if __name__ == '__main__':
    main()
