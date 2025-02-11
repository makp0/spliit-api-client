import sys
from pathlib import Path
import time
import pytest
import json
import os
import uuid
from datetime import datetime, timezone, timedelta

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
    assert expense_details["notes"] == test_case["notes"]
    
    # Parse expense date from API response
    expense_date = datetime.strptime(
        expense_details["expenseDate"], 
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ).replace(tzinfo=timezone.utc)
    
    # Compare dates in UTC
    test_date = test_case["expense_date"].astimezone(timezone.utc)
    assert expense_date.date() == test_date.date()
    
    # Get shares for each participant
    shares = {
        paid["participantId"]: int(paid["shares"])  # API returns shares as strings
        for paid in expense_details["paidFor"]
    }
    
    for participant_id, expected_data in test_case["expected_shares"].items():
        assert shares[participant_id] == expected_data["shares"]

def test_expense_lifecycle():
    """Test the complete lifecycle of expenses with different split modes."""
    server_url = get_server_url()
    
    # First create a group using the static method
    group_name = f"Test Group {uuid.uuid4()}"
    participants = [
        {"name": "Test User 1"},
        {"name": "Test User 2"}
    ]
    
    temp_client = Spliit.create_group(
        name=group_name,
        server_url=server_url,
        participants=participants
    )
    
    # Now create a new client instance using the constructor
    client = Spliit(
        group_id=temp_client.group_id,
        server_url=server_url
    )
    
    # Verify both clients can access the same group
    group1 = temp_client.get_group()
    group2 = client.get_group()
    assert group1["id"] == group2["id"]
    assert group1["name"] == group2["name"]
    assert len(group1["participants"]) == len(group2["participants"])
    
    # Get initial state using the new client instance
    participants = client.get_participants()
    
    # Get first two participants for testing
    participant_names = list(participants.keys())
    payer = participant_names[0]
    payer_id = participants[payer]
    participant1_id = participants[participant_names[0]]
    participant2_id = participants[participant_names[1]]
    
    # Create test dates with timezone info
    base_date = datetime(2025, 2, 11, tzinfo=timezone.utc)
    test_dates = [
        base_date.replace(hour=14, minute=10, second=49, microsecond=423000),
        base_date.replace(hour=14, minute=11, second=50, microsecond=735000),
        base_date.replace(hour=14, minute=12, second=29, microsecond=246000),
        base_date.replace(hour=14, minute=13, second=15, microsecond=789000)
    ]
    
    # Also test with a non-UTC timezone
    local_tz = timezone(timedelta(hours=2))  # UTC+2
    test_dates.append(datetime(2025, 2, 11, 16, 15, 0, tzinfo=local_tz))  # Will be converted to 14:15 UTC
    
    test_cases = [
        {
            "title": f"Even Split Test {time.time()}",
            "amount": 5000,  # $50.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 100), (participant2_id, 100)],  # Each gets 100 shares
            "split_mode": SplitMode.EVENLY,
            "expense_date": test_dates[0],
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
            "expense_date": test_dates[1],
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
            "paid_for": [(participant1_id, 100), (participant2_id, 300)],  # $1.00, $3.00
            "split_mode": SplitMode.BY_AMOUNT,
            "expense_date": test_dates[2],
            "notes": "Testing exact amount split",
            "expected_shares": {
                participant1_id: {"shares": 100},  # $1.00
                participant2_id: {"shares": 300}   # $3.00
            }
        },
        {
            "title": f"Shares Split Test {time.time()}",
            "amount": 8000,  # $80.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 100), (participant2_id, 300)],  # 1:3 ratio
            "split_mode": SplitMode.BY_SHARES,
            "expense_date": test_dates[3],
            "notes": "Testing share ratio split",
            "expected_shares": {
                participant1_id: {"shares": 100},  # 1 share
                participant2_id: {"shares": 300}   # 3 shares
            }
        },
        {
            "title": f"Local Timezone Test {time.time()}",
            "amount": 9000,  # $90.00
            "paid_by": payer_id,
            "paid_for": [(participant1_id, 100), (participant2_id, 100)],  # Even split
            "split_mode": SplitMode.EVENLY,
            "expense_date": test_dates[4],  # Using local timezone
            "notes": "Testing expense with non-UTC timezone",
            "expected_shares": {
                participant1_id: {"shares": 100},
                participant2_id: {"shares": 100}
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\nTesting {test_case['split_mode'].value} split mode:")
        print(f"- Title: {test_case['title']}")
        print(f"- Amount: ${test_case['amount']/100:.2f}")
        print(f"- Date: {test_case['expense_date'].isoformat()}")
        
        # Add the expense
        new_expense_response = client.add_expense(
            title=test_case["title"],
            amount=test_case["amount"],
            paid_by=test_case["paid_by"],
            paid_for=test_case["paid_for"],
            split_mode=test_case["split_mode"],
            expense_date=test_case["expense_date"],
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