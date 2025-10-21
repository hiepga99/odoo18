import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { roundPrecision } from "@web/core/utils/numbers";
import { accountTaxHelpers } from "@account/helpers/account_tax";

// -------------------------------------------------------------------------
// HELPERS IN BOTH PYTHON/JAVASCRIPT (account_tax.js / account_tax.py)
// -------------------------------------------------------------------------
if (session["allow_l10n_it_pos"]) {
    patch(accountTaxHelpers, {
        get_total_price(price_unit, quantity, tax_amount, precision_rounding) {
            function round(value) {
                return roundPrecision(value, precision_rounding);
            }

            const tax_value = tax_amount / 100;
            const unit_price_tax_excluded = round(price_unit);
            const unit_price_tax_included = round(unit_price_tax_excluded * (1 + tax_value));
            const total_price_tax_included = round(unit_price_tax_included * quantity);
            const total_price_tax_excluded = round(total_price_tax_included / (1 + tax_value));
            const total_tax_amount = round(total_price_tax_excluded * (tax_amount / 100));

            return {
                tax_included: total_price_tax_included,
                tax_excluded: total_price_tax_excluded,
                tax_amount: total_tax_amount,
            };
        },

        eval_raw_base(quantity, price_unit, evaluation_context) {
            const tax_amount = evaluation_context.taxes[0]?.amount;
            const precision_rounding = evaluation_context.precision_rounding;
            const total_price = this.get_total_price(
                price_unit,
                quantity,
                tax_amount,
                precision_rounding
            );
            return total_price.tax_excluded;
        },

        /** override **/
        /**
         * [!] Mirror of the same method in l10n_it_pos/account_tax.py.
         * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
         */
        eval_tax_amount_price_excluded(tax, batch, raw_base, evaluation_context) {
            const price_unit = evaluation_context.price_unit;
            const quantity = evaluation_context.quantity;
            const precision_rounding = evaluation_context.precision_rounding;
            const total_price = this.get_total_price(
                price_unit,
                quantity,
                tax.amount,
                precision_rounding
            );

            return total_price.tax_amount;
        },

        // /** override **/
        /**
         * [!] Mirror of the same method in l10n_it_pos/account_tax.py.
         * PLZ KEEP BOTH METHODS CONSISTENT WITH EACH OTHERS.
         */
        get_tax_details(
            taxes,
            price_unit,
            quantity,
            {
                precision_rounding = null,
                rounding_method = "round_per_line",
                // When product is null, we need the product default values to make the "formula" taxes
                // working. In that case, we need to deal with the product default values before calling this
                // method because we have no way to deal with it automatically in this method since it depends of
                // the type of involved fields and we don't have access to this information js-side.
                product = null,
                special_mode = false,
            } = {}
        ) {
            const tax_details = super.get_tax_details(taxes, price_unit, quantity, {
                precision_rounding,
                rounding_method,
                product,
                special_mode,
            });

            const batching_results = this.batch_for_taxes_computation(taxes, {
                special_mode: special_mode,
            });
            const sorted_taxes = batching_results.sorted_taxes;

            let total_excluded = 0;
            let total_included = 0;
            for (const tax of sorted_taxes) {
                const total_price = this.get_total_price(
                    price_unit,
                    quantity,
                    tax.amount,
                    precision_rounding
                );
                total_included += total_price.tax_included;
                total_excluded += total_price.tax_excluded;
            }

            tax_details.total_excluded = total_excluded;
            tax_details.total_included = total_included;
            return tax_details;
        },
    });
}
