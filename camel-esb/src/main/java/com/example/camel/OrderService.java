package com.example.camel;

import javax.jws.WebMethod;
import javax.jws.WebService;

@WebService
public interface OrderService {
    @WebMethod
    String submitOrder(String orderXml);
}
