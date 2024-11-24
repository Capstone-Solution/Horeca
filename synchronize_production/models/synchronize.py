from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import re
import datetime
import time
import requests

class Synchronize(models.Model):
    _name = 'synchronize'
    _rec_name = 'api_url'

    api_url = fields.Char(string='API Url')
    token = fields.Char(string='Token')
    
    def category_sync(self):
        categories = self.env['product.category'].search([])

        sync_data = self.env['synchronize'].search([])
        for rec in sync_data:
        # raise ValidationError(sync_data[0].token)
            category_names = [ {'id': category.id, 'name': category.name}  for category in categories]
            return self.send_post_Data(rec.api_url ,rec.token , category_names , "category" , "الاصناف")
    

    def unites_sync(self):
        unities = self.env['uom.category'].search([])

        sync_data = self.env['synchronize'].search([])
        for rec in sync_data:
        # raise ValidationError(sync_data[0].token)
            unities_names = [ {'id': unit.id, 'name': unit.name}  for unit in unities]
            return self.send_post_Data(rec.api_url ,rec.token , unities_names , "unites" , "الوحدات")
 

    def product_sync(self):
        products = self.env['product.template'].search([])
        sync_data = self.env['synchronize'].search([])
        for rec in sync_data:
        # raise ValidationError(products[0] )
            products_array = [ {'id': product.id , 'code':   product.default_code ,  'unite_id': product.uom_id.id ,  'name': product.name , 'price': product.list_price , 'categ_id': product.categ_id.id ,'qty_available':product.qty_available}  for product in products]
        # raise ValidationError(products_array )
            return self.send_post_Data(rec.api_url ,  rec.token , products_array , "products" , "المنتجات")



    # uom.category
    def contacts_sync(self):
        contacts = self.env['res.partner'].search([] )
        sync_data = self.env['synchronize'].search([])
        for rec in sync_data:

            contact_array = [ {
                            'id': contact.id,
                            'ar_name': contact.ar_client_name_ar ,
                            'phone': contact.phone , 
                            'email':  contact.email ,
                            'street': contact.street,
                             'name': contact.name,
                            'en_name':  contact.en_client_name_en ,
                            'partner_latitude':  contact.partner_latitude ,
                            'partner_longitude':  contact.partner_longitude ,
                             } for contact in contacts]
        
            return self.send_post_Data( rec.api_url ,rec.token , contact_array , "customers" , "العملاء")

    def send_post_Data(self , url , token , data , type , name):
        endpoint_url = url
        jwt_token = token
        headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
       }
        payload = {
        'type': type,
        'data': data,
  
         }
        
        try:
        # Send the POST request
            response = requests.post(endpoint_url, headers=headers, json=payload)
        
        # Check if the request was successful (status code 200)
            if response.status_code == 200:
            #    print('Categories sent successfully.')
               view = self.env.ref('sh_message.sh_message_wizard')
               context = dict(self._context or {})
               dic_msg =   f'تم تحديث {name} بنجاح'
               context['message'] = dic_msg

               return {
                  'name': 'success' ,
                   'type': 'ir.actions.act_window',
                   'view_type': 'form',
                   'view_mode': 'form',
                   'res_model': 'sh.message.wizard',
                   'views':[(view.id , 'form')   ],
                   'view_id': view.id,
                  'target': 'new',
                  'context': context
               }
            #    raise ValidationError( f'تم تحديث {name} بنجاح')
            else:
               view = self.env.ref('sh_message.sh_message_wizard')
               context = dict(self._context or {})
               dic_msg =  response.content
               
            #    f'في مشكلة في تحديث {name}'
               context['message'] = dic_msg

               return {
                   'name': 'error' ,
                   'type': 'ir.actions.act_window',
                   'view_type': 'form',
                   'view_mode': 'form',
                   'res_model': 'sh.message.wizard',
                   'views':[(view.id , 'form')   ],
                   'view_id': view.id,
                  'target': 'new',
                  'context': context
               }
            #    raise ValidationError( f'في مشكلة في تحديث {name}')
    
        except requests.exceptions.RequestException as e:
               raise ValidationError( f'An error occurred: {e}')
               print(f'An error occurred: {e}')
       
# class SyncAction(models.Model):
#     _name = 'sync.action'

#     @api.model
#     def run_sync_action(self):
#         # Your sync logic here
#         # This function will be executed when the action is triggered
#         # Replace this with your actual synchronization logic
#         print("Sync action executed successfully!")

# class SyncView(models.Model):
#     _name = 'sync.view'

#     @api.model
#     def create_sync_view(self):
#         # Your view creation logic here
#         # This function will be executed when the view is opened
#         # Replace this with your actual view creation logic
#         view_arch = """
#             <div>
#                 <button name="run_sync_action" string="Sync" type="object"/>
#             </div>
#         """
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Sync Page',
#             'res_model': 'sync.action',
#             'view_mode': 'form',
#             'target': 'new',
#             'views': [(False, 'form')],
#             'context': {},
#             'view_id': False,
#             'view_type': 'form',
#             'limit': 1,
#             'res_id': False,
#             'arch': view_arch,
#         }
