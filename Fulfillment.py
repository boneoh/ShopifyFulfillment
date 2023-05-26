    # my function to fulfill a single line item in a Shopify order
  
    # need imports for ShopifyAPI and requests  
    
    # replace 'self.my_context.log_' with whatever you please e.g. print
    
    # your class should provide  self.shop_url, self.api_key, and self.api_version
    
    def fulfill_line_item(self, order, line_item):
        self.my_context.log_write("Fulfill line item was requested for " + str(line_item.id))

        try:
            fulfillment_orders = shopify.FulfillmentOrders.find(order_id=order.id)
            fulfillment_order = fulfillment_orders[0]

            fulfillment_order_id = fulfillment_order.id

            locations = shopify.Location.find()
            location = locations[0]
            location_id = location.id

            line_item_id = line_item.id         # from the order

            # find the matching fulfillment_order line_item

            fulfillment_line_item_id = 0

            for fulfillment_line_item in fulfillment_order.line_items:
                if fulfillment_line_item.line_item_id == line_item_id:

                    if fulfillment_line_item.fulfillable_quantity <= 0:

                        # we are fulfilling each line item after it has been successfully processed.
                        # it is benevolent, in that the fulfill_line_item will only give a warning
                        # and still return True if the line item was already fulfilled.

                        self.my_context.log_warning("This line item was already fulfilled")
                        return True

                    fulfillment_line_item_id = fulfillment_line_item.id
                    break

            if fulfillment_line_item_id <= 0:
                self.my_context.log_error("Could not find matching fulfillment order line item id ")

            fulfillment_order_line_items = []
            fulfillment_order_line_items.append(
                {
                    'id': fulfillment_line_item_id,
                    'quantity': line_item.quantity,
                }
            )

            payload = {
                "fulfillment":
                    {
                        "notify_customer": 'true',
                        "location_id": location_id,
                        "tracking_info":
                            {
                                "url": "www.lglsvcs.com",
                                "company": "lglsvcs.com",
                                "number": "0",
                            },
                        "line_items_by_fulfillment_order": [
                            {
                                "fulfillment_order_id": fulfillment_order_id,
                                "fulfillment_order_line_items": fulfillment_order_line_items
                            }
                        ]
                    }
            }

            # POST https://{shop}.myshopify.com/admin/api/{api_version}/fulfillments.json

            url = "https://" + self.shop_url + '/admin/api/' + self.api_version + '/fulfillments.json'
            headers = {"Accept": "application/json", "Content-Type": "application/json", "X-Shopify-Access-Token": self.api_key}

            response = requests.post(url, json=payload, headers=headers)

            if response is None:
                self.my_context.log_error("Response was None from POST request")
                return False
            elif response.status_code == 200 or response.status_code == 201:
                self.my_context.log_write("fulfill_line_item was successful")
                return True
            else:
                self.my_context.log_error(str(response.status_code) + ' ' + response.text)
                return False

        except Exception as e:
            self.my_context.log_error("fulfill_line_item failed " + str(e))
            return False

        return True
