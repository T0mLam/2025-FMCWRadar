import torch
from torch.utils.data import Dataset
import os 
import glob

class GaitDataset(Dataset):
    def __init__(self, data_dir, is_train=True, train_split=0.8):
        """
        data_dir: path to processed data (e.g., 'data/processed')
        is_train: If True, uses the first 80% of files. If False, uses the last 20%.
        """
        self.samples = []
        self.labels = []
        self.classes = {}

        class_names = sorted(os.listdir(data_dir))
        class_sample_counts = {}

        for i, class_name in enumerate(class_names):
            self.classes[i] = class_name
            
            class_path = os.path.join(data_dir, class_name)
            files = sorted(glob.glob(os.path.join(class_path, "*.pt")))

            split_idx = int(len(files) * train_split)

            if is_train:
                selected_files = files[:split_idx]
            else:
                selected_files = files[split_idx:]

            for file_path in selected_files:
                data, label = torch.load(file_path)

                class_sample_counts[class_name] = (
                    class_sample_counts.get(class_name, 0) + data.shape[0]
                )
                for i in range(data.shape[0]):
                    self.samples.append(data[i])
                    self.labels.append(label)

        self.feature_count = -1 if not self.samples else self.samples[0].shape[0]
        self.window_size = -1 if not self.samples else self.samples[0].shape[1]

        # Print dataset info 
        split_name = "Train" if is_train else "Val"
        counts_str = ", ".join(
            f"|{name}|={class_sample_counts.get(name, 0)}" for name in class_names
        )
        print(f"GaitDataset ({split_name}) sample counts: {counts_str}")

    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        return self.samples[idx], self.labels[idx]
