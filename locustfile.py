import random
import threading
from locust import HttpUser, task, between
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserCounter:
    def __init__(self, max_numbered_users=1000):
        self._counter = 0
        self._lock = threading.Lock()
        self.max_numbered_users = max_numbered_users
    
    def get_next_user(self):
        with self._lock:
            self._counter += 1
            if self._counter > self.max_numbered_users:
                self._counter = 1
            return self._counter

user_counter = UserCounter(max_numbered_users=1000)

class WalletUser(HttpUser):
    wait_time = between(1, 4)

    def on_start(self):
        try:
            user_number = user_counter.get_next_user()
            self.user = f'user{user_number}'
            self.user_email = f'{self.user}@example.com'

            response = self.client.post('/auth/login', json={
                'email': self.user_email,
                'password': 'Password123!'
            })
            response.raise_for_status()
            
            data = response.json()
            self.token = data['access_token']

            initial_deposit = random.randint(200, 500)
            deposit_response = self.client.post('/wallet/deposit', json={
                'email': self.user_email,
                'amount': initial_deposit
            })
            deposit_response.raise_for_status()
            
            logger.info(f"Usuario {self.user} inicializado con ${initial_deposit}")
            
        except Exception as e:
            logger.error(f"Error inicializando usuario {self.user}: {str(e)}")
            raise

    @task(5)
    def check_balance(self):
        try:
            response = self.client.get('/wallet/balance',
                headers={'Authorization': f'Bearer {self.token}'})
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error checking balance for {self.user}: {str(e)}")

    @task(3)
    def view_transactions(self):
        try:
            response = self.client.get('/transactions',
                headers={'Authorization': f'Bearer {self.token}'})
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error viewing transactions for {self.user}: {str(e)}")

    @task(2)
    def transfer_money(self):
        try:
            target_user_number = random.randint(1, user_counter.max_numbered_users)
            target_email = f'user{target_user_number}@example.com'
            
            # Ensure not transferring to self
            if target_email == self.user_email:
                return
            
            amount = random.randint(5, 50)
            
            response = self.client.post('/transactions', json={
                'recipientEmail': target_email,
                'amount': amount
            }, headers={'Authorization': f'Bearer {self.token}'})
            response.raise_for_status()
            
            logger.info(f"{self.user} transfirió ${amount} a user{target_user_number}")
            
        except Exception as e:
            logger.error(f"Error in transfer for {self.user}: {str(e)}")

    @task(1)
    def deposit_money(self):
        try:
            amount = random.randint(10, 100)
            response = self.client.post('/wallet/deposit', json={
                'email': self.user_email,
                'amount': amount
            })
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error in deposit for {self.user}: {str(e)}")

    @task(1)
    def request_debin(self):
        try:
            amount = random.randint(20, 100)
            response = self.client.post('/wallet/debin', json={
                'amount': amount
            }, headers={'Authorization': f'Bearer {self.token}'})
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error in debin request for {self.user}: {str(e)}")

