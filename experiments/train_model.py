import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from app.core.model import SimpleClassifier

# synthetic dataset
X = np.random.rand(1000, 5)
y = (X.sum(axis=1) > 2.5).astype(float)  # simple rule

X = torch.tensor(X, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

model = SimpleClassifier(input_dim=5)
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

for epoch in range(200):
    optimizer.zero_grad()
    outputs = model(X)
    loss = criterion(outputs, y)
    loss.backward()
    optimizer.step()

    if epoch % 50 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

# save model
torch.save(model.state_dict(), "model.pt")
print("Model trained and saved.")
