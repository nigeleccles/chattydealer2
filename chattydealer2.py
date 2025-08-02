import streamlit as st
import random
import openai

# --- Deck Utilities ---
suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
deck = [f"{rank}{suit}" for suit in suits for rank in ranks]

def card_value(card):
    rank = card[:-1]
    if rank in ['J', 'Q', 'K']:
        return 10
    elif rank == 'A':
        return 11
    else:
        return int(rank)

def hand_value(hand):
    value = sum(card_value(card) for card in hand)
    aces = sum(1 for card in hand if card[:-1] == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def get_dealer_comment(action, player_hand, dealer_visible_card):
    prompt = (
        f"You are a sarcastic blackjack dealer. The player just chose to '{action}'. "
        f"Their hand is: {player_hand} (total {hand_value(player_hand)}). "
        f"The dealer's visible card is: {dealer_visible_card}. "
        f"Respond with a short, funny, sarcastic comment."
    )

    try:
        client = openai.OpenAI(api_key="xxx")  
        response = client.chat.completions.create(
           model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a sarcastic blackjack dealer in a casino."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=60,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Dealer is speechless: {e}]"

# --- Initialize Session State ---
for key in ['player_hand', 'dealer_hand', 'game_over', 'result', 'dealer_comment']:
    if key not in st.session_state:
        st.session_state[key] = []

if not st.session_state.player_hand:
    st.session_state.player_hand = random.sample(deck, 2)
    st.session_state.dealer_hand = random.sample(
        [c for c in deck if c not in st.session_state.player_hand], 2)
    st.session_state.game_over = False
    st.session_state.result = ""
    st.session_state.dealer_comment = ""

# --- UI ---
st.title("🃏 Blackjack with a Sarcastic Dealer (GPT-4)")

st.subheader("Your Hand:")
st.write(f"{'  '.join(st.session_state.player_hand)}")
player_val = hand_value(st.session_state.player_hand)
st.write(f"Total: {player_val}")

st.subheader("Dealer's Hand:")
if st.session_state.game_over:
    st.write(f"{'  '.join(st.session_state.dealer_hand)}")
    dealer_val = hand_value(st.session_state.dealer_hand)
    st.write(f"Total: {dealer_val}")
else:
    st.write(f"{st.session_state.dealer_hand[0]}  [Hidden]")

# --- Buttons ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Hit") and not st.session_state.game_over:
        remaining_cards = [c for c in deck if c not in st.session_state.player_hand + st.session_state.dealer_hand]
        new_card = random.choice(remaining_cards)
        st.session_state.player_hand.append(new_card)
        if hand_value(st.session_state.player_hand) > 21:
            st.session_state.result = "💥 You busted! Dealer wins."
            st.session_state.game_over = True

        st.session_state.dealer_comment = get_dealer_comment(
            "Hit", st.session_state.player_hand, st.session_state.dealer_hand[0]
        )

with col2:
    if st.button("Stand") and not st.session_state.game_over:
        while hand_value(st.session_state.dealer_hand) < 17:
            remaining_cards = [c for c in deck if c not in st.session_state.player_hand + st.session_state.dealer_hand]
            new_card = random.choice(remaining_cards)
            st.session_state.dealer_hand.append(new_card)

        player_val = hand_value(st.session_state.player_hand)
        dealer_val = hand_value(st.session_state.dealer_hand)

        if dealer_val > 21 or player_val > dealer_val:
            st.session_state.result = "🎉 You win!"
        elif dealer_val == player_val:
            st.session_state.result = "🤝 It's a tie!"
        else:
            st.session_state.result = "🏴 Dealer wins!"
        st.session_state.game_over = True

        st.session_state.dealer_comment = get_dealer_comment(
            "Stand", st.session_state.player_hand, st.session_state.dealer_hand[0]
        )

with col3:
    if st.button("Restart"):
        for key in ['player_hand', 'dealer_hand', 'game_over', 'result', 'dealer_comment']:
            st.session_state[key] = []

# --- Result ---
if st.session_state.result:
    st.markdown(f"### {st.session_state.result}")

# --- Dealer Comment ---
if st.session_state.dealer_comment:
    st.markdown(f"**Dealer says:** _{st.session_state.dealer_comment}_")

