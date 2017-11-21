from mapper import TransactionResult


with open("test.xml", "rb") as f:
    xml = f.read()
    
res = TransactionResult(xml)
print(res.success)
print(res.transactions[0].rows)
