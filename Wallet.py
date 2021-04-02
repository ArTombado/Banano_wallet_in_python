import bananopy.banano as ban

from nanolib import *

seed = """put your seed here"""
private_key = generate_account_private_key(seed, 0)
address = 'ban' + generate_account_id(seed, 0)[3:]
representative = """put your representative here"""

def receive(amount, link):
  #Return the hash of the last account transaction. If the previous hash don't exist, the previous will be 0000000000000000000000000000000000000000000000000000000000000000.
  try:
    previous = ban.accounts_frontiers([address])["frontiers"][address]
  except:
    previous = '0'*64
  #Return the actual balance from the account.
  actual_balance = ban.account_balance(address)["balance"]
  #Create, sign and make the PoW of the transaction.
  block = Block(block_type="state",account="xrb"+address[3:],representative="xrb"+representative[3:],previous=previous, balance=actual_balance+amount,link=link)
  block.solve_work('fffffe0000000000')
  block.sign(private_key)
  #Create a dictionary of the block and send to the banano network.
  block1 = block.to_dict()
  print(ban.process("state", 'ban' + block1['account'][3:], block1['previous'], 'ban' + block1['representative'][3:], block1['balance'], block1['link'], block1['link_as_account'], block1['signature'], block1['work'], json_block = True))

def send(amount, link_as_account):
  #Return the hash of the last account transaction.
  previous = ban.accounts_frontiers([address])["frontiers"][address]
  #Return the actual balance from the account.
  actual_balance = ban.account_balance(address)["balance"]
  #Verify if the account have enought balance to make this transaction.
  if actual_balance >= amount:
    #Create, sign and make the PoW of the transaction.
    block = Block(block_type="state",account="xrb"+address[3:],representative="xrb"+representative[3:],previous=previous,link_as_account="xrb" + link_as_account[3:],balance=actual_balance-amount)
    block.solve_work('fffffe0000000000')
    block.sign(private_key)
    #Create a dictionary of the block and send to the banano network.
    block1 = block.to_dict()
    print(ban.process("state", 'ban' + block1['account'][3:], block1['previous'], 'ban' + block1['representative'][3:], block1['balance'], block1['link'], block1['link_as_account'], block1['signature'], block1['work'], json_block = True))
  else:
    print("You can't make this transaction.")

def receive_pendings():
  #Return the list of the pendings transactions in the account.
  pendings = ban.pending(address)['blocks']
  #Verify if has pendings. 
  if pendings != {}:
    #Receive all pending transactions.
    for x in pendings:
      #Return the amount of the pending transaction and  send to the network.
      bans = ban.block_info(x)['amount']
      receive(bans, x)
  else:
    print("There aren't pendings")
