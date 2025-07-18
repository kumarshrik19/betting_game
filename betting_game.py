import random
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from streamlit import rerun

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
            results["All three identical"] = 0 #-bets["All three identical"]
    if bets["More heads than tails"] > 0:
        if counts["H"] > counts["T"]:
            results["More heads than tails"] = odds["Coin Flip"]["More heads than tails"] * bets["More heads than tails"]
        else:
            results["More heads than tails"] = 0 #-bets["More heads than tails"]
    if bets["More tails than heads"] > 0:
        if counts["T"] > counts["H"]:
            results["More tails than heads"] = odds["Coin Flip"]["More tails than heads"] * bets["More tails than heads"]
        else:
            results["More tails than heads"] = 0 #-bets["More tails than heads"]
    if bets["Alternating (HTH or THT)"] > 0:
        pattern = "".join(outcome)
        if pattern in ["HTH", "THT"]:
            results["Alternating (HTH or THT)"] = odds["Coin Flip"]["Alternating (HTH or THT)"] * bets["Alternating (HTH or THT)"]
        else:
            results["Alternating (HTH or THT)"] = 0 #-bets["Alternating (HTH or THT)"]
    return results

def evaluate_dice_bets(total, bets):
    results = {}
    for condition, amount in bets.items():
        if amount == 0:
            continue
        success = False
        try:
            if condition == "Even":
                success = total % 2 == 0
            elif condition == "Odd":
                success = total % 2 == 1
            elif condition == "2 or 3":
                success = total in [2,3]
            elif condition == "6-7 or 8":
                success = total in [6,7,8]
            elif condition == "11 or 12":
                success = total in [11,12]
            else:
                success = total == int(condition)
            results[condition] = odds["Dice"][condition] * amount if success else 0
        except Exception as e:
            results[condition] = f"Error: {e}"
    return results

def evaluate_card_bets(cards, bets):
    prod = cards[0] * cards[1]
    results = {}
    for cond, amount in bets.items():
        if amount == 0:
            continue
        success = False
        if cond == "Product is Even":
            success = prod % 2 == 0
        elif cond == "Product > 50":
            success = prod > 50
        elif cond == "Product > 100":
            success = prod > 100
        elif cond == "Product > 10":
            success = prod > 10
        elif cond == "Product < 40":
            success = prod < 40
        results[cond] = odds["Cards"][cond] * amount if success else 0
    return results


true_probs = {
    "Coin Flip": {
        "All three identical": 0.25,
        "More heads than tails": 0.5,
        "More tails than heads": 0.5,
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
        "Product is Even": .715,
        "Product > 50": 0.407,
        "Product > 100": 0.1343,
        "Product > 10": 0.841,
        "Product < 40": 0.478,
    }
}


def noisy_odds(true_prob):
    return round(1 / true_prob * random.uniform(0.9, 1.1), 2)

def generate_odds():
    return {
        "Coin Flip": {
            "All three identical": noisy_odds(true_probs["Coin Flip"]["All three identical"]),
            "More heads than tails": noisy_odds(true_probs["Coin Flip"]["More heads than tails"]),
            "More tails than heads": noisy_odds(true_probs["Coin Flip"]["More tails than heads"]),
            "Alternating (HTH or THT)": noisy_odds(true_probs["Coin Flip"]["Alternating (HTH or THT)"]),
        },
        "Dice": {
            "2 or 3": noisy_odds(true_probs["Dice"]["2 or 3"]),
            "4": noisy_odds(true_probs["Dice"]["4"]),
            "10": noisy_odds(true_probs["Dice"]["10"]),
            "6-7 or 8": noisy_odds(true_probs["Dice"]["6-7 or 8"]),
            "11 or 12": noisy_odds(true_probs["Dice"]["11 or 12"]),
            "Even": noisy_odds(true_probs["Dice"]["Even"]),
            "Odd": noisy_odds(true_probs["Dice"]["Odd"]),
        },
        "Cards": {
            "Product is Even": noisy_odds(true_probs["Cards"]["Product is Even"]),
            "Product > 50": noisy_odds(true_probs["Cards"]["Product > 50"]),
            "Product > 100": noisy_odds(true_probs["Cards"]["Product > 100"]),
            "Product > 10": noisy_odds(true_probs["Cards"]["Product > 10"]),
            "Product < 40": noisy_odds(true_probs["Cards"]["Product < 40"]),
        }
    }

# ---- Session State Initialization ----
if "bankroll" not in st.session_state:
    st.session_state.bankroll = 1000.0
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "results" not in st.session_state:
    st.session_state.results = None
if "odds" not in st.session_state:
    st.session_state.odds = generate_odds()
if "clear_bets_flag" not in st.session_state:     
    st.session_state.clear_bets_flag = False

odds = st.session_state.odds

#st.title("Betting Game")
#st.write(f"### Current Bankroll: ${st.session_state.bankroll:.2f}")
if st.session_state.submitted == True: 
    st.write(f"### Current Bankroll: ${st.session_state.bankroll-st.session_state.last_win:.2f}, Win/Loss: {st.session_state.last_win:.2f}")
else:
    st.write(f"### Current Bankroll: ${st.session_state.bankroll:.2f}")
        

# ---- Expected vs Offered Odds View ----

if st.checkbox("Show Expected vs Offered Odds"):
    for category in true_probs:
        st.subheader(f"{category} Odds Comparison")
        df = pd.DataFrame({
            "Event": list(true_probs[category].keys()),
            "Expected Odds (1/p)": [round(1 / p, 2) for p in true_probs[category].values()],
            "Offered Odds": [odds[category][k] for k in true_probs[category].keys()]
        })
        df["Expected Value per $1 Bet"] = df["Offered Odds"] * list(true_probs[category].values()) - 1
        st.dataframe(df)

        if False:
            fig, ax = plt.subplots()
            ax.bar(df["Event"], df["Expected Odds (1/p)"], label="Expected", alpha=0.6)
            ax.bar(df["Event"], df["Offered Odds"], label="Offered", alpha=0.6)
            ax.set_ylabel("Odds")
            ax.set_title("Expected vs Offered Odds")
            ax.set_xticklabels(df["Event"], rotation=45, ha="right")
            ax.legend()
            st.pyplot(fig)


# ---- UI ----

def bet_input(label, key):
    val = 0.0 if st.session_state.clear_bets_flag else st.session_state.get(key, 0.0)
    return st.number_input(label, min_value=0.0, step=10.0, key=key, value=val)


def safe_key(item):
    return f"{item.replace(' ', '_').replace('(', '').replace(')', '').replace('>', 'gt').replace('<', 'lt').replace('-', '_').replace('or', '_or_')}"
    
#st.subheader("3 Coin Flip")
st.markdown("<h4 style='color:#1f77b4;'>3 Coin Flip</h3>", unsafe_allow_html=True)
coin_bets = {}
coin_cols = st.columns(len(odds["Coin Flip"]))
for idx, item in enumerate(odds["Coin Flip"]):
    with coin_cols[idx]:
        st.markdown(f"**{item}** <br>Odds: <b style='color:red'>{odds['Coin Flip'][item]}<b>", unsafe_allow_html=True)
        coin_bets[item] = bet_input("", f"coin_{safe_key(item)}")

#st.subheader("Sum of two Dice Roll")
st.markdown("<h4 style='color:#1f77b4;'>Sum of two Dice Roll</h3>", unsafe_allow_html=True)
dice_bets = {}
dice_cols = st.columns(len(odds["Dice"]))
for idx, item in enumerate(odds["Dice"]):
    with dice_cols[idx]:
        st.markdown(f"**{item}** <br>Odds: <b style='color:red'>{odds['Dice'][item]}<b>", unsafe_allow_html=True)
        dice_bets[item] = bet_input("", f"dice_{safe_key(item)}")

#st.subheader("Product of two Card Draw")
st.markdown("<h4 style='color:#1f77b4;'>Product of two Card Draw</h3>", unsafe_allow_html=True)
card_bets = {}
card_cols = st.columns(len(odds["Cards"]))
for idx, item in enumerate(odds["Cards"]):
    with card_cols[idx]:
        st.markdown(f"**{item}** <br>Odds: <b style='color:red'>{odds['Cards'][item]}<b>", unsafe_allow_html=True)
        card_bets[item] = bet_input("", f"card_{safe_key(item)}")


if st.session_state.get("clear_bets_flag"):
    st.session_state.clear_bets_flag = False
    
# ---- Buttons ----

button_cols = st.columns(2)


with button_cols[1]:
    if st.button("Clear Bets"):
        for key in list(st.session_state.keys()):
            if key.startswith("coin_") or key.startswith("dice_") or key.startswith("card_"):
                del st.session_state[key]
        st.session_state.submitted = False
        st.session_state.results = None
        st.session_state.odds = generate_odds()
        st.session_state.clear_bets_flag = True
        st.rerun()


with button_cols[0]:
    if st.button("Submit Bets") or st.session_state.submitted:
        submit_pressed = not st.session_state.submitted

        if submit_pressed: # generate new coins/dice/cards
            st.session_state.coin_bets = coin_bets
            st.session_state.dice_bets = dice_bets
            st.session_state.card_bets = card_bets

            st.session_state.coins = get_outcome_coin_flip()
            st.session_state.dice = get_outcome_dice_sum()
            st.session_state.cards = get_outcome_card_draw()
        
        coin_bets = st.session_state.coin_bets
        dice_bets = st.session_state.dice_bets
        card_bets = st.session_state.card_bets
        
        bankroll = st.session_state.bankroll
        total_bet = sum(coin_bets.values()) + sum(dice_bets.values()) + sum(card_bets.values())
        if total_bet > bankroll:
            st.error("You don't have enough bankroll to place these bets.")
        else:
            coins = st.session_state.coins
            dice = st.session_state.dice
            cards = st.session_state.cards

            #st.write("### Outcomes")
            st.markdown("<h4 style='color:#1f77b4;'>Outcomes</h3>", unsafe_allow_html=True)
            
            st.write(f"Coin Flip: {' '.join(coins)}")
            st.write(f"Dice Total: {dice}")
            st.write(f"Cards: {cards[0]}, {cards[1]}, {cards[2]} (Product of first two: {cards[0] * cards[1]})")

            coin_results = evaluate_coin_bets(coins, coin_bets)
            dice_results = evaluate_dice_bets(dice, dice_bets)
            card_results = evaluate_card_bets(cards, card_bets)

            all_results = {**coin_results, **dice_results, **card_results}
            total_payout = sum(all_results.values())
            
            if submit_pressed:  # update bankroll and states
                net_bankroll = st.session_state.bankroll - total_bet + total_payout
                st.session_state.submitted = True
                st.session_state.bankroll = net_bankroll
                st.session_state.last_win = total_payout - total_bet
            
            st.session_state.results = all_results
            #st.write("### Results")
            #st.markdown("<h3 style='color:#1f77b4;'>Results</h3>", unsafe_allow_html=True)
            st.markdown(f"<h4 style='color:#52ef50;'>Results: Bets ${total_bet}, Payout ${total_payout}, New Bankroll ${st.session_state.bankroll:.2f}</h4>", unsafe_allow_html=True)
            #st.write(f"**New Bankroll:** ${net_bankroll:.2f}")

            #st.write(f"**Bets results:**\n")
            # Group results by category
            coin_results = {k: v for k, v in all_results.items() if k in odds["Coin Flip"]}
            dice_results = {k: v for k, v in all_results.items() if k in odds["Dice"]}
            card_results = {k: v for k, v in all_results.items() if k in odds["Cards"]}

            def display_result_row(results_dict, bets, label, max_cols=4):
                st.markdown(f"**{label}**")
                items = list(results_dict.items())
                rows = (len(items) + max_cols - 1) // max_cols

                for r in range(rows):
                    cols = st.columns(max_cols)
                    for i in range(max_cols):
                        idx = r * max_cols + i
                        if idx < len(items):
                            event, payout = items[idx]
                            bet = bets[event]
                            with cols[i]:
                                if (label == "Dice Roll"):
                                    st.markdown(f"*Sum is {event}*, bet: {bet:.2f} $ payout: {payout:,.2f}")
                                else:
                                    st.markdown(f"*{event}*, bet: {bet:.2f}, $ payout: {payout:,.2f}")
                        else:
                            with cols[i]:
                                st.markdown("")  # Empty to preserve spacing
                        
            display_result_row(coin_results, coin_bets, "Coin Flip")
            display_result_row(dice_results, dice_bets, "Dice Roll")
            display_result_row(card_results, card_bets, "Card Draw")
            if submit_pressed:
                st.rerun()


