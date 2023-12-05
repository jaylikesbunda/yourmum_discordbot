import random

def generate_reel():
    # Slightly increased weights for lower value symbols
    symbols = ["🍒", "🍇", "🍋", "🃏", "🍀", "🍑", "🔔", "❤", "💎"]
    symbol_weights = [0.22, 0.22, 0.22, 0.03, 0.09, 0.006, 0.18, 0.06, 0.05]
    return random.choices(symbols, weights=symbol_weights, k=3)

def check_paylines(grid, bet_amount):
    paylines = [
        [grid[0], grid[1], grid[2]], [grid[3], grid[4], grid[5]], [grid[6], grid[7], grid[8]],
        [grid[0], grid[3], grid[6]], [grid[1], grid[4], grid[7]], [grid[2], grid[5], grid[8]],
        [grid[0], grid[4], grid[8]], [grid[2], grid[4], grid[6]]
    ]
    WILD_SYMBOL = "🃏"
    PEACH_JACKPOT_MULTIPLIER = 45  # Adjusted jackpot multiplier
    HIGH_VALUE_PARTIAL_MATCH_MULTIPLIER = 0.45  # Adjusted multiplier for partial matches
    WILD_MULTIPLIER = 1.15  # Adjusted wild multiplier
    HIGH_VALUE_SYMBOLS = ["🍑", "💎", "❤", "🍀"]
    BASE_PAYOUTS = {'🍒': 1.15, '🍇': 1.15, '🍋': 1.15, '🃏': 0, '🍀': 1.9, '🍑': 22, '🔔': 1.8, '❤': 3.2, '💎': 8.5}  # Adjusted payouts
    
    winnings = 0
    for payline in paylines:
        symbol_count = {symbol: payline.count(symbol) for symbol in set(payline)}
        if WILD_SYMBOL in symbol_count:
            for symbol, count in symbol_count.items():
                if symbol != WILD_SYMBOL and count + symbol_count[WILD_SYMBOL] == 3:
                    winnings += bet_amount * BASE_PAYOUTS[symbol] * WILD_MULTIPLIER
                    break
        else:
            if len(set(payline)) == 1:
                symbol = payline[0]
                if symbol == "🍑":
                    winnings += bet_amount * PEACH_JACKPOT_MULTIPLIER
                else:
                    winnings += bet_amount * BASE_PAYOUTS[symbol]
            elif len(set(payline)) == 2:
                most_common = max(set(payline), key=payline.count)
                if payline.count(most_common) == 2 and most_common in HIGH_VALUE_SYMBOLS:
                    winnings += bet_amount * HIGH_VALUE_PARTIAL_MATCH_MULTIPLIER * BASE_PAYOUTS[most_common]
    return winnings

def simulate_rtp(total_spins, bet_amount):
    total_bet = 0
    total_winnings = 0

    for _ in range(total_spins):
        reel1 = generate_reel()
        reel2 = generate_reel()
        reel3 = generate_reel()

        grid = [reel1[0], reel2[0], reel3[0], reel1[1], reel2[1], reel3[1], reel1[2], reel2[2], reel3[2]]
        winnings = check_paylines(grid, bet_amount)
        total_bet += bet_amount
        total_winnings += winnings

    return (total_winnings / total_bet) * 100

# Example usage
total_spins = 100000
bet_amount = 20
rtp = simulate_rtp(total_spins, bet_amount)
print(f"Simulated RTP: {rtp:.2f}%")
