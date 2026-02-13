import torch
from torch.utils.data import Dataset
import os 
import glob

class GaitDataset(Dataset):
    def __init__(self, data_dir, is_train=True, train_split=0.8, split_by_file=True, split_seed=None):
        self.samples = []
        self.labels = []
        self.classes = {}

        class_names = sorted(os.listdir(data_dir))
        class_sample_counts = {}

        for class_idx, class_name in enumerate(class_names):
            self.classes[class_idx] = class_name
            
            class_path = os.path.join(data_dir, class_name)
            files = sorted(glob.glob(os.path.join(class_path, "*.pt")))
            
            if split_by_file:
                split_idx = int(len(files) * train_split)
                selected_files = files[:split_idx] if is_train else files[split_idx:]

                for file_path in selected_files:
                    data, label = torch.load(file_path)

                    class_sample_counts[class_name] = (
                        class_sample_counts.get(class_name, 0) + data.shape[0]
                    )
                    for sample_idx in range(data.shape[0]):
                        self.samples.append(data[sample_idx])
                        self.labels.append(label)
            else:
                class_samples = []
                class_labels = []

                for file_path in files:
                    data, label = torch.load(file_path)
                    for sample_idx in range(data.shape[0]):
                        class_samples.append(data[sample_idx])
                        class_labels.append(label)

                if class_samples:
                    base_seed = 0 if split_seed is None else int(split_seed)
                    gen = torch.Generator()
                    gen.manual_seed(base_seed + (class_idx + 1) * 1000003)
                    perm = torch.randperm(len(class_samples), generator=gen).tolist()
                    split_idx = int(len(class_samples) * train_split)
                    selected_idx = perm[:split_idx] if is_train else perm[split_idx:]

                    class_sample_counts[class_name] = len(selected_idx)
                    for idx in selected_idx:
                        self.samples.append(class_samples[idx])
                        self.labels.append(class_labels[idx])
                else:
                    class_sample_counts[class_name] = 0

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
