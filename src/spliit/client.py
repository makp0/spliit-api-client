import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, overload

import requests

from .utils import format_expense_payload, SplitMode

@dataclass
class Spliit:
    """Client for interacting with the Spliit API."""
    
    group_id: str
    base_url: str = "https://spliit.app/api/trpc"
    
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
    
    @overload
    def add_expense(
        self,
        title: str,
        paid_by: str,
        paid_for: List[str],
        amount: int,
        category: int = 0,
        notes: str = ""
    ) -> str:
        """
        Add a new expense to the group with even split.
        
        Args:
            title: Title of the expense
            paid_by: ID of the participant who paid
            paid_for: List of participant IDs to split evenly between
            amount: Amount in cents (e.g., 1350 for $13.50)
            category: Expense category ID
            notes: Optional notes for the expense
        """
        ...

    @overload
    def add_expense(
        self,
        title: str,
        paid_by: str,
        paid_for: List[Tuple[str, int]],
        amount: int,
        category: int = 0,
        notes: str = "",
        split_mode: SplitMode = SplitMode.EVENLY
    ) -> str:
        """
        Add a new expense to the group.
        
        Args:
            title: Title of the expense
            paid_by: ID of the participant who paid
            paid_for: List of tuples containing (participant_id, shares/percentage/amount)
            amount: Amount in cents (e.g., 1350 for $13.50)
            category: Expense category ID
            notes: Optional notes for the expense
            split_mode: How to split the expense (EVENLY, BY_SHARES, BY_PERCENTAGE, BY_AMOUNT)
        """
        ...

    def add_expense(
        self,
        title: str,
        paid_by: str,
        paid_for: Union[List[str], List[Tuple[str, int]]],
        amount: int,
        category: int = 0,
        notes: str = "",
        split_mode: SplitMode = SplitMode.EVENLY
    ) -> str:
        """
        Add a new expense to the group.
        
        Args:
            title: Title of the expense
            paid_by: ID of the participant who paid
            paid_for: Either a list of participant IDs for even split,
                     or a list of (participant_id, shares) tuples for custom split
            amount: Amount in cents (e.g., 1350 for $13.50)
            category: Expense category ID
            notes: Optional notes for the expense
            split_mode: How to split the expense (EVENLY, BY_SHARES, BY_PERCENTAGE, BY_AMOUNT)
        """
        params = {"batch": "1"}
        
        json_data = format_expense_payload(
            self.group_id,
            title,
            paid_by,
            paid_for,
            amount,
            category,
            notes,
            split_mode
        )
        
        response = requests.post(
            f"{self.base_url}/groups.expenses.create",
            params=params,
            json=json_data
        )
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