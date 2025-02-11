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
    paid_for: List[Union[str, Tuple[str, Union[int, float]]]],
    split_mode: SplitMode,
    notes: str = "",
    category: int = 0,
) -> Dict[str, Any]:
    """Format the expense payload according to the API requirements."""
    # Convert paid_for to the expected format based on split mode
    formatted_paid_for = []
    
    if split_mode == SplitMode.EVENLY:
        # For even splits, each participant gets 1 share
        for participant in paid_for:
            if isinstance(participant, tuple):
                participant_id = participant[0]
            else:
                participant_id = participant
            formatted_paid_for.append({
                "participant": participant_id,
                "shares": "1"
            })
    else:
        # For other split modes, handle the (participant_id, value) tuples
        total_shares = 0
        for participant_data in paid_for:
            if isinstance(participant_data, tuple):
                participant_id, value = participant_data
                if split_mode == SplitMode.BY_PERCENTAGE:
                    # For percentage splits, convert basis points to percentage
                    shares = str(int(value) // 100)  # Convert 7000 to 70
                    total_shares += int(shares)
                elif split_mode == SplitMode.BY_AMOUNT:
                    # For amount splits, convert to basis points
                    # Handle rounding to ensure total is exactly 10000
                    if participant_data == paid_for[-1]:  # Last participant
                        shares = str(10000 - total_shares)  # Use remaining points
                    else:
                        shares = str(round(value * 10000 / amount))  # Convert to basis points
                    total_shares += int(shares)
                else:  # SplitMode.BY_SHARES
                    # For share splits, use the share value directly
                    shares = str(value)
            else:
                participant_id = participant_data
                shares = "1"  # Default to 1 share if no value provided
                
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
                "participantId": paid_by
            },
            "meta": {
                "values": {
                    "expenseFormValues.expenseDate": ["Date"]
                }
            }
        }
    }