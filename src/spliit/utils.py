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
