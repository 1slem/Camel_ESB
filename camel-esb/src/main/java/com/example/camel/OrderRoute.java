package com.example.camel;

import org.apache.camel.builder.RouteBuilder;
import org.springframework.stereotype.Component;

@Component
public class OrderRoute extends RouteBuilder {
    @Override
    public void configure() throws Exception {
        // Validate incoming XML against XSD
        from("cxf://http://0.0.0.0:8080/OrderService?serviceClass=com.example.camel.OrderService")
            .routeId("order-soap-route")
            .log("Received order message")
            .to("validator:schemas/order.xsd")
            .log("XML validated")
            // Transform XML to JSON via XSLT
            .to("xslt:xslt/order-to-json.xsl")
            .log("Transformed to JSON: ${body}")
            // Send to Supplier app
            .setHeader("Content-Type", constant("application/json"))
            .to("http://localhost:5000/ingest")
            .log("Forwarded to supplier: ${header.CamelHttpResponseCode}");
    }
}
