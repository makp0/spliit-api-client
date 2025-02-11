import sys
from pathlib import Path
import time
import pytest
import json
import os
import uuid

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from spliit.client import Spliit, SplitMode, OFFICIAL_INSTANCE

def get_server_url():
    """Get the server URL from environment or use official instance."""
    return os.getenv("SPLIIT_SERVER_URL", OFFICIAL_INSTANCE)

def verify_expense(expense_details, test_case):
    """Helper function to verify expense details."""
    assert expense_details["title"] == test_case["title"]
    assert expense_details["amount"] == test_case["amount"]
    assert expense_details["paidBy"]["id"] == test_case["paid_by"]
    
    # Get shares for each participant
    shares = {
        paid["participantId"]: int(paid["shares"])  # API returns shares as strings
        for paid in expense_details["paidFor"]
    }
    
    # For even splits, verify all shares are 100
    if test_case["split_mode"] == SplitMode.EVENLY:
        for share in shares.values():
            assert share == 100
    
    for participant_id, expected_data in test_case["expected_shares"].items():
        assert shares[participant_id] == expected_data["shares"]

def test_expense_lifecycle():
    """Test the complete lifecycle of expenses with different split modes."""
    server_url = get_server_url()
    
    # Create a new group with test participants
    group_name = f"Test Group {uuid.uuid4()}"
    participants = [
        {"name": "Test User 1"},
        {"name": "Test User 2"}
    ]
    
    client = Spliit.create_group(
        name=group_name,
        server_url=server_url,
        participants=participants
    )
    
    # Get initial state
    participants = client.get_participants()
    
    # Get first two participants for testing
    participant_names = list(participants.keys())
    payer = participant_names[0]
    payer_id = participants[payer]
    participant1_id = participants[participant_names[0]]
    participant2_id = participants[participant_names[1]]
    
    test_cases = [
        {
            "title": f"Even Split Test {time.time()}",
            "amount": 5000,  # $50.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 100), (participant2_id, 100)],  # Each gets 100 shares
            "split_mode": SplitMode.EVENLY,
            "notes": "Testing even split between two participants",
            "expected_shares": {
                participant1_id: {"shares": 100},
                participant2_id: {"shares": 100}
            }
        },
        {
            "title": f"Percentage Split Test {time.time()}",
            "amount": 6000,  # $60.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 7000), (participant2_id, 3000)],  # 70% and 30%
            "split_mode": SplitMode.BY_PERCENTAGE,
            "notes": "Testing 70-30 percentage split",
            "expected_shares": {
                participant1_id: {"shares": 7000},  # 70%
                participant2_id: {"shares": 3000}   # 30%
            }
        },
        {
            "title": f"Amount Split Test {time.time()}",
            "amount": 400,  # $4.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 100), (participant2_id, 300)],  # $1.00, $1.50, $1.50
            "split_mode": SplitMode.BY_AMOUNT,
            "notes": "Testing exact amount split",
            "expected_shares": {
                participant1_id: {"shares": 100},  # $1.00
                participant2_id: {"shares": 300}   # $1.50
            }
        },
        {
            "title": f"Shares Split Test {time.time()}",
            "amount": 8000,  # $80.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 100), (participant2_id, 300)],  # 1:3:4 ratio
            "split_mode": SplitMode.BY_SHARES,
            "notes": "Testing share ratio split",
            "expected_shares": {
                participant1_id: {"shares": 100},  # 1 share
                participant2_id: {"shares": 300}   # 3 shares
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['split_mode'].value} split mode:")
        print(f"- Title: {test_case['title']}")
        print(f"- Amount: ${test_case['amount']/100:.2f}")
        
        # Add the expense
        new_expense_response = client.add_expense(
            title=test_case["title"],
            amount=test_case["amount"],
            paid_by=test_case["paid_by"],
            paid_for=test_case["paid_for"],
            split_mode=test_case["split_mode"],
            notes=test_case["notes"]
        )
        
        # Extract expense ID from response
        expense_id = json.loads(new_expense_response)[0]["result"]["data"]["json"]["expenseId"]
        print(f"- Created expense ID: {expense_id}")
        
        # Wait for the expense to be processed
        time.sleep(1)
        
        # Get and verify expense details
        expense_details = client.get_expense(expense_id)
        verify_expense(expense_details, test_case)
        print("- Expense verified successfully")
        
        # Remove the test expense
        removed = client.remove_expense(expense_id)
        assert removed is not None
        print("- Expense removed successfully")
        
        # Verify the expense was removed
        expenses = client.get_expenses()
        assert not any(exp["id"] == expense_id for exp in expenses)
        print("- Verified expense no longer exists") 