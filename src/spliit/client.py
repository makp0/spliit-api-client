import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, Any
from urllib.parse import urljoin
from enum import Enum
import requests
import uuid

class SplitMode(str, Enum):
    """Split modes available in Spliit."""
    EVENLY = "EVENLY"
    BY_SHARES = "BY_SHARES"
    BY_PERCENTAGE = "BY_PERCENTAGE"
    BY_AMOUNT = "BY_AMOUNT"

OFFICIAL_INSTANCE = "https://spliit.app"

def format_expense_payload(
    group_id: str,
    title: str,
    amount: int,
    paid_by: str,
    paid_for: List[Tuple[str, int]],
    split_mode: SplitMode,
    expense_date: str,
    notes: str = "",
    category: int = 0,
) -> Dict[str, Any]:
    """Format the expense payload according to the API requirements."""
    # Convert paid_for to the expected format
    formatted_paid_for = []
    
    for participant_id, shares in paid_for:
        formatted_paid_for.append({
            "participant": participant_id,
            "shares": shares
        })

    # Create the expense form values
    expense_form_values = {
        "expenseDate": expense_date,
        "title": title,
        "category": category,
        "amount": amount,
        "paidBy": paid_by,
        "paidFor": formatted_paid_for,
        "splitMode": split_mode.value,
        "saveDefaultSplittingOptions": False,
        "isReimbursement": False,
        "documents": [],
        "notes": notes
    }

    return {
        "0": {
            "json": {
                "groupId": group_id,
                "expenseFormValues": expense_form_values,
                "participantId": "None"
            },
            "meta": {
                "values": {
                    "expenseFormValues.expenseDate": ["Date"]
                }
            }
        }
    }

@dataclass
class Spliit:
    """Client for interacting with the Spliit API."""
    
    group_id: str
    server_url: str = OFFICIAL_INSTANCE
    
    @property
    def base_url(self) -> str:
        """Get the base URL for API requests."""
        return urljoin(self.server_url, "/api/trpc")
    
    @classmethod
    def create_group(cls, name: str, currency: str = "$", server_url: str = OFFICIAL_INSTANCE, participants: List[Dict[str, str]] = None) -> "Spliit":
        """Create a new group and return a client instance for it."""
        if participants is None:
            participants = [{"name": "You"}]
            
        # Add UUIDs to participants
        for participant in participants:
            participant["id"] = str(uuid.uuid4())
            
        json_data = {
            "0": {
                "json": {
                    "groupFormValues": {
                        "name": name,
                        "currency": currency,
                        "information": "",
                        "participants": participants
                    }
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        url = f"{urljoin(server_url, '/api/trpc/groups.create')}"
        print("\nDebug: Request details:")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"JSON data: {json_data}")
        
        response = requests.post(
            url,
            json=json_data,
            headers=headers,
            params={"batch": "1"}
        )
        
        print(f"Debug: Response status: {response.status_code}")
        print(f"Debug: Response content: {response.content.decode()}")
        
        response.raise_for_status()
        group_id = response.json()[0]["result"]["data"]["json"]["groupId"]
        return cls(group_id=group_id, server_url=server_url)
    
    def get_group(self) -> Dict:
        """Get group details."""
        params_input = {
            "0": {"json": {"groupId": self.group_id}},
            "1": {"json": {"groupId": self.group_id}}
        }
        
        params = {
            "batch": "1",
            "input": json.dumps(params_input)
        }
        
        response = requests.get(
            f"{self.base_url}/groups.get,groups.getDetails",
            params=params
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]["group"]
    
    def get_username_id(self, name: str) -> Optional[str]:
        """Get participant ID by name."""
        group = self.get_group()
        for participant in group["participants"]:
            if name == participant["name"]:
                return participant["id"]
        return None
    
    def get_participants(self) -> Dict[str, str]:
        """Get all participants with their IDs."""
        group = self.get_group()
        return {
            participant["name"]: participant["id"]
            for participant in group["participants"]
        }
    
    def get_expenses(self) -> List[Dict]:
        """Get all expenses in the group."""
        params_input = {
            "0": {"json": {"groupId": self.group_id}}
        }
        
        params = {
            "batch": "1",
            "input": json.dumps(params_input)
        }
        
        response = requests.get(
            f"{self.base_url}/groups.expenses.list",
            params=params
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]["expenses"]
    
    def get_expense(self, expense_id: str) -> Dict:
        """
        Get details of a specific expense.
        
        Args:
            expense_id: The ID of the expense to retrieve
            
        Returns:
            Dict containing the expense details
        """
        params_input = {
            "0": {
                "json": {
                    "groupId": self.group_id,
                    "expenseId": expense_id
                }
            }
        }
        
        params = {
            "batch": "1",
            "input": json.dumps(params_input)
        }
        
        response = requests.get(
            f"{self.base_url}/groups.expenses.get",
            params=params
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]["expense"]
    
    def add_expense(
        self,
        title: str,
        amount: int,
        paid_by: str,
        paid_for: List[Tuple[str, int]],
        split_mode: SplitMode = SplitMode.EVENLY,
        expense_date: str = "2025-02-11T14:10:49.423Z",
        notes: str = "",
        category: int = 0
    ) -> str:
        """
        Add a new expense to the group.
        
        Args:
            title: Title of the expense
            amount: Amount in cents (e.g., 1350 for $13.50)
            paid_by: ID of the participant who paid
            paid_for: List of (participant_id, shares) tuples
            split_mode: How to split the expense (EVENLY, BY_SHARES, BY_PERCENTAGE, BY_AMOUNT)
            expense_date: ISO format date string (e.g., "2025-02-11T14:10:49.423Z")
            notes: Optional notes for the expense
            category: Expense category ID
        """
        params = {"batch": "1"}
        
        json_data = format_expense_payload(
            self.group_id,
            title,
            amount,
            paid_by,
            paid_for,
            split_mode,
            expense_date,
            notes,
            category
        )
        
        print("\nDebug: Request payload:")
        print(json.dumps(json_data, indent=2))
        
        response = requests.post(
            f"{self.base_url}/groups.expenses.create",
            params=params,
            json=json_data
        )
        
        print("\nDebug: Response status:", response.status_code)
        print("Debug: Response content:", response.content.decode())
        
        response.raise_for_status()
        return response.content.decode()

    def remove_expense(self, expense_id: str) -> Dict:
        """
        Remove an expense from the group.
        
        Args:
            expense_id: The ID of the expense to remove
            
        Returns:
            Dict containing the response data
        """
        params = {"batch": "1"}
        json_data = {
            "0": {
                "json": {
                    "groupId": self.group_id,
                    "expenseId": expense_id
                }
            }
        }
        
        response = requests.post(
            f"{self.base_url}/groups.expenses.delete",
            params=params,
            json=json_data
        )
        response.raise_for_status()
        return response.json()[0]["result"]["data"]["json"]