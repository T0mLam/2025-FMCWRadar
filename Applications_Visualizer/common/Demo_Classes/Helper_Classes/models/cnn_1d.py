from torch import nn

class CNN1D(nn.Module):
    """
    Reference:
    Machine Learning on the Edge with the mmWave Radar Device IWRL6432
    Figure 4-2. 1D CNN Architecture for Motion Classification
    https://www.ti.com/lit/wp/swra774/swra774.pdf
    """
    def __init__(self, num_features, output_size):
        super().__init__()
        self.conv_block1 = nn.Sequential(
            nn.Conv1d(num_features, 16, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(16)
        )
        self.conv_block2 = nn.Sequential(
            nn.Conv1d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(32)
        )
        self.conv_block3 = nn.Sequential(
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.BatchNorm1d(64)
        )
        
        self.pool = nn.AvgPool1d(kernel_size=2)
        self.gap = nn.AdaptiveAvgPool1d(1) # (B, C, T) -> (B, C, 1)

        self.classifier = nn.Sequential(
            nn.Flatten(), # (B, C, 1) -> (B, C)
            nn.Dropout(0.5),
            nn.Linear(64, output_size)
        )

    def forward(self, x):
        # Input shape: (batch, channel, length)
        out = self.conv_block1(x)
        out = self.conv_block2(out)
        out = self.conv_block3(out)
        out = self.pool(out)
        out = self.gap(out)
        out = self.classifier(out)
        return out 