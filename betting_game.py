import random
import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# ---- Helper Functions ----
def get_outcome_coin_flip():
    return [random.choice(["H", "T"]) for _ in range(3)]

def get_outcome_dice_sum():
    return random.randint(1, 6) + random.randint(1, 6)

def get_outcome_card_draw():
    card1 = random.randint(1, 13)
    card2 = random.randint(1, 13)
    card3 = random.randint(1, 13)
    return card1, card2, card3

def evaluate_coin_bets(outcome, bets):
    counts = {"H": outcome.count("H"), "T": outcome.count("T")}
    results = {}
    if bets["All three identical"] > 0:
        if counts["H"] == 3 or counts["T"] == 3:
            results["All three identical"] = odds["Coin Flip"]["All three identical"] * bets["All three identical"]
        else:
            results["All three identical"] = -bets["All three identical"]
    if bets["More heads than tails"] > 0:
        if counts["H"] > counts["T"]:
            results["More heads than tails"] = odds["Coin Flip"]["More heads than tails"] * bets["More heads than tails"]
        else:
            results["More heads than tails"] = -bets["More heads than tails"]
    if bets["More tails than heads"] > 0:
        if counts["T"] > counts["H"]:
            results["More tails than heads"] = odds["Coin Flip"]["More tails than heads"] * bets["More tails than heads"]
        else:
            results["More tails than heads"] = -bets["More tails than heads"]
    if bets["Alternating (HTH or THT)"] > 0:
        pattern = "".join(outcome)
        if pattern in ["HTH", "THT"]:
            results["Alternating (HTH or THT)"] = odds["Coin Flip"]["Alternating (HTH or THT)"] * bets["Alternating (HTH or THT)"]
        else:
            results["Alternating (HTH or THT)"] = -bets["Alternating (HTH or THT)"]
    return results

def evaluate_dice_bets(total, bets):
    results = {}
    for condition, amount in bets.items():
        if amount == 0:
            continue
        success = False
        if condition == "Even":
            success = total % 2 == 0
        elif condition == "Odd":
            success = total % 2 == 1
        elif "or" in condition:
            options = [int(x) for x in condition.split(" or ")]
            success = total in options
        elif "-" in condition:
            low, high = map(int, condition.split("-"))
            success = low <= total <= high
        else:
            success = total == int(condition)

        results[condition] = odds["Dice"][condition] * amount if success else -amount
    return results

def evaluate_card_bets(cards, bets):
    prod = cards[0] * cards[1]
    results = {}
    for cond, amount in bets.items():
        if amount == 0:
            continue
        success = False
        if cond == "Even":
            success = prod % 2 == 0
        elif cond == "Above 50":
            success = prod > 50
        elif cond == "Above 100":
            success = prod > 100
        elif cond == "Product > 10":
            success = prod > 10
        elif cond == "Product < 40":
            success = prod < 40

        results[cond] = odds["Cards"][cond] * amount if success else -amount
    return results

# ---- UI Setup ----
import matplotlib.pyplot as plt
st.title("Betting Game")

# ---- Odds Visualization ----
true_probs = {
    "Coin Flip": {
        "All three identical": 0.25,
        "More heads than tails": 0.375,
        "More tails than heads": 0.375,
        "Alternating (HTH or THT)": 0.25,
    },
    "Dice": {
        "2 or 3": (1+2)/36,
        "4": 3/36,
        "10": 3/36,
        "6-7 or 8": (5+6+5)/36,
        "11 or 12": (2+1)/36,
        "Even": 0.5,
        "Odd": 0.5,
    },
    "Cards": {
        "Even": 0.5,
        "Above 50": 0.4423,
        "Above 100": 0.0897,
        "Product > 10": 0.946,
        "Product < 40": 0.615,
    }
}

if st.checkbox("Show Expected vs Offered Odds"):
    for category in true_probs:
        st.subheader(f"{category} Odds Comparison")
        df = pd.DataFrame({
            "Event": list(true_probs[category].keys()),
            "Expected Odds (1/p)": [round(1 / p, 2) for p in true_probs[category].values()],
            "Offered Odds": [odds[category][k] for k in true_probs[category].keys()]
        })
                df["Expected Value per $1 Bet"] = (df["Offered Odds"] * list(true_probs[category].values())) - 1
        st.dataframe(df)

        fig, ax = plt.subplots()
        ax.bar(df["Event"], df["Expected Odds (1/p)"], label="Expected", alpha=0.6)
        ax.bar(df["Event"], df["Offered Odds"], label="Offered", alpha=0.6)
        ax.set_ylabel("Odds")
        ax.set_title("Expected vs Offered Odds")
        ax.set_xticklabels(df["Event"], rotation=45, ha="right")
        ax.legend()
        st.pyplot(fig)

bankroll = st.number_input("Bankroll", value=1000.0, step=10.0)

# Odds are calculated from actual probabilities
def noisy_odds(true_prob):
    return round(1 / true_prob * random.uniform(0.9, 1.1), 2)

true_probs = {
    "Coin Flip": {
        "All three identical": 0.25,
        "More heads than tails": 0.375,
        "More tails than heads": 0.375,
        "Alternating (HTH or THT)": 0.25,
    },
    "Dice": {
        "2 or 3": (1+2)/36,
        "4": 3/36,
        "10": 3/36,
        "6-7 or 8": (5+6+5)/36,
        "11 or 12": (2+1)/36,
        "Even": 0.5,
        "Odd": 0.5,
    },
    "Cards": {
        "Even": 0.5,
        "Above 50": 0.4423,
        "Above 100": 0.0897,
        "Product > 10": 0.946,
        "Product < 40": 0.615,
    }
}


odds = {
    "Coin Flip": {
        "All three identical": noisy_odds(0.25),  # 2 outcomes: HHH, TTT out of 8 = 2/8 = 0.25
        "More heads than tails": noisy_odds(0.375),     # HHH, HHT, HTH, THH = 3/8
        "More tails than heads": noisy_odds(0.375),     # TTT, TTH, THT, HTT = 3/8
        "Alternating (HTH or THT)": noisy_odds(0.25),   # HTH or THT = 2/8 = 0.25
    },
    "Dice": {
        "2 or 3": noisy_odds((1+2)/36),             # 2: 1+1, 3: 1+2, 2+1
        "4": noisy_odds(3/36),
        "10": noisy_odds(3/36),
        "6-7 or 8": noisy_odds((5+6+5)/36),           # 6:5, 7:6, 8:5
        "11 or 12": noisy_odds((2+1)/36),
        "Even": noisy_odds(0.5),
        "Odd": noisy_odds(0.5),
    },
    "Cards": {
        "Even": round(1 / 0.5, 2),
        "Above 50": noisy_odds(0.4423),                 # approx P(X*Y > 50) for X,Y~Uniform(1,13)
        "Above 100": noisy_odds(0.0897),                # approx P(X*Y > 100)
        "Product > 10": noisy_odds(0.946),              # approx
        "Product < 40": noisy_odds(0.615),              # approx
    }
}

st.subheader("Coin Flip")
coin_bets = {}
for item in odds["Coin Flip"]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"{item} (Odds: {odds['Coin Flip'][item]})")
    with col2:
        coin_bets[item] = st.number_input(f"Bet - {item}", min_value=0.0, step=10.0, key=f"coin_{item}")

st.subheader("Dice Roll")
dice_bets = {}
for item in odds["Dice"]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"{item} (Odds: {odds['Dice'][item]})")
    with col2:
        dice_bets[item] = st.number_input(f"Bet - {item}", min_value=0.0, step=10.0, key=f"dice_{item}")

st.subheader("Card Draw")
card_bets = {}
for item in odds["Cards"]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.write(f"{item} (Odds: {odds['Cards'][item]})")
    with col2:
        card_bets[item] = st.number_input(f"Bet - {item}", min_value=0.0, step=10.0, key=f"card_{item}")

if st.button("Submit Bets"):
    total_bet = sum(coin_bets.values()) + sum(dice_bets.values()) + sum(card_bets.values())
    if total_bet > bankroll:
        st.error("You don't have enough bankroll to place these bets.")
    else:
        # Run outcomes
        coins = get_outcome_coin_flip()
        dice = get_outcome_dice_sum()
        cards = get_outcome_card_draw()

        st.write("### Outcomes")
        st.write(f"Coin Flip: {' '.join(coins)}")
        st.write(f"Dice Total: {dice}")
        st.write(f"Cards: {cards[0]}, {cards[1]}, {cards[2]} (Product: {cards[0] * cards[1]})")

        coin_results = evaluate_coin_bets(coins, coin_bets)
        dice_results = evaluate_dice_bets(dice, dice_bets)
        card_results = evaluate_card_bets(cards, card_bets)

        all_results = {**coin_results, **dice_results, **card_results}
        total_payout = sum(all_results.values())
        net_bankroll = bankroll - total_bet + total_payout

        st.write("### Results")
        st.write(pd.DataFrame.from_dict(all_results, orient="index", columns=["Payout"]))
        st.write(f"**Net Bankroll:** ${net_bankroll:.2f}")
