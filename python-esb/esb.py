from flask import Flask, request, Response
from flask_cors import CORS
from lxml import etree
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# load XSD and XSLT
BASE = os.path.join(os.path.dirname(__file__), '..', 'camel-esb', 'src', 'main', 'resources')
XSD_PATH = os.path.join(BASE, 'schemas', 'order.xsd')
XSLT_PATH = os.path.join(BASE, 'xslt', 'order-to-json.xsl')

with open(XSD_PATH, 'rb') as f:
    xmlschema_doc = etree.parse(f)
    xmlschema = etree.XMLSchema(xmlschema_doc)

xslt_doc = etree.parse(XSLT_PATH)
transform = etree.XSLT(xslt_doc)

SUPPLIER_URL = 'http://localhost:5000/ingest'

@app.route('/')
def home():
    return '''
    ESB is running. Send SOAP POST to /OrderService
    Example:
    curl -X POST http://localhost:8080/OrderService 
         -H "Content-Type: text/xml" 
         -d @order.xml
    '''

@app.route('/OrderService', methods=['GET', 'POST'])
def handle_order():
    app.logger.info('Request to /OrderService: method=%s content-type=%s', 
                    request.method, request.headers.get('Content-Type'))
    
    if request.method == 'GET':
        return '''
        ESB OrderService endpoint. Send SOAP POST requests here.
        Example:
        curl -X POST http://localhost:8080/OrderService 
             -H "Content-Type: text/xml" 
             -d @order.xml
        '''
    
    # Log the received SOAP request
    app.logger.info('Received SOAP request body: %s', request.get_data(as_text=True))
    
    # Handle SOAP POST request
    try:
        data = request.get_data()
        app.logger.info('Received data: %s', data)
        doc = etree.fromstring(data)
        
        # Find order element anywhere in the envelope
        order_elem = doc.find('.//{*}order')
        if order_elem is None:
            return 'No <order> element found in SOAP body', 400
            
        # Validate and transform
        order_doc = etree.ElementTree(order_elem)
        try:
            xmlschema.assertValid(order_doc)
        except Exception as e:
            return f'XML validation failed: {e}', 400
            
        # Transform to JSON and forward
        json_text = str(transform(order_elem))
        app.logger.info('Transformed to JSON: %s', json_text)
        
        headers = {'Content-Type': 'application/json'}
        r = requests.post(SUPPLIER_URL, 
                        data=json_text.encode('utf-8'),
                        headers=headers)
        
        app.logger.info('Supplier response: %s', r.text)
        return f'Order processed. Supplier status: {r.status_code}', 200
        
    except Exception as e:
        app.logger.error('Error processing request: %s', e)
        return f'Error processing request: {e}', 500
def order_service():
    app.logger.info('Received ESB request to path: %s', request.path)
    app.logger.info('Request data: %s', request.get_data(as_text=True))
    # parse incoming SOAP envelope
    data = request.get_data()
    try:
        doc = etree.fromstring(data)
    except Exception as e:
        return Response(f'Invalid XML: {e}', status=400)

    # Extract the <order> element (namespace-agnostic)
    order_elem = doc.find('.//order')
    if order_elem is None:
        return Response('No <order> element found', status=400)

    # validate
    order_doc = etree.ElementTree(order_elem)
    try:
        xmlschema.assertValid(order_doc)
    except Exception as e:
        return Response(f'Validation failed: {e}', status=400)

    # transform to JSON text
    json_text = str(transform(order_elem))

    # forward to supplier
    headers = {'Content-Type': 'application/json'}
    r = requests.post(SUPPLIER_URL, data=json_text.encode('utf-8'), headers=headers)

    return Response(f'Forwarded, supplier status: {r.status_code}', status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
