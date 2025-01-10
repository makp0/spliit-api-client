#!/usr/bin/env python3
import requests
from dataclasses import dataclass
from typing import List, Tuple
import json
from datetime import datetime, UTC
CATEGORIES = {
    "Uncategorized": {
        "General": 0,
        "Payment": 1
    },
    "Entertainment": {
        "Entertainment": 2,
        "Games": 3,
        "Movies": 4,
        "Music": 5,
        "Sports": 6
    },
    "Food and Drink": {
        "Food and Drink": 7,
        "Dining Out": 8,
        "Groceries": 9,
        "Liquor": 10
    },
    "Home": {
        "Home": 11,
        "Electronics": 12,
        "Furniture": 13,
        "Household Supplies": 14,
        "Maintenance": 15,
        "Mortgage": 16,
        "Pets": 17,
        "Rent": 18,
        "Services": 19
    },
    "Life": {
        "Childcare": 20,
        "Clothing": 21,
        "Education": 22,
        "Gifts": 23,
        "Insurance": 24,
        "Medical Expenses": 25,
        "Taxes": 26
    },
    "Transportation": {
        "Transportation": 27,
        "Bicycle": 28,
        "Bus/Train": 29,
        "Car": 30,
        "Gas/Fuel": 31,
        "Hotel": 32,
        "Parking": 33,
        "Plane": 34,
        "Taxi": 35
    },
    "Utilities": {
        "Utilities": 36,
        "Cleaning": 37,
        "Electricity": 38,
        "Heat/Gas": 39,
        "Trash": 40,
        "TV/Phone/Internet": 41,
        "Water": 42
    }
}

def get_current_timestamp():
    # format '2024-11-14T22:26:58.244Z'
    now = datetime.now(UTC)
    return now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 10000:03d}Z"

@dataclass
class Spliit():
    group_id: str
    
    def get_group(self):
        params_input = {"0":{"json":{"groupId": self.group_id }},"1":{"json":{"groupId": self.group_id}}}
        params = {
            'batch': '1',
            "input": json.dumps(params_input)
        }

        response = requests.get('https://spliit.app/api/trpc/groups.get,groups.getDetails', params=params)
        return response.json()[0]['result']['data']['json']['group']

    def get_username_id(self, name: str):
        group = self.get_group()
        for participant in group["participants"]:
            if name == participant["name"]:
                return participant["id"]
        return None

    def get_participants(self):
        return_value = {}
        group = self.get_group()
        for participant in group["participants"]:
            return_value[participant["name"]] = participant["id"]
        return return_value

    def add_expense(self, title, paid_by: str, paid_for: List[Tuple[str,int]], amount: int = 1300, category = 0):
        # paid for is a list of participant ID and how much share
        params = {
            'batch': '1',
        }
        paid_for_format = []
        for participant in paid_for:
            paticipant_id = participant[0]
            paticipant_shares = participant[1]
            paid_for_format.append({"participant": paticipant_id, "shares": paticipant_shares})
            json_data = {
            '0': {
                'json': {
                    'groupId': self.group_id,
                    'expenseFormValues': {
                        'expenseDate': get_current_timestamp(),
                        'title': title,
                        'category': category,
                        'amount': amount,
                        'paidBy': paid_by,
                        'paidFor': paid_for_format,
                        'splitMode': 'EVENLY',
                        'saveDefaultSplittingOptions': False,
                        'isReimbursement': False,
                        'documents': [],
                        'notes': '',
                    },
                    'participantId': 'None',
                },
                'meta': {
                    'values': {
                        'expenseFormValues.expenseDate': [
                            'Date',
                        ],
                    },
                },
            },
        }

        response = requests.post('https://spliit.app/api/trpc/groups.expenses.create', params=params, json=json_data)
        return response.content.decode()



if __name__ == "__main__":
    a = Spliit(group_id = "3w4pzrjzIyu3xipruh_XR")
    # print(a.get_group())
    b = a.get_group()
    john = a.get_participants()["John"]
    print(a.add_expense("test exp", john, [(john, 100)], 1200))

