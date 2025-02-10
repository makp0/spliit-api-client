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

def format_expense_payload(group_id: str, title: str, paid_by: str, paid_for: List[Tuple[str, int]], amount: int, category: int):
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

def format_expense_with_shares_payload(
    group_id: str,
    title: str,
    paid_by: str,
    shares: List[Tuple[str, float]],  # List of (participant_id, share_percentage)
    amount: int,
    category: int = 0
) -> dict:
    """
    Format an expense payload with custom share percentages for each participant.
    
    Args:
        group_id: The Spliit group ID
        title: Title of the expense
        paid_by: ID of the participant who paid
        shares: List of tuples containing (participant_id, share_percentage)
                where share_percentage is a float between 0 and 1
        amount: Amount in cents
        category: Expense category ID
    
    Example:
        shares = [
            ("user1_id", 0.7),  # user1 pays 70%
            ("user2_id", 0.3),  # user2 pays 30%
        ]
    """
    # Convert percentages to shares (multiply by 100 for Spliit's format)
    total_shares = 100
    paid_for_format = []
    for participant_id, share_percentage in shares:
        share_amount = int(total_shares * share_percentage)
        paid_for_format.append({
            "participant": participant_id,
            "shares": share_amount
        })
    
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
                    'splitMode': 'SHARES',  # Using SHARES mode for custom split
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