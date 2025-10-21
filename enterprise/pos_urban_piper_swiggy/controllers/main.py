from odoo.addons.pos_urban_piper.controllers.main import PosUrbanPiperController
from odoo.http import request
from odoo.osv.expression import AND


class PosSwiggyController(PosUrbanPiperController):

    def _get_tax_value(self, taxes_data, pos_config):
        taxes = super()._get_tax_value(taxes_data, pos_config)
        if request.env.ref('pos_urban_piper_swiggy.pos_delivery_provider_swiggy', False) in pos_config.urbanpiper_delivery_provider_ids and taxes:
            parent_tax = request.env['account.tax'].sudo().search([('children_tax_ids', 'in', taxes.ids)])
            if parent_tax:
                taxes = parent_tax
        return taxes

    def _tax_amount_to_remove(self, lines, pos_config):
        five_percent_fiscal_line = (
            pos_config.urbanpiper_fiscal_position_id.tax_ids.filtered(
                lambda l: l.tax_src_id.amount == 5
                and l.tax_src_id.tax_group_id.name == 'GST'
                and l.tax_dest_id
                and l.tax_dest_id.amount != 0
            ) if pos_config.urbanpiper_fiscal_position_id.tax_ids else False
        )
        if pos_config.company_id.country_id.code != 'IN' or five_percent_fiscal_line:
            return super()._tax_amount_to_remove(lines, pos_config)
        return sum(
            float(line.get('total_with_tax', 0.0)) - float(line.get('price', 0.0))
            for line in lines
            if line.get('taxes', [{}])[0].get('rate') == 2.5
        )

    def _get_tax_domain(self, pos_config, tax_percentage):
        base_domain = super()._get_tax_domain(pos_config, tax_percentage)
        return (
            AND([
                [("tax_group_id.name", "=", "GST")],
                base_domain
            ])
            if pos_config.company_id.country_id.code == "IN"
            else base_domain
        )
