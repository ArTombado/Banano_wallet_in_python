from ast import literal_eval
from nanolib import *
import os

seed = """Put your seed here"""
private_key = generate_account_private_key(seed, 0)
address = 'ban' + generate_account_id(seed, 0)[3:]
representative = """Put your representative here"""

def balance(account):
  #Return the balance of an account in a dictionary.
  return literal_eval(os.popen('curl -g -d \'{"action":"account_balance","account":"' + account +'"}\' \'https://api-beta.banano.cc:443\'').read())

def history(account, count):
  #Return the history of an account in a dictionary.
  return literal_eval(os.popen('curl -g -d \'{"action":"account_history","account":"' + account +'", "count": "' + count + '"}\' \'https://api-beta.banano.cc:443\'').read())

def pending(account):
  #Return the pending transactions of an account in a dictionary.
  return literal_eval(os.popen('curl -g -d \'{"action":"pending","account":"' + account +'"}\' \'https://api-beta.banano.cc:443\'').read())

def block_info(hash):
  #Return the info of a block in a dictionary.
  return literal_eval(os.popen('curl -g -d \'{"action":"block_info","json_block":"true","hash":"' + hash +'"}\' \'https://api-beta.banano.cc:443\'').read())

def process(account, previous, representative, balance, link,link_as_account, signature, work):
  #Send a transaction to the banano network.
  return literal_eval(os.popen('''curl -g -d '{"action": "process","json_block": "true","block": "{\\"type\\": \\"state\\",\\"account\\": \\"''' + account + '''\\",\\"previous\\": \\"''' + previous + '''\\",\\"representative\\": \\"''' + representative + '''\\",\\"balance\\": \\"''' + balance + '''\\",\\"link\\": \\"''' + link + '''\\",\\"link_as_account\\": \\"''' + link_as_account +'''\\",\\"signature\\": \\"''' + signature + '''\\",\\"work\\": \\"''' + work + '''\\"}"}' -H "Content-Type: application/json" 'https://api-beta.banano.cc:443'
''').read())

def receive(amount, link):
  #Return the hash of the last account transaction. If the previous hash don't exist, the previous will be 0000000000000000000000000000000000000000000000000000000000000000.
  try:
    previous = str(history(address, '1')['history'][0]['hash'])
  except:
    previous = '0'*64
  #Return the actual balance from the account.
  actual_balance = int(balance(address)['balance'])
  #Create, sign and make the PoW of the transaction.
  block = Block(block_type="state",account="xrb"+address[3:],representative="xrb"+address[3:],previous=previous, balance=actual_balance+amount,link=link)
  block.solve_work('fffffe0000000000')
  block.sign(private_key)
  #Create a dictionary of the block and send to the banano network.
  block1 = literal_eval(block.json())
  print(process('ban' + block1['account'][3:], block1['previous'], 'ban' + block1['representative'][3:], block1['balance'], block1['link'], block1['link_as_account'], block1['signature'], block1['work']))

def send(amount, link_as_account):
  #Return the hash of the last account transaction.
  previous = str(history(address, '1')['history'][0]['hash'])
  #Return the actual balance from the account.
  actual_balance = int(balance(address)['balance'])
  #Verify if the account have enought balance to make this transaction.
  if actual_balance >= amount:
    #Create, sign and make the PoW of the transaction.
    block = Block(block_type="state",account="xrb"+address[3:],representative="xrb"+address[3:],previous=previous,link_as_account="xrb" + link_as_account[3:],balance=actual_balance-amount)
    block.solve_work('fffffe0000000000')
    block.sign(private_key)
    #Create a dictionary of the block and send to the banano network.
    block1 = literal_eval(block.json())
    print(process('ban' + block1['account'][3:], block1['previous'], 'ban' + block1['representative'][3:], block1['balance'], block1['link'], block1['link_as_account'], block1['signature'], block1['work']))
  else:
    print("You can't make this transaction.")

def receive_pendings():
  #Return the list of the pendings transactions in the account.
  pendings = pending(address)['blocks']
  #Verify if has pendings. 
  if pendings != '':
    #Receive all pending transactions.
    for x in pendings:
      #Return the amount of the pending transaction and  send to the network.
      bans = int(block_info(x)['amount'])
      receive(bans, x)
  else:
    print("There aren't pendings")
