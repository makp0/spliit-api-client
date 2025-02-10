import sys
from pathlib import Path
import time
import pytest
import json

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from spliit.client import Spliit

# Test group ID - you might want to use a different one for testing
TEST_GROUP_ID = "nldjPQDNgMJaiwigAr4HE"

@pytest.fixture
def client():
    """Create a Spliit client instance for testing."""
    return Spliit(group_id=TEST_GROUP_ID)

def test_expense_lifecycle(client):
    """Test the complete lifecycle of an expense: create, verify, and delete."""
    # Get initial state
    group = client.get_group()
    participants = client.get_participants()
    initial_expenses = client.get_expenses()
    initial_count = len(initial_expenses)
    
    # Setup test data
    test_title = f"Test Expense {time.time()}"
    test_amount = 5000  # $50.00
    test_notes = "Integration test note with timestamp: " + str(time.time())
    participant_names = list(participants.keys())
    payer = participant_names[0]
    payer_id = participants[payer]
    
    # Create paid_for list with even split between first two participants
    paid_for = [
        (participants[participant_names[0]], 50),  # First participant pays 50 shares
        (participants[participant_names[1]], 50),  # Second participant pays 50 shares
    ]
    
    print(f"\nRunning integration test:")
    print(f"- Group: {group['name']}")
    print(f"- Currency: {group['currency']}")
    print(f"- Adding expense: {test_title}")
    print(f"- Paid by: {payer}")
    print(f"- Split evenly between: {participant_names[0]} and {participant_names[1]}")
    print(f"- Notes: {test_notes}")
    
    # Add the expense
    new_expense = client.add_expense(
        title=test_title,
        paid_by=payer_id,
        paid_for=paid_for,
        amount=test_amount,
        notes=test_notes
    )
    assert new_expense is not None
    
    # Verify the expense was added
    expenses = client.get_expenses()
    assert len(expenses) == initial_count + 1
    
    # Find our test expense
    test_expense = next(
        (exp for exp in expenses if exp["title"] == test_title),
        None
    )
    assert test_expense is not None
    
    # Get detailed expense info
    expense_details = client.get_expense(test_expense["id"])
    print("\nExpense details:")
    print(json.dumps(expense_details, indent=2))
    
    # Verify expense details
    assert expense_details["title"] == test_title
    assert expense_details["amount"] == test_amount
    assert expense_details["paidBy"]["name"] == payer
    assert expense_details["notes"] == test_notes
    
    # Create a map of participant IDs to names for verification
    participant_map = {id: name for name, id in participants.items()}
    
    # Verify shares
    shares = {participant_map[paid["participantId"]]: paid["shares"] for paid in expense_details["paidFor"]}
    assert shares[participant_names[0]] == 50
    assert shares[participant_names[1]] == 50
    
    print("- Expense verified successfully")
    print(f"- Notes verified: {expense_details['notes']}")
    
    # Remove the test expense
    removed = client.remove_expense(test_expense["id"])
    assert removed is not None
    
    # Verify the expense was removed
    final_expenses = client.get_expenses()
    assert len(final_expenses) == initial_count
    assert not any(exp["title"] == test_title for exp in final_expenses)
    
    print("- Test expense removed successfully") 