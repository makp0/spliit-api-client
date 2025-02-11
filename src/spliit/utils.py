#!/usr/bin/env python3
import requests
from dataclasses import dataclass
from typing import List, Tuple, Union, Dict, Any
import json
from datetime import datetime, UTC
from enum import Enum, auto

class SplitMode(str, Enum):
    """Split modes available in Spliit."""
    EVENLY = "EVENLY"
    BY_SHARES = "BY_SHARES"
    BY_PERCENTAGE = "BY_PERCENTAGE"
    BY_AMOUNT = "BY_AMOUNT"

def get_current_timestamp():
    # format '2024-11-14T22:26:58.244Z'
    now = datetime.now(UTC)
    return now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 10000:03d}Z"

def format_expense_payload(
    group_id: str,
    title: str,
    amount: int,
    paid_by: str,
    paid_for: List[Tuple[str, int]],
    split_mode: SplitMode,
    notes: str = "",
    category: int = 0,
) -> Dict[str, Any]:
    """Format the expense payload according to the API requirements."""
    # Convert paid_for to the expected format based on split mode
    formatted_paid_for = []
    
    for participant_id, shares in paid_for:
        formatted_paid_for.append({
            "participant": participant_id,
            "shares": shares
        })

    # Create the expense form values
    expense_form_values = {
        "expenseDate": get_current_timestamp(),
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