import torch
from torch.utils.data import Dataset
import os 
import glob

class GaitDataset(Dataset):
    def __init__(self, data_dir, is_train=True, val_split=0.2):
        """
        data_dir: path to processed data (e.g., 'data/processed')
        is_train: If True, uses the first 80% of files. If False, uses the last 20%.
        """
        self.samples = []
        self.labels = []

        classes = sorted(os.listdir(data_dir))

        for class_name in classes:
            class_path = os.path.join(data_dir, class_name)
            files = sorted(glob.glob(os.path.join(class_path, "*.pt")))

            split_idx = int(len(files) * (1 - val_split))

            if is_train:
                selected_files = files[:split_idx]
            else:
                selected_files = files[split_idx:]

            print(f"Loading {len(selected_files)} for class {class_name} ({"Train" if is_train else "Val"})")

            for file_path in selected_files:
                data, label = torch.load(file_path)

                for i in range(data.shape[0]):
                    self.samples.append(data[i])
                    self.labels.append(label)

    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]