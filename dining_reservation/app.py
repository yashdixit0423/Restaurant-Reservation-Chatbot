import json
import streamlit as st
from datetime import datetime

from services.table_optimizer import in_hours, pick_table
from services.waitlist_manager import add as add_waitlist
from services.sms_mock import send_sms
from services.metrics import stats
from services.chatbot import scaledown_compress


# Utility functions

def load(path):
    with open(path, "r") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# Load data

menu = load("data/menu_scaledown.json")
policies = load("data/policies_scaledown.json")
availability = load("data/availability.json")


# Streamlit setup

st.set_page_config(page_title="Restaurant Reservation Bot", page_icon="🍽️")
st.title(" Restaurant Chatbot")


# Session state initialization

if "chat" not in st.session_state:
    st.session_state.chat = []

if "flow_state" not in st.session_state:
    st.session_state.flow_state = "GREETING"

if "booking_data" not in st.session_state:
    st.session_state.booking_data = {
        "people": None,
        "date": None,
        "time": None,
        "phone": None,
        "reservation_id": None
    }


# Initial greeting 

if st.session_state.flow_state == "GREETING":
    st.session_state.chat.append(
        ("assistant", "Hello! I am your assistant, I can help you from reservation to cancellation... Would you like to see the menu first? (yes / no)")
    )
    st.session_state.flow_state = "ASK_MENU"


#  chat history

for role, msg in st.session_state.chat:
    with st.chat_message(role):
        st.write(msg)

# User input

user = st.chat_input("Type your message...")
if not user:
    st.stop()

st.session_state.chat.append(("user", user))
with st.chat_message("user"):
    st.write(user)

reply = ""
state = st.session_state.flow_state
data = st.session_state.booking_data
u = user.strip().lower()


# Conversation flow

if state == "ASK_MENU":
    if u in ["yes", "y"]:
        menu_text = "\n".join(
            f"{m['name']} ({', '.join(m['tags'])}) - ${m['price']}"
            for m in menu["menu"]
        )
        reply = scaledown_compress(menu_text)
        reply += "\n\nWould you like to book a table? (yes / no)"
    else:
        reply = "Alright. Would you like to book a table? (yes / no)"

    st.session_state.flow_state = "ASK_BOOK"

elif state == "ASK_BOOK":
    if u in ["yes", "y"]:
        reply = "How many people?"
        st.session_state.flow_state = "ASK_PEOPLE"
    else:
        reply = "Okay 😊 You can refresh the page to exit."

elif state == "ASK_PEOPLE":
    if not u.isdigit():
        reply = "Please enter a number. Example: 2"
    else:
        data["people"] = int(u)
        reply = "Please enter date (DD-MM-YYYY)"
        st.session_state.flow_state = "ASK_DATE"

elif state == "ASK_DATE":
    try:
        datetime.strptime(user.strip(), "%d-%m-%Y")
        data["date"] = user.strip()
        reply = "Please enter time (HH:MM, 24-hour format)"
        st.session_state.flow_state = "ASK_TIME"
    except ValueError:
        reply = "Invalid date format. Please use DD-MM-YYYY."

elif state == "ASK_TIME":
    try:
        clean_time = user.strip()
        datetime.strptime(clean_time, "%H:%M")
        data["time"] = clean_time

        d = data["date"]
        t = data["time"]
        p = data["people"]

        date_key = datetime.strptime(d, "%d-%m-%Y").strftime("%Y-%m-%d")

        if date_key not in availability:
            reply = "Sorry, we do not have availability for this date. Please try another date."

        elif t not in availability[date_key]:
            available_times = list(availability[date_key].keys())
            reply = (
                "That time slot is not available.\n\n"
                f"Available times are: {', '.join(available_times)}"
            )

        elif not in_hours(policies["hours"]["open"], policies["hours"]["close"], t):
            reply = "That time is outside opening hours."

        else:
            slot = availability[date_key][t]
            table = pick_table(p, slot)

            if not table:
                add_waitlist({"date": date_key, "time": t, "people": p})
                reply = "No table available. You have been added to the waitlist."

            else:
                slot[str(table)] -= 1
                save("data/availability.json", availability)

                reservations = load("data/reservations.json")
                reservation_id = f"R{int(datetime.now().timestamp())}"

                reservations["reservations"].append({
                    "reservation_id": reservation_id,
                    "date": date_key,
                    "time": t,
                    "people": p,
                    "table": table,
                    "status": "CONFIRMED"
                })
                save("data/reservations.json", reservations)

                data["reservation_id"] = reservation_id

                reply = (
                    f"✅ Reservation confirmed!\n\n"
                    f"Reservation ID: {reservation_id}\n"
                    f"People: {p}\n"
                    f"Date: {d}\n"
                    f"Time: {t}\n"
                    f"Table: {table}\n\n"
                    "Please enter your phone number for SMS confirmation."
                )

                st.session_state.flow_state = "ASK_PHONE"

    except ValueError:
        reply = "Invalid time format. Please use HH:MM (example: 19:00)."

elif state == "ASK_PHONE":
    phone = user.strip()

    if not phone.isdigit() or len(phone) < 8:
        reply = "Please enter a valid phone number (digits only)."
    else:
        data["phone"] = phone
        send_sms(
            phone,
            f"Your reservation {data['reservation_id']} is confirmed for {data['date']} at {data['time']}."
        )

        reply = (
            "📩 SMS confirmation sent!\n\n"
            "What would you like to do next?\n"
            "1️⃣ Book another table\n"
            "2️⃣ Cancel this reservation\n"
            "3️⃣ Exit"
        )

        st.session_state.flow_state = "POST_BOOK"

elif state == "POST_BOOK":
    if "1" in u or "another" in u:
        st.session_state.booking_data = {
            "people": None,
            "date": None,
            "time": None,
            "phone": None,
            "reservation_id": None
        }
        reply = "Sure! How many people?"
        st.session_state.flow_state = "ASK_PEOPLE"

    elif "2" in u or "cancel" in u:
        reservations = load("data/reservations.json")

        for r in reservations["reservations"]:
            if r.get("reservation_id") == data["reservation_id"]:
                r["status"] = "CANCELLED"
                break

        save("data/reservations.json", reservations)

        reply = (
            f"❌ Reservation {data['reservation_id']} has been cancelled.\n\n"
            "Would you like to book another table? (yes / no)"
        )

        st.session_state.flow_state = "ASK_BOOK"

    else:
        reply = "Thank you for visiting 😊 Have a great day!"
        st.session_state.flow_state = "END"

else:
    reply = "Session ended. Refresh the page to start again."

# Display assistant reply

st.session_state.chat.append(("assistant", reply))
with st.chat_message("assistant"):
    st.write(reply)

# Sidebar metrics

with st.sidebar:
    st.header("Metrics")
    st.json(stats())
