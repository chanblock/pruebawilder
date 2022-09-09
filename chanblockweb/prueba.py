
from pymongo import MongoClient

client = MongoClient("mongodb+srv://admin:uINsqkhy8mrC4rv2@clusterchanblock.9rmo2.mongodb.net/?retryWrites=true&w=majority")
db= client.chancblock.mtgox
list_walletsMongo= list(db.find({}))
print(list_walletsMongo)