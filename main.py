import asyncio
import time

import octobot_commons.symbols as symbols
import octobot_commons.os_util as os_util

import triangular_arbitrage.detector as detector

# OctoBot partner exchanges exchange_ids from https://github.com/ccxt/ccxt/wiki/manual#exchanges
exchange_ids = {
    "Binance": "binanceus",
    "OKX": "okx",
    "Kucoin": "kucoin",
    "Bybit": "bybit",
    "Crypto.com": "cryptocom",
    "HTX": "huobi",
    "Bitget": "bitget",
    "BingX": "bingx",
    "MEXC": "mexc",
    "CoinEx": "coinex",
    "BitMart": "bitmart",
    "HollaEx": "hollaex",
    "Phemex": "phemex",
    "GateIO": "gate",
    "Ascendex": "ascendex",
    "Okcoin": "okcoin",
}

if __name__ == "__main__":
    if hasattr(asyncio, "WindowsSelectorEventLoopPolicy"):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())  # Windows handles asynchronous event loops

    benchmark = os_util.parse_boolean_environment_var("IS_BENCHMARKING", "True")  # default true
    exchange_timings = {}  # Store each exchange's execution time

    # Start scanning exchanges
    print("Scanning exchanges...")

    # Loop through each exchange in exchange_ids
    for exchange_name, exchange_id in exchange_ids.items():
        print(f"\nStarting detection for {exchange_name} ({exchange_id})...")
        start_time = time.perf_counter()  # Start time for current exchange

        try:
            # Run detection
            best_opportunities, best_profit = asyncio.run(detector.run_detection(exchange_id))

            def opportunity_symbol(opportunity):
                return symbols.parse_symbol(str(opportunity.symbol))

            def get_order_side(opportunity: detector.ShortTicker):
                return 'buy' if opportunity.reversed else 'sell'

            # Display arbitrage detection result
            if best_opportunities is not None:
                print("-------------------------------------------")
                total_profit_percentage = round((best_profit - 1) * 100, 5)
                print(f"New {total_profit_percentage}% {exchange_name} opportunity:")
                
                for i, opportunity in enumerate(best_opportunities):
                    # Get the base and quote currencies
                    base_currency = opportunity.symbol.base
                    quote_currency = opportunity.symbol.quote

                    # Format the output as below (real live example):
                    # -------------------------------------------
                    # New 2.33873% binanceus opportunity:
                    # 1. buy DOGE with BTC at 552486.18785
                    # 2. sell DOGE for USDT at 0.12232
                    # 3. buy ETH with USDT at 0.00038
                    # 4. buy ADA with ETH at 7570.02271
                    # 5. sell ADA for USDC at 0.35000
                    # 6. buy SOL with USDC at 0.00662
                    # 7. sell SOL for BTC at 0.00226
                    # -------------------------------------------
                    order_side = get_order_side(opportunity)
                    # print(
                    #     f"{i + 1}. {order_side} {base_currency} "
                    #     f"{'with' if order_side == 'buy' else 'for'} "
                    #     f"{quote_currency} at {opportunity.last_price:.5f}")
                print("-------------------------------------------")
            else:
                print(f"No opportunity detected for {exchange_name}")

        except AttributeError:
            print(f"Exchange ID '{exchange_id}' not found in ccxt.")
        except Exception as e:
            print(f"An error occurred with {exchange_name}: {e}")

        # Calculate and store elapsed time for this exchange
        elapsed_time = time.perf_counter() - start_time
        exchange_timings[exchange_name] = elapsed_time

    # Print timing results for each exchange
    print("\nBenchmark results (time taken per exchange):")
    for exchange, timing in exchange_timings.items():
        print(f"{exchange}: {timing:.2f} seconds")

    # Display total elapsed time if benchmarking is enabled
    if benchmark:
        total_elapsed = sum(exchange_timings.values())
        print(f"\nTotal execution time: {total_elapsed:.2f} seconds.")
