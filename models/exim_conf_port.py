from odoo import models, fields 


class CountryPorts(models.Model):
    _name = 'configuration.port.parent'
    _rec_name = 'country' 
    country = fields.Many2one('res.country', string="Country", required=True)
    ports = fields.One2many('configuration.port.child', 'parent_field_id', string="Ports")


class Ports(models.Model):
    _name = 'configuration.port.child'
    _rec_name = 'port'
    port = fields.Char('Port', required=True)
    parent_field_id = fields.Many2one('configuration.port.parent', string="Parent ID")





