import sys
from pathlib import Path
import json

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from spliit.client import Spliit

# Your group ID from Spliit
GROUP_ID = "nldjPQDNgMJaiwigAr4HE"

# Initialize the client
client = Spliit(group_id=GROUP_ID, server_url="https://spliit.app")

# Get group details
group = client.get_group()
print("Group details:", group)

# Get all participants
participants = client.get_participants()
print("\nParticipants:", participants)

# Get all expenses
expenses = client.get_expenses()
print("\nExpenses:")
for expense in expenses:
    print(f"\n{expense['title']} - {expense['amount']/100:.2f} {group['currency']}")
    print(f"Paid by: {expense['paidBy']['name']}")
    print("Paid for:")
    for paid_for in expense['paidFor']:
        share_amount = (expense['amount'] * paid_for['shares']) / 300  # 300 is total shares (100 per person)
        print(f"  - {paid_for['participant']['name']}: {share_amount/100:.2f} {group['currency']}")

# Example of adding an expense (commented out - uncomment and modify as needed)
# Add an expense where someone paid for others

participant_names = list(participants.keys())
expense = client.add_expense(
    title="Dinner",
    paid_by="John",  # Name of the person who paid
    paid_for=[(participants[participant_names[0]], 2000), (participants[participant_names[1]], 2000)],  # List of (name, amount in cents)
    amount=4000,  # Total amount in cents (40.00)
    category=0
)
print("\nAdded expense:", expense)