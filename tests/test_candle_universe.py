import pytest

from capitalgram.candle import CandleBucket, GroupedCandleUniverse
from capitalgram.client import Capitalgram
from capitalgram.chain import ChainId
from capitalgram.pair import PairUniverse, PandasPairUniverse


@pytest.fixture(scope="module")
def client():
    """Create a client that uses test API key from OS environment against the production server."""
    c = Capitalgram.create_test_client()
    return c


@pytest.fixture(scope="module")
def cache_path(client: Capitalgram):
    cache_path = client.transport.cache_path
    return cache_path


def test_grouped_candles(client: Capitalgram, cache_path: str):
    """Group downloaded candles by a trading pair."""

    exchange_universe = client.fetch_exchange_universe()
    raw_pairs = client.fetch_pair_universe().to_pandas()
    raw_candles = client.fetch_all_candles(CandleBucket.d7).to_pandas()

    pair_universe = PandasPairUniverse(raw_pairs)
    candle_universe = GroupedCandleUniverse(raw_candles)

    # Do some test calculations for a single pair
    sushi_swap = exchange_universe.get_by_name_and_chain(ChainId.ethereum, "sushiswap")
    sushi_usdt = pair_universe.get_one_pair_from_pandas_universe(sushi_swap.exchange_id, "SUSHI", "USDT")

    sushi_usdt_candles = candle_universe.get_candles_by_pair(sushi_usdt.pair_id)

    # Get max and min weekly candle of SUSHI-USDT on SushiSwap
    high_price = sushi_usdt_candles["high"]
    max_price = high_price.max()

    low_price = sushi_usdt_candles["low"]
    min_price = low_price.min()
    
    # Min and max prices of SUSHI-USDT ever
    assert max_price == pytest.approx(22.4612)
    assert min_price == pytest.approx(0.49680945)