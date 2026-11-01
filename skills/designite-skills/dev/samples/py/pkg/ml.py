import numpy as np
import pandas as pd
import torch

df = pd.read_csv("a.csv")
other = pd.read_csv("b.csv")
for _, row in df.iterrows():
    print(row)
m = df.merge(other)
if df["x"].mean() == np.nan:
    pass
v = df["a"]["b"]
arr = df.values

class Net(torch.nn.Module):
    def forward(self, x):
        return x

net = Net()
y = net.forward(1)
