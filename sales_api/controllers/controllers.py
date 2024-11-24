# -*- coding: utf-8 -*-
from odoo import http
import functools
import logging
from odoo.http import request
import json
from odoo.addons.sales_api.models.common import invalid_response, valid_response



_logger = logging.getLogger(__name__)


class SalesApi(http.Controller):
    @http.route('/api/sales', methods=["POST"], type="http", auth="none", csrf=False)
    def create_sale_orders(self, **post):
        access_token = request.httprequest.headers.get("access_token")
        db = request.httprequest.headers.get("db")
        # print(access_token,db)
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)

        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=access_token)
        # print("user&&",user_id)

        request.session.update(http.get_default_session(), db=db)
        # print("session&&",request.session,db)

        if not user_id:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        user_obj = request.env['res.users'].browse(user_id)
        customer = request.httprequest.args.get("customer_id")
        customer_obj = request.env['res.partner'].sudo().search([('id','=',customer)],limit=1)
        discount = request.httprequest.args.get("discount")
        discount_product = request.env['product.product'].sudo().search([('default_code','=','DISC')],limit=1)

        lines = request.httprequest.get_data()
        lines= json.loads(lines)
        ordr_lines = lines.get("order_lines")
        #
        sale_obj = request.env['sale.order']
        sale_line_obj = request.env['sale.order.line']

        if not customer_obj:
            status = "404"
            type = "Customer"
            message = "Customer ID Cannot Be Found"
            id = str(customer)
            _logger.error(status)
            return invalid_response(type, message, id, status)

        else:

            new_order = sale_obj.with_user(user_obj).create({
            'partner_id':customer_obj.id,
            'partner_invoice_id':customer_obj.id,
            'partner_shipping_id': customer_obj.id,
            'user_id':user_id,
            'order_reference':request.httprequest.args.get("order_reference")
        })

        for line in ordr_lines:

            product_obj =line['product_id']

            product = request.env['product.product'].sudo().search([('product_tmpl_id','=',product_obj)],limit=1)

            if not product or not customer_obj:
                status = "404"
                type = "product"
                message ="Product ID Cannot Be Found"
                id = str(product_obj)
                _logger.error(status)
                return invalid_response(type,message, id, status)

            else:

                new_order_line = sale_line_obj.with_user(user_obj).create({
                'order_id':new_order.id,
                'product_id':product.id,
                'product_uom_qty': line['qty'],
                'application_price': line['application_price'],

            })
        if discount:
                new_order_line = sale_line_obj.with_user(user_obj).create({
                'order_id':new_order.id,
                'product_id':discount_product.id,
                'product_uom_qty': 1,
                'application_price': float(discount),
                'price_unit':- float(discount)

            })


        return valid_response([{"order": new_order.id, "message": "Order Created successfully"}], status=200)

    @http.route('/api/partner', methods=["POST"], type="http", auth="none", csrf=False)
    def create_new_customer(self, **post):
        access_token = request.httprequest.headers.get("access_token")
        db = request.httprequest.headers.get("db")
        # print(access_token,db)
        if not access_token:
            return invalid_response("access_token_not_found", "missing access token in request header", 401)

        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=access_token)
        # print("user&&",user_id)

        request.session.update(http.get_default_session(), db=db)
        # print("session&&",request.session,db)

        if not user_id:
            info = "authentication failed"
            error = "authentication failed"
            _logger.error(info)
            return invalid_response(401, error, info)

        user_obj = request.env['res.users'].browse(user_id)

        phone = request.httprequest.args.get("phone").replace(" ", "")
        print(phone)

        customer_obj = request.env['res.partner']
        customer = customer_obj.sudo().search([('phone','=',phone)],limit=1)
        if customer:
            status = "500"
            type = "Customer"
            message = "Customer Exists"+ " With Code: "+str(customer.ref)
            ref = str(customer.id)
            _logger.error(status)
            return invalid_response(type, message, ref, status)
        else:
            first_name = request.httprequest.args.get("first_name")
            last_name =request.httprequest.args.get("last_name")
            full_name = str(first_name)+" "+ str(last_name)


            new_customer = customer_obj.with_user(user_obj).create({
                'name':full_name,
                'business_name':request.httprequest.args.get("business_name"),
                'areas_id':request.httprequest.args.get("areas_id"),
                'street':request.httprequest.args.get("address"),
                'phone': phone,
                'email': request.httprequest.args.get("email"),
                'partner_longitude': request.httprequest.args.get("partner_longitude"),
                'partner_latitude': request.httprequest.args.get("partner_latitude"),
            })



            return valid_response([{"id": new_customer.id, "ref": new_customer.ref, "message": "Customer Created successfully"}], status=200)

