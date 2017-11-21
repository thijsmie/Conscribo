from api import Conscribo
import getpass


password = getpass.getpass()


api = Conscribo("https://secure.conscribo.nl/olympustest2/request.xml", "9ab3f7836ef80e0ebb9861b9609717b2", password)

transactions = api.transactions()
print(transactions[0].rows)
