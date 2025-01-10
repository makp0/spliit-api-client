import json
import pytest
from datetime import datetime, UTC, timezone
from spliit import Spliit, CATEGORIES

def test_get_group(mock_requests):
    """Test the get_group method."""
    mock_get, _ = mock_requests
    mock_get.return_value.json.return_value = [{
        "result": {
            "data": {
                "json": {
                    "group": {
                        "id": "test_group",
                        "name": "Test Group",
                        "participants": [
                            {"id": "user1", "name": "John"},
                            {"id": "user2", "name": "Jane"}
                        ]
                    }
                }
            }
        }
    }]

    client = Spliit(group_id="test_group")
    result = client.get_group()

    assert result["id"] == "test_group"
    assert result["name"] == "Test Group"
    assert len(result["participants"]) == 2
    
    # Verify the API call
    mock_get.assert_called_once()
    call_args = mock_get.call_args
    assert "groups.get,groups.getDetails" in call_args[0][0]
    assert "batch" in call_args[1]["params"]

def test_get_username_id(mock_requests):
    """Test the get_username_id method."""
    mock_get, _ = mock_requests
    mock_get.return_value.json.return_value = [{
        "result": {
            "data": {
                "json": {
                    "group": {
                        "participants": [
                            {"id": "user1", "name": "John"},
                            {"id": "user2", "name": "Jane"}
                        ]
                    }
                }
            }
        }
    }]

    client = Spliit(group_id="test_group")
    
    # Test existing user
    assert client.get_username_id("John") == "user1"
    
    # Test non-existent user
    assert client.get_username_id("Bob") is None

def test_get_participants(mock_requests):
    """Test the get_participants method."""
    mock_get, _ = mock_requests
    mock_get.return_value.json.return_value = [{
        "result": {
            "data": {
                "json": {
                    "group": {
                        "participants": [
                            {"id": "user1", "name": "John"},
                            {"id": "user2", "name": "Jane"}
                        ]
                    }
                }
            }
        }
    }]

    client = Spliit(group_id="test_group")
    participants = client.get_participants()
    
    assert participants == {
        "John": "user1",
        "Jane": "user2"
    }

def test_add_expense(mock_requests):
    """Test the add_expense method."""
    _, mock_post = mock_requests
    mock_post.return_value.content.decode.return_value = "Success"

    client = Spliit(group_id="test_group")
    result = client.add_expense(
        title="Test Expense",
        paid_by="user1",
        paid_for=[("user1", 50), ("user2", 50)],
        amount=1000,
        category=CATEGORIES["Food and Drink"]["Dining Out"]
    )

    assert result == "Success"
    
    # Verify the API call
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert "groups.expenses.create" in call_args[0][0]
    
    # Verify request payload
    json_data = call_args[1]["json"]
    expense_values = json_data["0"]["json"]["expenseFormValues"]
    assert expense_values["title"] == "Test Expense"
    assert expense_values["amount"] == 1000
    assert expense_values["paidBy"] == "user1"
    assert len(expense_values["paidFor"]) == 2
    assert expense_values["category"] == CATEGORIES["Food and Drink"]["Dining Out"]

def test_categories_structure():
    """Test the CATEGORIES constant structure."""
    # Test main categories exist
    expected_categories = {
        "Uncategorized",
        "Entertainment",
        "Food and Drink",
        "Home",
        "Life",
        "Transportation",
        "Utilities"
    }
    assert set(CATEGORIES.keys()) == expected_categories
    
    # Test some specific subcategories
    assert CATEGORIES["Food and Drink"]["Dining Out"] == 8
    assert CATEGORIES["Transportation"]["Car"] == 30
    assert CATEGORIES["Utilities"]["Water"] == 42
    
    # Test value ranges
    all_values = [
        value
        for category in CATEGORIES.values()
        for value in category.values()
    ]
    assert min(all_values) == 0
    assert max(all_values) == 42
    assert len(set(all_values)) == 43  # Check all values are unique

# tests/test_utils.py
from spliit.utils import get_current_timestamp
from datetime import datetime, UTC

def test_get_current_timestamp():
    """Test the get_current_timestamp function."""
    timestamp = get_current_timestamp()
    
    # Verify format
    assert len(timestamp) == 24  # Length of ISO format with milliseconds
    assert timestamp.endswith('Z')  # UTC timezone marker
    assert 'T' in timestamp  # ISO datetime separator
    
    # Verify it can be parsed back to datetime
    dt = datetime.strptime(
        timestamp,
        '%Y-%m-%dT%H:%M:%S.%fZ'
    ).replace(tzinfo=timezone.utc)  # Explicitly attach UTC timezone
    
    assert dt.tzinfo is not None  # Should be timezone-aware
    assert dt.tzinfo == timezone.utc  # Should be UTC specifically
