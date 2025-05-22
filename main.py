import random
from locust import HttpUser, task, between

class KobraUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    def on_start(self):
        # Log in as either user1 or user2
        self.user = random.choice(['user1', 'user2'])
        self.token, self.user_uuid, self.wallet_id = self.login()

    def login(self):
        response = self.client.post('/auth/login', json={
            'email': f'{self.user}@example.com',
            'password': 'password123'
        })

        data = response.json()
        access_token = data['access_token']
        user_id = data['user']['id']
        wallet_id = data['user']['wallet']['id']

        return access_token, user_id, wallet_id

    @task(3)
    def get_balance(self):
        self.client.get('/wallet/balance', headers={'Authorization': f'Bearer {self.token}'})

    @task(2)
    def view_transactions(self):
        self.client.get('/transactions', headers={'Authorization': f'Bearer {self.token}'})

    @task(1)
    def transfer_money(self):
        other_user = 'user2' if self.user == 'user1' else 'user1'
        self.client.post('/transactions', json={
            'recipientEmail': other_user + '@example.com',
            'amount': 1
        }, headers={'Authorization': f'Bearer {self.token}'})

    @task(1)
    def deposit(self):
        self.client.post('/wallet/deposit', json={
            'walletId': self.wallet_id,
            'amount': random.randint(10, 1000)
        }, headers={'Authorization': f'Bearer {self.token}'})

    @task(1)
    def request_debin(self):
        self.client.post('/wallet/debin', json={
            'walletId': self.wallet_id,
            'amount': random.randint(10, 1000)
        }, headers={'Authorization': f'Bearer {self.token}'})
