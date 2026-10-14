from odoo.tests import TransactionCase, tagged
from odoo.addons.ai_mcp.core import rate_limit


@tagged('post_install', '-at_install', 'ai_mcp')
class TestRateLimit(TransactionCase):

    def setUp(self):
        super().setUp()
        rate_limit.reset()

    def test_allows_within_limit(self):
        for _ in range(60):
            self.assertTrue(rate_limit.check(1, 'aaaa', limit=60))

    def test_blocks_over_limit(self):
        for _ in range(60):
            rate_limit.check(1, 'aaaa', limit=60)
        self.assertFalse(rate_limit.check(1, 'aaaa', limit=60))

    def test_buckets_isolated_per_key(self):
        for _ in range(60):
            rate_limit.check(1, 'aaaa', limit=60)
        self.assertTrue(rate_limit.check(1, 'bbbb', limit=60))   # key khác — bucket khác
        self.assertTrue(rate_limit.check(2, 'aaaa', limit=60))   # uid khác — bucket khác

    def test_refills_over_time(self):
        for _ in range(60):
            rate_limit.check(1, 'cccc', limit=60)
        rate_limit._BUCKETS[(1, 'cccc')]['ts'] -= 61   # giả lập 61s trôi qua
        self.assertTrue(rate_limit.check(1, 'cccc', limit=60))
