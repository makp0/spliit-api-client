#!/usr/bin/env python3
import requests
from dataclasses import dataclass
from typing import List, Tuple, Union
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
    paid_by: str,
    paid_for: Union[List[str], List[Tuple[str, int]]],
    amount: int,
    category: int,
    notes: str = "",
    split_mode: SplitMode = SplitMode.EVENLY
):
    paid_for_format = []
    
    # Handle both list of IDs and list of tuples
    if split_mode == SplitMode.EVENLY:
        # For even split, each participant gets 1 share
        for participant_id in paid_for:
            paid_for_format.append({"participant": participant_id, "shares": 1})
    else:
        # For custom splits, unpack the tuples
        for participant in paid_for:
            participant_id = participant[0]
            participant_shares = participant[1]
            paid_for_format.append({"participant": participant_id, "shares": participant_shares})
    
    return {
        '0': {
            'json': {
                'groupId': group_id,
                'expenseFormValues': {
                    'expenseDate': get_current_timestamp(),
                    'title': title,
                    'category': category,
                    'amount': amount,
                    'paidBy': paid_by,
                    'paidFor': paid_for_format,
                    'splitMode': split_mode.value,
                    'saveDefaultSplittingOptions': False,
                    'isReimbursement': False,
                    'documents': [],
                    'notes': notes,
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