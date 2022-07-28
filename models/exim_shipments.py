from odoo import models, fields , api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class EximShipment(models.Model):
    _name = 'exim.shipments'
    _rec_name = 'shipment_no' 
    pi_no_id = fields.Many2one('exim.pi',string='Proforma Invoice', required=True)
    shipment_no = fields.Char('Shipment')
    lot_no = fields.Char('Lot No.')
    state = fields.Selection([('draft', 'Draft'),('transit', 'in-Transit'),('igm', 'IGM Received'),('released', 'Released')],default="draft", string='State') 


class EximShipmentCommercialInvoice(models.Model):
    _name = 'exim.shipments.ci'
    _rec_name = 'invoice_no'
    _inherit = ['mail.thread']
    shipment_id = fields.Many2one("exim.shipments" , string="Shipment")
    invoice_no = fields.Char("Invoice No." , required=True)
    port_of_embarkation = fields.Many2one('configuration.port.child',string="Port of Embarkation",required=True,domain="[('parent_field_id', '=', country_of_origin)]")
    country_of_origin = fields.Many2one('configuration.port.parent',string="Country of Origin",required=True)
    port_of_discharge = fields.Many2one('configuration.port.child',string="Port of Discharge",required=True,domain="[('parent_field_id', '=', country_of_destination)]")
    country_of_destination = fields.Many2one('configuration.port.parent',string="Country of Destination",required=True)
    product_detail = fields.One2many('exim.shipment.ci.product','ci_id',string="Product Detail",required=True)
    no_of_packages = fields.Integer("Number of Packages",required=True)
    gross_weight = fields.Integer("Gross Weight",required=True)
    net_weight = fields.Integer("Net Weight",required=True)
    no_of_pallets = fields.Integer("Number of Pallets",required=True)
    lot_no = fields.Integer("Lot No",required=True)
    payment_terms = fields.Text("Payment Terms",required=True)
    beneficiary_name = fields.Text("Beneficiary Name",required=True)
    bank_name = fields.Text("Bank Name",required=True)
    bank_address = fields.Text("Bank Address",required=True)
    branch = fields.Char("Branch",required=True)
    swift_code = fields.Char("Swift Code",required=True)
    iban = fields.Char("IBAN",required=True)
    currency_id = fields.Many2one('res.currency',compute='_compute_currency', inverse='_set_uom',string='Currency' ,required=True)




    @api.model
    def create(self, values):
        CommercialInvoice = self.env['exim.shipments.ci']
        # _logger.info("Working" + str(values))
        limit = CommercialInvoice.search_count([('shipment_id','=', values["shipment_id"])])
        # _logger.info("Working" + str(limit))
        if(limit >= 1):
            raise ValidationError("Only One Commercial Invoice Allowed Per Shipment")
        else:
            return super(EximShipmentCommercialInvoice, self).create(values)
    
    def _set_uom(self):
        pass

    @api.depends('shipment_id')
    def _compute_currency(self):
        for ci in self:
            if ci.shipment_id:
                ci.currency_id = ci.shipment_id.pi_no_id.currency_id
            else:
                ci.currency_id = None

    

class ProductCommercialInvoice(models.Model):
    _name = 'exim.shipment.ci.product'
    ci_id = fields.Many2one('exim.shipments.ci',string="CI ID")
    packing_type = fields.Char("Packing Type",required=True)
    description = fields.Char("Description",required=True)
    unit_price = fields.Monetary("Unit Price",currency_field='currency_id',required=True)
    quantity_box = fields.Integer("Qty(Box)",required=True)
    line_total = fields.Monetary("Line Total",currency_field='currency_id',compute='_calculate_line_total',required=True)
    currency_id = fields.Many2one('res.currency',compute='_compute_currency', inverse='_set_uom',string='Currency' ,required=True)
    final_amount = fields.Monetary("Final Amount",compute='_compute_final_amount', currency_field='currency_id')


    @api.depends('ci_id')
    def _compute_currency(self):
        for product_detail in self:
            if product_detail.ci_id:
                product_detail.currency_id = product_detail.ci_id.currency_id
            else:
                product_detail.currency_id = None

    def _set_uom(self):
        pass
        
    @api.depends('unit_price','quantity_box')
    def _calculate_line_total(self):
        for x in self:
                x.line_total = x.unit_price * x.quantity_box
        

    
    @api.depends('line_total')
    def _compute_final_amount(self):
        for pi in self:
            sum = 0
            for product_detail in pi.line_total:
                sum = sum + product_detail.line_total
            pi.final_amount = sum