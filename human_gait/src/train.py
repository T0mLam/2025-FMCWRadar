
import torch
import torch.nn as nn
import matplotlib.pyplot as plt

from torch.optim import SGD
from torchmetrics.classification import MulticlassF1Score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

from src.models.cnn_1d import CNN1D

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

def train(model, device, num_epoch, optimizer, class_data, train_dataLoader, test_dataLoader):
    # Define model size and send to CPU
    #model_0 = CNN1D(input_size=WINDOW_SIZE * FEATURE_COUNT, output_size=len(class_data))

    model.to(device)

    loss_fn = nn.CrossEntropyLoss()

    # setup the optimizer function  
    #optimizer = SGD(params=model_0.parameters(), lr=LEARNING_RATE)
    ## Alternative optimizer.
    # optimizer = Adam(params=model_0.parameters(), lr = LEARNING_RATE)   

    # setup F1 score 
    f1 = MulticlassF1Score(num_classes=len(class_data)).to(device)

    # Create empty loss lists to track values
    train_loss_values = []
    test_loss_values = []
    epoch_count = []

    ###############################
    # Start the main training loop 
    ###############################
    for epoch in range(num_epoch):
        ### Training
        model.train()
        train_loss = 0

        # Add a loop to loop through training batches
        for X, y in train_dataLoader:
            # 1. Forward pass
            X, y = X.to(device), y.squeeze().long().to(device)
            y_pred = model(X)

            # 2. Calculate loss (per batch)  
            loss = loss_fn(y_pred, y)

            # 3. Optimizer zero grad
            optimizer.zero_grad()

            # 4. Loss backward
            loss.backward()

            # 5. Optimizer step 
            optimizer.step()

            # 6. Accumulatively add up the loss per epoch 
            train_loss += loss.item()  

        # Divide total train loss by length of train dataloader (average loss per batch per epoch)
        train_loss /= len(train_dataLoader)

        ### Testing
        # Setup variables for accumulatively adding up loss and accuracy 
        test_loss, test_acc = 0, 0
        model.eval()

        all_preds = []
        all_labels = []
        distance = 0

        # Calculations on test metrics should happen inside torch.inference_mode()
        with torch.inference_mode():
            for X, y in test_dataLoader:
                # 1. Forward pass   
                X, y = X.to(device), y.squeeze().long().to(device)
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

                # Calculate Hamming Distance Between predictions and correct categories
                # a = predicted_labels.tolist()
                # b = y.tolist()

                # for i in range(len(a)):
                #     if a[i] != b[i]:
                #         distance += 1
                distance += (predicted_labels != y).sum().item()

            # Divide total test loss by length of test dataloader (per batch)
            test_loss /= len(test_dataLoader)

            # Divide total accuracy by length of test dataloader (per batch)
            test_acc /= len(test_dataLoader)

        ## Print out what's happening in the epoch loop
        if epoch % (num_epoch / 10) == 0:
            print(f"EPOCH: {epoch} | F1: {f1(test_pred, y):.5f}")
            print(f"Train loss: {train_loss:.5f} | Test loss: {test_loss:.5f}, Test acc: {test_acc:.2f}%")
            print(f'Distance: {distance}')

        # keep a history to view loss curves. Detach the tensors from the computation graphs.  
        epoch_count.append(epoch)
        train_loss_values.append(train_loss)
        test_loss_values.append(test_loss)

    # Compute confusion matrix
    cm = confusion_matrix(all_labels, all_preds)

    # Display confusion matrix
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap="Blues")
    plt.title("Confusion Matrix")
    plt.show()

    # Plot the loss curves
    plt.plot(epoch_count, train_loss_values, label="Train loss")
    plt.plot(epoch_count, test_loss_values, label="Test loss")
    plt.title("Training and test loss curves")
    plt.ylabel("Loss")
    plt.xlabel("Epochs")
    plt.legend()