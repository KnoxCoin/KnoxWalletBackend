import web3
from flask import Flask, render_template

app= Flask(__name__)
import os
from twilio.rest import Client
import json
from web3 import Web3

w3= Web3(Web3.HTTPProvider('http://9c17-152-3-43-53.ngrok.io'))
account_sid = 'AC1eb1382555242af0a2d2285c48e0b9ab'
auth_token = '6360787bb87ddb6bcb23eb56f5fd68bc'
client = Client(account_sid, auth_token)
accts = w3.eth.get_accounts()
accts_dict ={}
latestBlock = w3.eth.get_block('latest')

for i in range(len(accts)):
    accts_dict[accts[i]]= w3.eth.get_balance(accts[i]),'+12488845909'

@app.route("/")
def homepage():
    return "add /history for transaction history or /notification to notify about recent transactions"

@app.route("/history/<acctId>")
def transactHistory(acctId):
    history = []
    endBlock = w3.eth.get_block('latest')['number']
    #startBlock = w3.eth.get_block('latest')['number']
    print("Searching for transactions to/from account: " + acctId)
    for i in range(endBlock-5, endBlock):
          block = w3.eth.get_block(i)
          if block is not None and block.transactions is not None:
              for i in block.transactions:
                  if w3.eth.get_transaction(i)['from'] == acctId:
                      history.append({"Transaction" : len(history), "Sender" : w3.eth.get_transaction(i)['from'],
                                                                      "Recipient" : w3.eth.get_transaction(i)['to'],
                                                                      "amount" : w3.eth.get_transaction(i)['value'],
                                                                      "timestamp": w3.eth.getBlock(w3.eth.getTransaction(i).blockNumber).timestamp})
                  if w3.eth.get_transaction(i)['to'] == acctId:
                      history.append({"Transaction" : len(history), "Sender" : w3.eth.get_transaction(i)['from'],
                                                                      "Recipient" : w3.eth.get_transaction(i)['to'],
                                                                      "amount" : w3.eth.get_transaction(i)['value'],
                                                                      "timestamp": w3.eth.getBlock(w3.eth.getTransaction(i).blockNumber).timestamp})
    return(json.dumps(history))
        
        
@app.route("/notification")
def notification():
    print("Getting latest transactions...")
    latestBlock = w3.eth.get_block('latest')
    for t in latestBlock.transactions:
        transact = w3.eth.get_transaction(t)
        sender = transact['from']
        recipient = transact['to']
        senderNumber = accts_dict[sender][1]
        recipientNumber = accts_dict[recipient][1]
        message = client.messages \
                .create(
                     body=("Your KnoxCoin public key: " + str(recipient) + "received " + str(transact['value'])
                     + " KnoxCoin from the following public key: " + str(sender)),
                     from_='+14845597653',
                     to=recipientNumber)
        print(message)
        message = client.messages \
                .create(
                     body=("Your KnoxCoin public key: " + str(sender) + "sent " + str(transact['value'])
                     + " KnoxCoin to the following public key: " + str(recipient)),
                     from_='+14845597653',
                     to=senderNumber)
        print(message)
    return "Ok"
@app.route("/verify/<sender>/<recipient>/<amount>/<datetime>")
def addTransact(sender, recipient, amount, datetime):
    ans=w3.eth.send_transaction({
        'to': recipient,
        'from': sender,
        'value': amount
        })
    senderNumber = accts_dict[sender][1]
    recipientNumber = accts_dict[recipient][1]
    message = client.messages \
            .create(
                body=("Your KnoxCoin public key: " + str(recipient) + "received " + str(amount)
                + " KnoxCoin from the following public key: " + str(sender)),
                from_='+14845597653',
                to=recipientNumber)
    print(message)
    message = client.messages \
            .create(
                body=("Your KnoxCoin public key: " + str(sender) + "sent " + str(amount)
                + " KnoxCoin to the following public key: " + str(recipient)),
                from_='+14845597653',
                to=senderNumber)
    print(message)
    return "Ok"
    
if __name__=="__main__":
    app.run(port='8080')

