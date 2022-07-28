from odoo import models, fields ,api

class EximProformaInvoice(models.Model):
    _name = 'exim.pi'
    _inherit = ['mail.thread']
    _description = "Proforma Invoice"
    _rec_name = 'pi_no'
    pi_no = fields.Char(string="PI No.", required = True)
    shipper_name = fields.Many2one('res.partner',string="Shipper", required=True)
    product_details = fields.One2many('exim.pi.product','pi_id',string="Product Detail",required=True)
    payment_terms = fields.Text("Payment Terms")
    incoterms = fields.Text("Incoterms")
    shipment_count = fields.Integer(compute="_compute_shipment_count")
    currency_id = fields.Many2one('res.currency',compute='_compute_currency',string='Currency' ,required=True)
    state = fields.Selection([('draft', 'Draft'),('inprogress', 'In-Progress'),('partially-complete', 'Partially Complete'),('complete', 'Complete')],default="draft", string='State')
    amount_total = fields.Monetary('Total',compute='_compute_total_amount', currency_field='currency_id', required=True) 
    discount = fields.Monetary('Discount', currency_field='currency_id', required=True)
    final_amount = fields.Monetary("Final Amount",compute='_compute_final_amount', currency_field='currency_id')
    
    
    @api.depends('shipper_name')
    def _compute_currency(self):
        for pi in self:
            if pi.shipper_name:
                pi.currency_id = pi.shipper_name.country_id.currency_id
            else:
                pi.currency_id = None
    
    @api.depends('discount')
    def _compute_final_amount(self):
        for pi in self:
            pi.final_amount = pi.amount_total - pi.discount
    
    @api.depends('product_details')
    def _compute_total_amount(self):
        for pi in self:
            sum = 0
            for product_detail in pi.product_details:
                sum = sum + product_detail.total

            pi.amount_total = sum

        



    def _compute_shipment_count(self):
        Shipment = self.env['exim.shipments']
        for pi in self:
            pi.shipment_count = Shipment.search_count([('pi_no_id','=',pi.id)])
    
    def button_confirm(self):
        self.write({'state': 'inprogress' })
    

class EximProformaInvoiceProduct(models.Model):
    _name = 'exim.pi.product'
    product_id = fields.Many2one('product.template',string="Product", required=True)
    uom_id = fields.Many2one('uom.uom',string="UoM", required=True)
    qty = fields.Float('Quantity', required=True)
    net_wt = fields.Float('Net wt', required=True)

    price = fields.Monetary( 'Price', currency_field='currency_id', required=True)
    total = fields.Monetary(string='Total', currency_field='currency_id',compute='_compute_total',required=True) 
    currency_id = fields.Many2one('res.currency',compute='_compute_currency', inverse='_set_uom',string='Currency' ,required=True)
    pi_id = fields.Many2one('exim.pi', string="Parent ID")
    


    def _set_uom(self):
        pass

    @api.depends('qty','price')
    def _compute_total(self):
        for product in self:
            if product.price:
                total_price = product.price * product.qty
                product.total = total_price
            else:
                product.total = 0
    
    @api.depends('pi_id')
    def _compute_currency(self):
        for product in self:
            if product.pi_id.shipper_name:
                product.currency_id = product.pi_id.shipper_name.country_id.currency_id
            else:
                product.currency_id = None
    





