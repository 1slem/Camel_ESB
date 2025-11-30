import requests

SOAP_TEMPLATE = """<?xml version='1.0' encoding='UTF-8'?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body>
    <order>
      <id>ORD-1001</id>
      <customer>
        <name>John Doe</name>
        <email>john@example.com</email>
      </customer>
      <items>
        <item>
          <sku>SKU-1</sku>
          <qty>2</qty>
        </item>
        <item>
          <sku>SKU-2</sku>
          <qty>1</qty>
        </item>
      </items>
    </order>
  </soapenv:Body>
</soapenv:Envelope>
"""

if __name__ == '__main__':
    url = 'http://localhost:8080/OrderService'
    headers = {'Content-Type': 'text/xml'}
    r = requests.post(url, data=SOAP_TEMPLATE.encode('utf-8'), headers=headers)
    print('Status:', r.status_code)
    print('Body:', r.text)
