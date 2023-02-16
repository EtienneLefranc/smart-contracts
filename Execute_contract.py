import marshal
import requests
import json
from flask import Flask, jsonify, request
from ecdsa import SigningKey
# improvements - created additional parameter file that is saved on blockchain in same transaction but separate (to not affect the hash value) this additional file records each time the contract is executed and avoids triggering twice in 1 day (and hence twice in 1 month)

# this file contains the contract and the relevant client side code required to send it to blockchain


def smart_contract():
    from ecdsa import SigningKey
    from datetime import date
    import pandas as pd

    class generate_user:

        def __init__(self, user_name):
            self.user_name = user_name
            # generate the users keys
            self.sign_key = SigningKey.generate()
            self.priv_key = self.sign_key
            self.pub_key = self.sign_key.get_verifying_key()
            # print(self.priv_key)

            # print(pub_key)

    user_one = generate_user("marie")
    print(user_one.user_name)
    print(user_one.priv_key)
    print(user_one.pub_key)

    class lease_contract:
        # we will have the terms and the two signatures
        # sign(self,privkey) and will fix the value
        # also make sure you are signing with the right one
        # and you will have a verify contact

        # initialise the contract
        def __init__(self, start_date, end_date, tenant_user: generate_user,
                     recipient_user: generate_user, monthly_rent):
            # data that we input
            self.tenant = tenant_user.pub_key
            self.recipient = recipient_user.pub_key
            self.start_date = start_date
            self.end_date = end_date
            self.monthly_rent = monthly_rent
            self.contract_terms = f"{self.start_date}{self.end_date}{self.tenant.to_der()}{self.recipient.to_der()}{self.monthly_rent}".encode(
                "ascii")
            self.timestamp = date.today()
            self.state = "Created"
            self.tenant_signature = None
            self.recipient_signature = None
            self.validated = False

        # do the signing in the contract
        def sign_contract(self, user_pub_key, user_signature):
            print(user_pub_key)
            print(self.tenant)
            if user_pub_key == self.tenant:
                if self.tenant.verify(user_signature, self.contract_terms):
                    self.tenant_signature = user_signature
                    if self.recipient_signature is not None:
                        return "Contract signed and ready to deploy."
                    else:
                        return "Contract signed by the tenant."

            if user_pub_key == self.recipient:
                if self.recipient.verify(user_signature, self.contract_terms):
                    self.recipient_signature = user_signature
                    if self.tenant_signature is not None:
                        self.validated = True
                        return "Contract signed by both parties."
                    else:
                        return "Contract not signed by both parties."

            return 'Error signing contract'

        @property
        def contract_state(self):
            # state created
            # state signed and confirm
            if self.state == "Ended":
                return self.state
            elif date.today() >= self.start_date and date.today() < self.end_date:
                self.state = "Ongoing"
                return "Ongoing"
            elif date.today() >= self.end_date:
                self.state = "Ended"
                return "Ended"
            return self.state

        def execute_monthly_payment(self):
            if date.today().day == 2 and self.contract_state == "Ongoing" and self.validated == True:
                index = blockchain.new_transaction(
                    str(self.tenant), str(self.recipient), int(self.monthly_rent))
                message = (
                    f'Validation finished and monthly payment sent to {self.recipient}. Transaction will be added to Block {index}')
                return message
            else:
                message = (
                    f"can't execute payment. Date today is {date.today()}, contract state is {self.contract_state} and validation is {self.validated}")
                return message

    # TEST

    # private activity
    user_one = generate_user("marie")
    print(user_one.user_name)
    print(user_one.priv_key)
    print(user_one.pub_key)

    user_two = generate_user("John")
    print(user_two.user_name)
    print(user_two.priv_key)
    print(user_two.pub_key)

    contract_new = lease_contract(pd.to_datetime("2022-1-1").date(), pd.to_datetime("2022-12-3").date(), user_one,
                                  user_two, 300)

    #sign in private
    user_one_signature = user_one.priv_key.sign(contract_new.contract_terms)
    user_two_signature = user_two.priv_key.sign(contract_new.contract_terms)

    # Check if ready to deploy
    print(contract_new.sign_contract(user_one.pub_key, user_one_signature))
    print(contract_new.sign_contract(user_two.pub_key, user_two_signature))

    result = lease_contract.execute_monthly_payment(contract_new)
    return(result)


def deploy(node, function):
    code = marshal.dumps(function.__code__)
    decoded = code.decode('latin-1')
    payload = json.dumps({"contract": decoded})
    #payload = json.dumps({"contract": 'gefnjdknfdkjn'})
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        "POST", f'http://{node}/deploy', headers=headers, data=payload)
    print(response.text)
    return(response.json()['hash'])


def mine(node):
    response = requests.get(f'http://{node}/mine')
    print(response.text)


def new_transaction(node, transaction):
    response = requests.post(f'http://{node}/transactions/new', transaction)
    print(response)


def chain(node):
    response = requests.get(f'http://{node}/chain')
    print(response)


def register(node1, node2):
    response = requests.get(f'http://{node1}/register', node2)
    print(response)


def resolve(node):
    response = requests.get(f'http://{node}/resolve')
    print(response)


def execute(node, hash):  # add subfunction
    payload = json.dumps({'hash': hash})  # add subfunction
    headers = {'Content-Type': 'application/json'}
    response = requests.request(
        "POST", f'http://{node}/execute', headers=headers, data=payload)
    print(response.text)


def test_deploy_execute(function):
    node = '138.195.245.83:5000'
    contract_id = deploy(node, function)
    mine(node)
    execute(node, contract_id)


test_deploy_execute(smart_contract)
