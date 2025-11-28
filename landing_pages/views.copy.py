# class CreateOrderView(View):
#     def parse_request_data(self, request):
#         if request.content_type == "application/json":
#             try:
#                 return json.loads(request.body.decode("utf-8"))
#             except Exception:
#                 raise ValidationError("Invalid JSON body")
#         return request.POST

#     def get_product(self, id):
#         if not id:
#             raise ValidationError("product_id is required")
#         product = get_object_or_404(Product, id=id)
#         # Optionally: product = Product.objects.select_related(...).get(id=id)
#         return product, float(product.discount_price or 0)

#     def get_product_variante(self, product, sku):
#         if not sku:
#             raise ValidationError("variante sku is required")
#         variante = get_object_or_404(ProductVariant, product=product, sku=sku)
#         return variante, float(variante.discount_price or 0)

#     def price_verify(self, input_price, actual_price):
#         try:
#             input_p = float(input_price)
#         except Exception:
#             raise ValidationError("Invalid product_price")
#         if round(input_p, 2) != round(float(actual_price), 2):
#             # rounding to avoid float tiny differences
#             raise ValidationError("Input price and product price do not match")
#         return True

#     def get_or_create_customer_by_email(self, name, phone, email):
#         """
#         If email provided: get_or_create CustomUser (assumes CustomerProfile auto-created)
#         If no email: get_or_create CustomerProfile by phone
#         Returns: customer_profile instance
#         """
#         if email:
#             user, created = CustomUser.objects.get_or_create(
#                 email=email,
#                 defaults={"full_name": name}
#             )
#             # ensure phone saved on profile
#             cust_profile = getattr(user, "customer_profile", None)
#             if not cust_profile:
#                 # fallback: create one if your project doesn't auto-create
#                 cust_profile = CustomerProfile.objects.get_or_create(
#                     user=user, defaults={"phone": phone, "full_name": name}
#                 )[0]
#             else:
#                 if phone and cust_profile.phone != phone:
#                     cust_profile.phone = phone
#                     cust_profile.save(update_fields=["phone"])
#             return cust_profile
#         else:
#             customer, _ = CustomerProfile.objects.get_or_create(
#                 phone=phone,
#                 defaults={"full_name": name}
#             )
#             return customer

#     def create_address(self, customer, address_text, district, upazila, area):
#         # minimal validation
#         if not address_text:
#             raise ValidationError("address is required")
#         addr = CustomerAddress.objects.create(
#             customer=customer,
#             address=address_text,
#             area=area or "",
#             upazila=upazila or "",
#             district=district or "",
#         )
#         return addr  # return model instance (not string)

#     def create_order_and_items(self, customer, address, product, variant, qty, unit_price, metadata):
#         # create order
#         order = Order.objects.create(
#             customer=customer,
#             items_total=int(qty),
#             billing_address=address,
#             shipping_address=address,
#             metadata=metadata or {}
#         )
#         # create order item(s) — here 1 item, if multiple items -> use bulk_create
#         OrderItem.objects.create(
#             order=order,
#             product=product,
#             variant=variant,
#             quantity=int(qty),
#             unit_price=float(unit_price),
#         )
#         return order

#     def post(self, request, *args, **kwargs):
#         try:
#             # parse incoming data (json or form)
#             data = self.parse_request_data(request)

#             # --- Basic validation BEFORE DB ---
#             product_id = data.get("product_id")
#             variant_sku = data.get("variante")  # user used 'variante' in original
#             input_price = data.get("product_price")
#             qty = data.get("qty")
#             name = data.get("name")
#             phone = data.get("phone")
#             email = data.get("email") or None
#             address_text = data.get("address")
#             district = data.get("district")
#             upazila = data.get("upazila")
#             area = data.get("area")
#             notes = data.get("notes")

#             if not product_id:
#                 return JsonResponse({"success": False, "message": "product_id is required"}, status=HTTPStatus.BAD_REQUEST)
#             if not qty:
#                 return JsonResponse({"success": False, "message": "qty is required"}, status=HTTPStatus.BAD_REQUEST)
#             try:
#                 qty_int = int(qty)
#                 if qty_int <= 0:
#                     raise ValueError()
#             except Exception:
#                 return JsonResponse({"success": False, "message": "qty must be a positive integer"}, status=HTTPStatus.BAD_REQUEST)
#             if not name or not phone:
#                 return JsonResponse({"success": False, "message": "name and phone are required"}, status=HTTPStatus.BAD_REQUEST)

#             # --- Fetch product/variant and verify price BEFORE creating any DB state ---
#             product, product_price = self.get_product(product_id)
#             variant = None
#             if variant_sku:
#                 variant, variant_price = self.get_product_variante(product, variant_sku)
#                 # override product_price with variant price
#                 product_price = variant_price

#             # price verify
#             self.price_verify(input_price, product_price)

#             # metadata
#             metadata = {"note": notes} if notes else {}

#             # --- All validations passed → enter atomic block to perform DB writes ---
#             with transaction.atomic():
#                 # customer (creates or gets) -> minimal queries due to get_or_create
#                 customer = self.get_or_create_customer_by_email(name, phone, email)

#                 # address create
#                 address = self.create_address(customer, address_text, district, upazila, area)

#                 # create order + items
#                 order = self.create_order_and_items(
#                     customer=customer,
#                     address=address,
#                     product=product,
#                     variant=variant,
#                     qty=qty_int,
#                     unit_price=product_price,
#                     metadata=metadata
#                 )

#                 # Send email AFTER commit so that rollback won't result in sent email
#                 if email:
#                     def _send_confirmation():
#                         try:
#                             send_mail = OrderConfirmatinoEmailSend(order, email)
#                             send_mail.order_confirmation_mail_send()
#                         except Exception as mail_exc:
#                             # log the mail exception instead of failing the transaction
#                             print("Order confirmation email failed:", str(mail_exc))
#                     transaction.on_commit(_send_confirmation)

#             # success response
#             return JsonResponse({"success": True, "message": "Order Successfully Created!", "order_id": getattr(order, "id", None)}, status=HTTPStatus.CREATED)

#         except ValidationError as ve:
#             return JsonResponse({"success": False, "message": str(ve)}, status=HTTPStatus.BAD_REQUEST)
#         except ObjectDoesNotExist as odne:
#             return JsonResponse({"success": False, "message": str(odne)}, status=HTTPStatus.NOT_FOUND)
#         except Exception as e:
#             # last resort: log exception server-side and return generic message
#             print("CreateOrderView Error:", repr(e))
#             return JsonResponse({"success": False, "message": "Something went wrong"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
















# from marketing.models import EmailConfig
# from marketing.utix import EmailConfigMailType, EmailConfigServerType
# from smtplib import SMTP
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.header import Header
# from email.utils import formataddr
# from accounts.models import CustomUser
# from accounts.utix import USER_TYPE
# from django.shortcuts import get_object_or_404


# class OrderConfirmatinoEmailSend:
#     def __init__(self, order, email) -> None:
#         self.order = order
#         self.email = email

#     def order_confirmation_mail_send(self):
#         email_server = EmailConfig.objects.filter(mail_type=EmailConfigMailType.NO_REPLY, is_active=True).first()
#         if email_server.server_type == EmailConfigServerType.SMTP:
#             subject = f"Successfully Confirm Your Order #{self.order.order_id}!"
#             html_body = self.get_dynamical_block_update(email_server)

#             mime_msg = MIMEMultipart('alternative')
#             mime_msg['Subject'] = str(Header(subject, 'utf-8'))
#             mime_msg['From'] = formataddr((email_server.name, email_server.email))
#             mime_msg['To'] = self.email
#             mime_msg["Reply-To"] = formataddr(("Samim Osman", email_server.reply_to))
#             mime_msg.attach(MIMEText(html_body, 'html', 'utf-8'))

#             server = SMTP(host=email_server.host, port=email_server.port)
#             server.starttls()
#             server.login(email_server.host_user, email_server.host_password)
#             server.sendmail(
#                 from_addr=email_server.email, to_addrs=self.email, msg=mime_msg.as_string()
#             )
#             return True
#         return True
    
#     def order_items_template(self):
#         order_items_html = ""
#         for item in self.order.items.all():
#             order_items_html += f"""
#                 <tr>
#                     <td style='padding:10px;'>{item.product.title}</td>
#                     <td style='padding:10px;'>{item.quantity}</td>
#                     <td style='padding:10px;'>৳{item.d_unit_price}</td>
#                 </tr>
#             """
#         return order_items_html
    
#     def get_dynamical_block_update(self, email_server):
#         user = get_object_or_404(CustomUser, email=self.email, user_type=USER_TYPE.CUSTOMER)
#         if user:
#             user = user.customer_profile
#         order = self.order
#         order_items = self.order_items_template()
#         msg_body = f"""<!DOCTYPE html>
#         <html>
#         <head>
#             <meta charset="UTF-8">
#             <title>Order Confirmation</title>
#         </head>
#         <body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif; background-color:#f4f4f4;">
#             <div style="max-width:600px; margin:20px auto; background:#ffffff; border-radius:8px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.1);">

#                 <!-- Header -->
#                 <div style="background:#177484; padding:20px; color:#ffffff; text-align:center;">
#                     <h2 style="margin:0; font-size:24px;">Order Confirmation</h2>
#                     <p style="margin:5px 0 0;">Thank you for shopping with us!</p>
#                 </div>

#                 <!-- Greeting -->
#                 <div style="padding:20px;">
#                     <p style="font-size:16px; margin:0 0 10px;">Dear {user.full_name},</p>
#                     <p style="font-size:15px; line-height:1.6; color:#333333;">
#                         We’re happy to let you know that your order has been successfully placed.  
#                         Below are the details of your order:
#                     </p>

#                     <!-- Order Info -->
#                     <div style="background:#f9f9f9; padding:15px; border-left:4px solid #177484; margin:20px 0; border-radius:5px;">
#                         <p style="margin:5px 0; font-size:15px;"><strong>Order ID:</strong> #{order.order_id}</p>
#                         <p style="margin:5px 0; font-size:15px;"><strong>Order Date:</strong> {order.placed_at.strftime("%d %B %Y")}</p>
#                         <p style="margin:5px 0; font-size:15px;"><strong>Total Amount:</strong> ৳{order.get_discount_total}</p>
#                         <p style="margin:5px 0; font-size:15px;"><strong>Payment Method:</strong> {order.payment_status}</p>
#                     </div>

#                     <!-- Items Table (Optional)
#                     Add if you have order items -->
                    
#                     <h3 style="font-size:18px; margin-bottom:10px;">Order Items</h3>
#                     <table width="100%" style="border-collapse:collapse;">
#                         <tr style="background:#f1f1f1;">
#                             <th style="padding:10px; text-align:left;">Product</th>
#                             <th style="padding:10px; text-align:left;">Qty</th>
#                             <th style="padding:10px; text-align:left;">Price</th>
#                         </tr>
#                         {order_items}
#                     </table>
                    

#                     <p style="font-size:15px; margin-top:20px; color:#333;">
#                         You will receive another email when your order is shipped.
#                     </p>

#                     <p style="font-size:15px; margin-top:25px;">
#                         If you have any questions, feel free to reply to this email.
#                     </p>

#                     <p style="font-size:16px; margin-top:20px;"><strong>Best regards,</strong><br>Your Company Team</p>
#                 </div>

#                 <!-- Footer -->
#                 <div style="background:#eeeeee; padding:15px; text-align:center; font-size:12px; color:#555;">
#                     &copy; {order.placed_at.year} Your Company. All rights reserved.
#                 </div>

#             </div>
#         </body>
#         </html>"""

#         return msg_body
    


