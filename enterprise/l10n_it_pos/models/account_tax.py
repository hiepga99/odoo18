from odoo import models
from odoo.tools.float_utils import float_round


class AccountTax(models.Model):
    _inherit = "account.tax"

    def _is_it_pos(self):
        return self.env.company.country_id.code == 'IT' and self.env.context.get('linked_to_pos')

    def _get_total_price(self, price_unit, quantity, tax_amount, precision_rounding):
        def _round(value):
            return float_round(value, precision_rounding=precision_rounding)

        tax_value = tax_amount / 100
        unit_price_tax_excluded = _round(price_unit)
        unit_price_tax_included = _round(unit_price_tax_excluded * (1 + tax_value))
        total_price_tax_included = _round(unit_price_tax_included * quantity)
        total_price_tax_excluded = _round(total_price_tax_included / (1 + tax_value))
        total_tax_amount = _round(total_price_tax_excluded * (tax_amount / 100))

        return {
            'tax_included': total_price_tax_included,
            'tax_excluded': total_price_tax_excluded,
            'tax_amount': total_tax_amount
        }

    def _eval_raw_base(self, quantity, price_unit, evaluation_context):
        if not self._is_it_pos():
            return super()._eval_raw_base(quantity, price_unit, evaluation_context)

        tax_amount = evaluation_context['taxes'].amount
        precision_rounding = evaluation_context['precision_rounding']
        total_price = self._get_total_price(price_unit, quantity, tax_amount, precision_rounding)
        return total_price['tax_excluded']

    def _eval_tax_amount_price_excluded(self, batch, raw_base, evaluation_context):
        if not self._is_it_pos():
            return super()._eval_tax_amount_price_excluded(batch, raw_base, evaluation_context)

        price_unit = evaluation_context['price_unit']
        quantity = evaluation_context['quantity']
        tax_amount = batch['amount']
        precision_rounding = evaluation_context['precision_rounding']
        total_price = self._get_total_price(price_unit, quantity, tax_amount, precision_rounding)

        return total_price['tax_amount']

    def _get_tax_details(
        self,
        price_unit,
        quantity,
        precision_rounding=0.01,
        rounding_method='round_per_line',
        product=None,
        special_mode=False,
    ):
        tax_details = super()._get_tax_details(price_unit, quantity, precision_rounding, rounding_method, product, special_mode)

        if not self._is_it_pos():
            return tax_details

        batching_results = self._batch_for_taxes_computation(special_mode=special_mode)
        sorted_taxes = batching_results['sorted_taxes']

        total_excluded = total_included = 0
        for tax in sorted_taxes:
            total_price = self._get_total_price(price_unit, quantity, tax['amount'], precision_rounding)
            total_included += total_price['tax_included']
            total_excluded += total_price['tax_excluded']

        tax_details.update({
            'total_excluded': total_excluded,
            'total_included': total_included
        })

        return tax_details
