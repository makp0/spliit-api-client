#!/usr/bin/env python3
import requests
from dataclasses import dataclass
from typing import List, Tuple
import json
from datetime import datetime, UTC

def get_current_timestamp():
    # format '2024-11-14T22:26:58.244Z'
    now = datetime.now(UTC)
    return now.strftime('%Y-%m-%dT%H:%M:%S.') + f"{now.microsecond // 10000:03d}Z"

def format_expense_payload(group_id: str, title: str, paid_by: str, paid_for: List[Tuple[str, int]], amount: int, category: int, notes: str = ""):
    paid_for_format = []
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
                    'splitMode': 'EVENLY',
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