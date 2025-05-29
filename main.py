import random
from locust import HttpUser, task, between, events
from typing import Dict, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KobraUser(HttpUser):
    # UI Configuration
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    # Test Configuration
    min_transfer_amount = 1
    max_transfer_amount = 100
    min_deposit_amount = 10
    max_deposit_amount = 1000
    
    def on_start(self):
        """Initialize user session and login"""
        try:
            # Log in as either user1 or user2
            self.user = random.choice(['user1', 'user2'])
            self.token, self.user_uuid, self.wallet_id = self.login()
        except Exception as e:
            logger.error(f"Failed to initialize user session: {str(e)}")
            raise

    def login(self) -> tuple:
        """Login and return token, user_id, and wallet_id"""
        try:
            response = self.client.post('/auth/login', json={
                'email': f'{self.user}@example.com',
                'password': 'password123'
            })
            response.raise_for_status()
            
            data = response.json()
            return (
                data['access_token'],
                data['user']['id'],
                data['user']['wallet']['id']
            )
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise

    @task(3)
    def check_balance_and_transactions(self):
        """Check balance and recent transactions"""
        try:
            # First check balance
            balance_response = self.client.get(
                '/wallet/balance',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            balance_response.raise_for_status()
            
            # Then view recent transactions
            transactions_response = self.client.get(
                '/transactions',
                headers={'Authorization': f'Bearer {self.token}'}
            )
            transactions_response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to check balance/transactions: {str(e)}")

    @task(2)
    def perform_transfer(self):
        """Perform a money transfer to another user"""
        try:
            other_user = 'user2' if self.user == 'user1' else 'user1'
            amount = random.randint(self.min_transfer_amount, self.max_transfer_amount)
            
            response = self.client.post(
                '/transactions',
                json={
                    'recipientEmail': f'{other_user}@example.com',
                    'amount': amount
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Transfer failed: {str(e)}")

    @task(1)
    def perform_deposit(self):
        """Perform a deposit to the wallet"""
        try:
            amount = random.randint(self.min_deposit_amount, self.max_deposit_amount)
            
            response = self.client.post(
                '/wallet/deposit',
                json={
                    'walletId': self.wallet_id,
                    'amount': amount
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Deposit failed: {str(e)}")

    @task(1)
    def request_debin(self):
        """Request a debin payment"""
        try:
            amount = random.randint(self.min_deposit_amount, self.max_deposit_amount)
            
            response = self.client.post(
                '/wallet/debin',
                json={
                    'walletId': self.wallet_id,
                    'amount': amount
                },
                headers={'Authorization': f'Bearer {self.token}'}
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Debin request failed: {str(e)}")

# Add event handlers for better monitoring
@events.request_failure.add_listener
def on_request_failure(request_type, name, response_time, exception, **kwargs):
    logger.error(f"Request failed: {request_type} {name} - {str(exception)}") 