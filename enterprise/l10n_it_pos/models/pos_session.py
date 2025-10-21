from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _update_session_info(self, session_info):
        super()._update_session_info(session_info)
        session_info['allow_l10n_it_pos'] = self.company_id.country_id.code == 'IT'
        return session_info
