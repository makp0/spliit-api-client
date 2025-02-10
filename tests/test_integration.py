import sys
from pathlib import Path
import time
import pytest

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
    
    # Add the expense
    new_expense = client.add_expense(
        title=test_title,
        paid_by=payer_id,
        paid_for=paid_for,
        amount=test_amount
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
    
    # Verify expense details
    assert test_expense["title"] == test_title
    assert test_expense["amount"] == test_amount
    assert test_expense["paidBy"]["name"] == payer
    
    # Verify shares
    shares = {paid["participant"]["name"]: paid["shares"] for paid in test_expense["paidFor"]}
    assert shares[participant_names[0]] == 50
    assert shares[participant_names[1]] == 50
    
    print("- Expense verified successfully")
    
    # Remove the test expense
    removed = client.remove_expense(test_expense["id"])
    assert removed is not None
    
    # Verify the expense was removed
    final_expenses = client.get_expenses()
    assert len(final_expenses) == initial_count
    assert not any(exp["title"] == test_title for exp in final_expenses)
    
    print("- Test expense removed successfully") 