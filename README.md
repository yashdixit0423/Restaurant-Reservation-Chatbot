# Restaurant-Reservation-Chatbot
rule-driven restaurant chatbot that handles table reservations, waitlist management, menu &amp; policy viewing with API-based data compression (ScaleDown).
A rule-based demo dining reservation chatbot built with Streamlit.  
The chatbot guides users step by step through menu viewing, table booking, phone number collection for SMS notification, and post-booking actions such as cancellation or additional bookings.

This project intentionally avoids paid AI APIs and focuses on clear system design and predictable behavior.

---

## Features

- Guided conversational booking flow
- Optional menu display with ScaleDown text compression
- Table availability validation and optimization
- Waitlist handling when tables are unavailable
- Phone number collection with SMS notification (mocked)
- Reservation cancellation support
- Booking metrics dashboard
- Light-themed, clean UI


## Tech Stack

- Python
- Streamlit
- ScaleDown API 
- JSON-based storage

## How It Works

1. Greet the user
2. Ask whether to view the menu
3. Collect booking details step by step
4. Validate availability and confirm reservation
5. Request phone number and send SMS confirmation (mock)
6. Offer post-booking options: book again, cancel, or exit

The chatbot uses a state-driven conversation model for reliable and predictable interactions.

---

## Run Locally on streamlit

## Notes
No paid AI or external database
SMS delivery is mocked
Designed as a functional prototype, not a production system

## Project Structure

dining-reservation-bot/
│
├── app.py # Main Streamlit application
├── data/
│ ├── menu_scaledown.json # Restaurant menu
│ ├── policies_scaledown.json # Opening hours and rules
│ ├── tables.json # Table size inventory
│ ├── availability.json # Date-wise time slot availability
│ ├── reservations.json # Stored reservations
│ └── waitlist.json # Waitlisted requests
│
├── services/
│ ├── chatbot.py # Rule-based logic + ScaleDown compression
│ ├── table_optimizer.py # Table selection logic
│ ├── waitlist_manager.py # Waitlist handling
│ ├── sms_mock.py # SMS notification mock
│ └── metrics.py # Booking statistics
