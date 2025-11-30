Camel ESB (Spring Boot + Camel) Demo

Build and run:

- Requires JDK 11+, Maven installed.
- From this folder run: mvn spring-boot:run

What it does:
- Exposes a CXF SOAP endpoint at http://localhost:8080/OrderService
- Validates incoming XML against `src/main/resources/schemas/order.xsd`
- Transforms XML to JSON with `src/main/resources/xslt/order-to-json.xsl`
- Forwards JSON to http://localhost:5000/ingest

Notes:
- This is a minimal demo. In production you'd configure CXF properly with WSDL and wsdlLocation and message handling.
