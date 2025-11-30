import requests, os, json

SOAP = '''<?xml version='1.0' encoding='UTF-8'?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Header/>
  <soapenv:Body>
    <order>
      <id>SMOKE-001</id>
      <customer>
        <name>Smoke Tester</name>
        <email>smoke@example.com</email>
      </customer>
      <items>
        <item>
          <sku>SMK-1</sku>
          <qty>5</qty>
        </item>
      </items>
    </order>
  </soapenv:Body>
</soapenv:Envelope>
'''

ESB_URL = 'http://127.0.0.1:8080/OrderService'
SUPPLIER_JSON = os.path.join('C:\\Users\\ASUS\\Documents\\augment-projects\\store\\supplier','orders.json')

try:
    r = requests.post(ESB_URL, data=SOAP.encode('utf-8'), headers={'Content-Type':'text/xml'}, timeout=10)
    print('ESB response:', r.status_code)
    print(r.text)
except Exception as e:
    print('Error posting to ESB:', e)

if os.path.exists(SUPPLIER_JSON):
    try:
        with open(SUPPLIER_JSON,'r',encoding='utf-8') as f:
            j=json.load(f)
        print('Supplier orders.json entries:', len(j))
        print('Last entry:', json.dumps(j[-1], indent=2))
    except Exception as e:
        print('Error reading supplier file:', e)
else:
    print('Supplier orders.json not found at', SUPPLIER_JSON)
