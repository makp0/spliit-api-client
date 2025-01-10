# Spliit API Client

A Python client for interacting with the Spliit API.

## Installation

```bash
pip install spliit
```

## Usage

```python
from spliit import Spliit

# Initialize the client
client = Spliit(group_id="your_group_id")

# Get group information
group = client.get_group()

# Get participants
participants = client.get_participants()

# Get categories
from spliit import CATEGORIES

# Add an expense
john_id = client.get_username_id("John")
client.add_expense(
    title="Dinner",
    paid_by=john_id,
    paid_for=[(john_id, 100)],
    amount=1200,
    category=CATEGORIES['Home']['Electronics']
)
```