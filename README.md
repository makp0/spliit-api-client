# Spliit API Client

A Python client for interacting with the Spliit expense sharing application API.

This project is a fork of [guysoft/SpliitApi](https://github.com/guysoft/SpliitApi), with additional features and improvements.

## Features

- Create new groups with custom currency and participants
- Get group details and participants
- Add expenses with multiple split modes:
  - Even split
  - Split by percentage
  - Split by exact amounts
  - Split by shares
- Proper timezone support for expense dates
- Extensive expense categorization
- Add notes to expenses
- Get expense details
- Remove expenses
- List all expenses in a group

## Installation

```bash
! not functional. too lazy to figure what's wrong with this all eggs, hatchings, pypi and stuff
pip install spliit-api-client
```

## Usage

```python
from spliit import Spliit, CATEGORIES, SplitMode
from datetime import datetime, timezone

# Create a new group
client = Spliit.create_group(
    name="Trip to Paris",
    currency="€",
    participants=[
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"}
    ]
)

# Or initialize with existing group ID
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
    category=CATEGORIES["Food and Drink"]["Dining Out"],  # Use predefined categories
    notes="Great dinner!",  # Optional notes
    expense_date=datetime.now(timezone.utc)  # Timezone-aware dates
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
    split_mode=SplitMode.BY_PERCENTAGE,
    category=CATEGORIES["Food and Drink"]["Groceries"]
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
    split_mode=SplitMode.BY_AMOUNT,
    category=CATEGORIES["Entertainment"]["Movies"]
)

# Get all expenses
expenses = client.get_expenses()
for expense in expenses:
    print(f"\n{expense['title']} - {expense['amount']/100:.2f} {group['currency']}")
    print(f"Paid by: {expense['paidBy']['name']}")
    print(f"Date: {expense['expenseDate']}")

# Get specific expense details
expense_details = client.get_expense("expense_id")

# Remove an expense
client.remove_expense("expense_id")
```

## Available Categories

The client provides predefined expense categories that match Spliit's web interface:

```python
from spliit import CATEGORIES

# Examples of available categories:
CATEGORIES["Food and Drink"]["Dining Out"]  # ID: 8
CATEGORIES["Transportation"]["Taxi"]        # ID: 35
CATEGORIES["Home"]["Rent"]                 # ID: 18
CATEGORIES["Entertainment"]["Movies"]      # ID: 4
```

See the `CATEGORIES` constant in the code for the complete list of available categories.

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
