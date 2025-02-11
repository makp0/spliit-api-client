# Spliit API Client

A Python client for interacting with the Spliit expense sharing application API.

This project is a fork of [guysoft/SpliitApi](https://github.com/guysoft/SpliitApi), with additional features and improvements.

## Installation

```bash
pip install spliit-api-client
```

## Usage

```python
from spliit.client import Spliit
from spliit.utils import SplitMode

# Initialize the client with your group ID
client = Spliit(group_id="your_group_id")

# Get group details
group = client.get_group()
print(f"Group: {group['name']}")

# Get participants
participants = client.get_participants()
print("Participants:", participants)

# Add an expense with even split (default)
expense = client.add_expense(
    title="Dinner",
    paid_by="participant_id",  # ID of the person who paid
    paid_for=[
        ("participant1_id", 1),  # Share values are ignored in EVENLY mode
        ("participant2_id", 1),
    ],
    amount=5000,  # $50.00 in cents
    notes="Great dinner!"  # Optional notes
)

# Add an expense with percentage split
expense = client.add_expense(
    title="Groceries",
    paid_by="participant_id",
    paid_for=[
        ("participant1_id", 70),  # 70% of the total
        ("participant2_id", 30),  # 30% of the total
    ],
    amount=3000,  # $30.00 in cents
    split_mode=SplitMode.BY_PERCENTAGE
)

# Add an expense with exact amounts
expense = client.add_expense(
    title="Movie tickets",
    paid_by="participant_id",
    paid_for=[
        ("participant1_id", 1500),  # $15.00 in cents
        ("participant2_id", 1500),  # $15.00 in cents
    ],
    amount=3000,  # $30.00 in cents
    split_mode=SplitMode.BY_AMOUNT
)

# Get all expenses
expenses = client.get_expenses()
for expense in expenses:
    print(f"\n{expense['title']} - {expense['amount']/100:.2f} {group['currency']}")
    print(f"Paid by: {expense['paidBy']['name']}")

# Get specific expense details
expense_details = client.get_expense("expense_id")

# Remove an expense
client.remove_expense("expense_id")
```

## Features

- Get group details and participants
- Add expenses with multiple split modes:
  - Even split
  - Split by percentage
  - Split by exact amounts
  - Split by shares
- Add notes to expenses
- Get expense details
- Remove expenses
- List all expenses in a group

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/makp0/spliit-api-client.git
cd spliit-api-client

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## License

MIT License