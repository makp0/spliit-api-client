import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import requests

from .utils import format_expense_payload

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
    
    def add_expense(
        self,
        title: str,
        paid_by: str,
        paid_for: List[Tuple[str, int]],
        amount: int = 1300,
        category: int = 0
    ) -> str:
        """Add a new expense to the group."""
        params = {"batch": "1"}
        
        json_data = format_expense_payload(
            self.group_id,
            title,
            paid_by,
            paid_for,
            amount,
            category
        )
        
        response = requests.post(
            f"{self.base_url}/groups.expenses.create",
            params=params,
            json=json_data
        )
        response.raise_for_status()
        return response.content.decode()