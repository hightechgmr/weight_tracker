import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

st.set_page_config(page_title="Weight & Calorie Tracker", layout="wide")

st.title("🏋‍♂ Daily Weight and Calorie Tracker")

# --- DATA STORAGE ---
@st.cache_data
def load_data():
    try:
        return pd.read_csv("tracker_data.csv", parse_dates=["Date"])
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Weight", "Calories"])

data = load_data()

# --- DAILY INPUT ---
st.subheader("📥 Input Today's Data")

today = datetime.today().date()
weight = st.number_input("Weight today (kg)", min_value=30.0, max_value=200.0, step=0.1)
calories = st.number_input("Calories consumed today", min_value=0, max_value=10000, step=10)

if st.button("Submit Today’s Data"):
    if not data[(data["Date"] == pd.to_datetime(today))].empty:
        st.warning("You’ve already entered data for today.")
    else:
        new_row = pd.DataFrame({
            "Date": [today],
            "Weight": [weight],
            "Calories": [calories]
        })
        data = pd.concat([data, new_row], ignore_index=True)
        data.to_csv("tracker_data.csv", index=False)
        st.success("Data saved!")

# --- DISPLAY DATA ---
st.subheader("📈 Progress Over Time")

if not data.empty:
    data = data.sort_values("Date")
    st.line_chart(data.set_index("Date")[["Weight"]], use_container_width=True)
    st.line_chart(data.set_index("Date")[["Calories"]], use_container_width=True)

    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Weight (kg)', color='tab:blue')
    ax1.plot(data["Date"], data["Weight"], color='tab:blue', label="Weight")
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    ax2 = ax1.twinx()
    ax2.set_ylabel('Calories', color='tab:red')
    ax2.plot(data["Date"], data["Calories"], color='tab:red', label="Calories")
    ax2.tick_params(axis='y', labelcolor='tab:red')

    fig.tight_layout()
    st.pyplot(fig)

    # --- ESTIMATE FUTURE PROGRESS ---
    st.subheader("📅 Goal Prediction")

    goal_weight = st.number_input("Your goal weight (kg)", value=69.0)
    daily_deficit = 0

    if len(data) >= 2:
        days = (data["Date"].iloc[-1] - data["Date"].iloc[0]).days or 1
        weight_lost = data["Weight"].iloc[0] - data["Weight"].iloc[-1]
        daily_loss = weight_lost / days
        calories_avg = data["Calories"].tail(7).mean()
        st.write(f"📊 Avg daily weight loss: *{daily_loss:.2f} kg/day*")
        st.write(f"🔥 Avg daily calories (last 7 days): *{calories_avg:.0f} kcal*")

        remaining = data["Weight"].iloc[-1] - goal_weight
        if daily_loss > 0:
            days_to_goal = int(remaining / daily_loss)
            date_to_goal = data["Date"].iloc[-1] + timedelta(days=days_to_goal)
            st.success(f"🎯 Estimated date to reach {goal_weight} kg: *{date_to_goal.date()}*")
        else:
            st.warning("Not enough progress to estimate a goal date yet.")
    else:
        st.info("Enter more than one day to show predictions.")

else:
    st.info("No data yet. Start entering daily values!")