from mapper import AuthenticateRequest, AuthenticateResult, TransactionRequest, TransactionResult
import requests
from datetime import date


class Conscribo:
    def __init__(self, api_endpoint, api_key, api_passphrase):
        self.s = requests.session()
        self.status = 0
        self.ep = api_endpoint
        self.key = ""
        self.headers = {"X-Conscribo-API-Version": "0.20110602"}
        self.authenticate(api_key, api_passphrase)
        
    def request(self, request):
        return self.s.post(self.ep, request.get(), headers=self.headers)
        
    def authenticate(self, api_key, api_passphrase):
        req = AuthenticateRequest(api_key, api_passphrase)
        tod = self.request(req)
        tod.raise_for_status()
        res = AuthenticateResult(tod.text)
        res.raise_for_status()
        
        self.headers.update({
            "X-Conscribo-SessionId": res.sessionId
        })
        
    def transactions(self):
        req = TransactionRequest()
        req.filterDate(date(2017, 8, 1), date(2017, 8, 1))
        tod = self.request(req)
        tod.raise_for_status()
        res = TransactionResult(tod.text)
        res.raise_for_status()
        return res.transactions
        
    def add_change_transaction(self, transaction):
        
        
        
