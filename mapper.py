import re
import datetime

from lxml import etree


def parse_result(xml):
    return etree.XML(xml)
    
def pretty_print(res):
    print(etree.tostring(res, pretty_print=True, encoding='unicode'))
    
    
class Result:
    def __init__(self, xml):
        tree = etree.fromstring(xml.encode())
        self.root = tree
        
    @property
    def success(self):
        return self.root.xpath("success")[0].text == "1"
        
    @property
    def notifications(self):
        return [child.text for child in self.root.xpath("notifications/notification")]
        
    def raise_for_status(self):
        if not self.success:
            raise ResultException(self.notifications)
            
        
class ResultException(Exception):
    def __init__(self, notifications):
        msg = "API exception(s) occurred:\n" + "\n".join(notifications)
        super(ResultException, self).__init__(msg)
        
        
class Request:
    def __init__(self, command, **kwargs):
        self.request = etree.Element("request")
        etree.SubElement(self.request, "command").text = command
        
        for k, v in kwargs.items():
            if v is not None:
                etree.SubElement(self.request, k).text = v
            
    def get(self):
        return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' \
               + etree.tostring(etree.ElementTree(self.request)).decode()
               
                            
               
class AuthenticateRequest(Request):
    def __init__(self, key, passphrase):
        super(AuthenticateRequest, self).__init__("authenticate", apiIdentifierKey=key, passPhrase=passphrase)


class AuthenticateResult(Result):        
    @property
    def sessionId(self):
        return self.root.xpath("sessionId")[0].text
        
        
class TransactionRequest(Request):
    def __init__(self, limit=None, offset=None):
        super(TransactionRequest, self).__init__("listTransactions", limit=limit, offset=offset)
        self.filters = etree.SubElement(self.request, "filters")
        
    def filterDate(self, dateStart=None, dateEnd=None):
        f = etree.SubElement(self.filters, "filter")
        if dateStart is not None:
            etree.SubElement(f, "dateStart").text = dateStart.strftime("%Y-%m-%d")
        if dateEnd is not None:
            etree.SubElement(f, "dateEnd").text = dateEnd.strftime("%Y-%m-%d")
        
        
class TransactionResult(Result):
    @property
    def transactions(self):
        return [TransactionXML(transaction) for transaction in self.root.xpath("transactions/transaction") 
        if self.is_interesting_transaction(transaction)]
        
    @staticmethod
    def is_interesting_transaction(transaction):
        regexp = r"T\#\[\d*\]"
        return re.search(regexp, transaction.xpath("description")[0].text)
        
        
class TransactionXML:
    def __init__(self, node_or_id):
        if type(node_or_id) == int:
            self.identifier = node_or_id
            self.description = "T#[{}]".format(self.identifier)
            self.date = datetime.now().date()    
        else    
            self.node = node_or_id
            regexp = r"T\#\[(\d*)\]"
            self.identifier = int(re.search(regexp, self.description).group(1))
            self.description = self.node.xpath("description")[0].text
            self.date = datetime.strptime(self.node.xpath("date")[0].text, "%Y-%m-%d").date()
        
            
        
    @property
    def description(self):
        return self.description
             
    @property
    def date(self):
        return 
        
    @property
    def rows(self):
        return [TransactionRow(row) for row in self.node.xpath("transactionRows/transactionRow")]
        
class TransactionRow:
    def __init__(self, node):
        self.node = node
        
    @property
    def amount(self):
        return int(100 * float(self.node.xpath("amount")[0].text.replace(',', '.')))
        
    @property
    def credit(self):
        return self.node.xpath("side")[0].text == "credit"
        
    @property
    def account(self):
        return int(self.node.xpath("accountNr")[0].text)
        
    def __repr__(self):
        return "{} to {} {}".format(self.amount, self.account, "Credit" if self.credit else "Debit")
        
    def __str__(self):
        return self.__repr__()
        

