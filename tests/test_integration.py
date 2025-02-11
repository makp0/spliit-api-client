import sys
from pathlib import Path
import time
import pytest
import json

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from spliit.client import Spliit, SplitMode

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
    
    # Setup test data
    test_title = f"Test Expense {time.time()}"
    test_amount = 5000  # $50.00
    test_notes = "Integration test note with timestamp: " + str(time.time())
    participant_names = list(participants.keys())
    payer = participant_names[0]
    payer_id = participants[payer]
    
    # Create paid_for list with even split between first two participants
    paid_for = [
        participants[participant_names[0]],
        participants[participant_names[1]],
    ]
    
    # Add the expense
    new_expense_response = client.add_expense(
        title=test_title,
        paid_by=payer_id,
        paid_for=paid_for,
        amount=test_amount,
        notes=test_notes
    )
    
    # Extract expense ID from response
    expense_id = json.loads(new_expense_response)[0]["result"]["data"]["json"]["expenseId"]
    
    # Wait for the expense to be processed
    time.sleep(1)
    
    # Get detailed expense info
    expense_details = client.get_expense(expense_id)
    
    # Verify expense details
    assert expense_details["title"] == test_title
    assert expense_details["amount"] == test_amount
    assert expense_details["paidBy"]["name"] == payer
    assert expense_details["notes"] == test_notes
    
    # Create a map of participant IDs to names for verification
    participant_map = {id: name for name, id in participants.items()}
    
    # Verify shares are equal for even split
    shares = {participant_map[paid["participantId"]]: paid["shares"] for paid in expense_details["paidFor"]}
    total_shares = sum(shares.values())
    expected_share = total_shares / len(shares)
    for share in shares.values():
        assert share == expected_share
    
    # Remove the test expense
    removed = client.remove_expense(expense_id)
    assert removed is not None
    
    # Verify the expense was removed
    expenses = client.get_expenses()
    assert not any(exp["id"] == expense_id for exp in expenses) 