import os
import json
import pytest
import sys
import time
from unittest.mock import MagicMock, patch

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gemini_auth_service import GeminiAuthService

TEST_AUTH_FILE = "test_gemini_cli_auth.json"

@pytest.fixture
def auth_service():
    if os.path.exists(TEST_AUTH_FILE):
        os.remove(TEST_AUTH_FILE)
    service = GeminiAuthService(auth_file=TEST_AUTH_FILE)
    yield service
    if os.path.exists(TEST_AUTH_FILE):
        os.remove(TEST_AUTH_FILE)

def test_generate_pkce(auth_service):
    verifier, challenge = auth_service.generate_pkce()
    assert len(verifier) == 64
    assert len(challenge) > 0
    assert "=" not in challenge

def test_account_management(auth_service):
    record = {
        "access": "access1",
        "refresh": "refresh1",
        "expires": int(time.time() * 1000) + 3600000,
        "projectId": "proj1",
        "clientId": "client1",
        "clientSecret": "secret1",
        "email": "user1@example.com",
        "status": "valid"
    }
    auth_service._update_or_add_account(record)
    assert len(auth_service.accounts) == 1
    assert auth_service.accounts[0]["email"] == "user1@example.com"

    # Update same account
    record["access"] = "access2"
    auth_service._update_or_add_account(record)
    assert len(auth_service.accounts) == 1
    assert auth_service.accounts[0]["access"] == "access2"

def test_account_cycling(auth_service):
    acc1 = {"email": "u1", "status": "valid", "access": "a1", "refresh": "r1", "expires": 0, "projectId": "p1", "clientId": "c1", "clientSecret": None}
    acc2 = {"email": "u2", "status": "valid", "access": "a2", "refresh": "r2", "expires": 0, "projectId": "p2", "clientId": "c2", "clientSecret": None}
    acc3 = {"email": "u3", "status": "invalid", "access": "a3", "refresh": "r3", "expires": 0, "projectId": "p3", "clientId": "c3", "clientSecret": None}
    
    auth_service.accounts = [acc1, acc2, acc3]
    
    # Cycle should only return valid accounts
    assert auth_service.get_next_account()["email"] == "u1"
    assert auth_service.get_next_account()["email"] == "u2"
    assert auth_service.get_next_account()["email"] == "u1"
