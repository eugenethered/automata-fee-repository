import unittest

from cache.holder.RedisCacheHolder import RedisCacheHolder
from core.number.BigFloat import BigFloat

from feerepo.repository.FeeRepository import FeeRepository
from feerepo.repository.account.AccountFeeRepository import AccountFeeRepository
from feerepo.repository.exception.NoTradeFeeError import NoTradeFeeError
from feerepo.repository.instrument.InstrumentFeeRepository import InstrumentFeeRepository


class FeeRepositoryTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.options = {
            'REDIS_SERVER_ADDRESS': '192.168.1.90',
            'REDIS_SERVER_PORT': 6379,
            'ACCOUNT_TRADE_FEE_KEY': 'test:fee:trade:account',
            'INSTRUMENT_TRADE_FEE_KEY': 'test:fee:trade:{instrument}'
        }
        self.cache = RedisCacheHolder(self.options)
        self.account_fee_repository = AccountFeeRepository(self.options)
        self.instrument_fee_repository = InstrumentFeeRepository(self.options)
        self.repository = FeeRepository(self.options)

    def tearDown(self):
        self.cache.delete('test:fee:trade:account')
        self.cache.delete('test:fee:trade:OTC')

    def test_should_retrieve_fee_at_instrument_level(self):
        self.instrument_fee_repository.store_instrument_trade_fee(BigFloat('0.25'), 'OTC')
        trade_fee = self.repository.get_trade_fee('OTC')
        self.assertEqual(trade_fee, BigFloat('0.25'))

    def test_should_retrieve_fee_at_account_level(self):
        self.account_fee_repository.store_account_trade_fee(BigFloat('0.11'))
        trade_fee = self.repository.get_trade_fee('OTC')
        self.assertEqual(trade_fee, BigFloat('0.11'))

    def test_should_raise_exception_when_trade_fee_cannot_be_obtained(self):
        with self.assertRaises(NoTradeFeeError) as ntf:
            self.repository.get_trade_fee('B@D')
        self.assertEqual(str(ntf.exception), 'Trade Fee cannot be found at instrument or account level for [B@D]')


if __name__ == '__main__':
    unittest.main()
