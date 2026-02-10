from torch import nn
import math
from torchinfo import summary


class CNN1D(nn.Module):
    """
    Reference:
    Machine Learning on the Edge with the mmWave Radar Device IWRL6432
    Figure 4-2. 1D CNN Architecture for Motion Classification
    https://www.ti.com/lit/wp/swra774/swra774.pdf
    """
    def __init__(self, num_features, time_steps, output_size):
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
        self.fc = nn.Linear(64 * math.floor(time_steps / 2), output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        # Input shape: (batch, channel, length)
        out = self.conv_block1(x)
        out = self.conv_block2(out)
        out = self.conv_block3(out)
        out = self.pool(out)

        # (batch, channel, length) -> (batch, channel * length)
        out = out.view(out.size(0), -1)
        out = self.fc(out)

        return self.softmax(out)
    

if __name__ == "__main__":
    model = CNN1D(64, 32, 5)
    summary(model, input_size=[32, 64, 32])