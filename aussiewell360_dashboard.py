
# aussiewell360_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
@st.cache_data
def load_data():
    users = pd.read_csv("data/users.csv")
    logs = pd.read_csv("data/daily_logs.csv")
    clusters = pd.read_csv("data/user_clusters.csv")
    return users, logs, clusters

users, logs, clusters = load_data()
logs['date'] = pd.to_datetime(logs['date'])

st.set_page_config(page_title="AussieWell360", layout="wide")
st.title("🍃 AussieWell360 – Smart Wellness Dashboard")

# Sidebar: Select user
user_ids = clusters['user_id'].tolist()
selected_user = st.sidebar.selectbox("Select a user:", user_ids)
user_data = clusters[clusters['user_id'] == selected_user].iloc[0]
user_logs = logs[logs['user_id'] == selected_user]

# Tab layout
personal_tab, community_tab, ai_tab = st.tabs(["🏠 Personal Dashboard", "📊 Community Insights", "🤖 AI Coach"])

# --- Personal Dashboard ---
with personal_tab:
    st.subheader(f"User {selected_user} Wellness Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Steps", int(user_data['avg_steps']))
    col2.metric("Avg Water (L)", round(user_data['avg_water'], 1))
    col3.metric("Mood Score", round(user_data['avg_mood'], 1))

    # Mood trend line
    mood_map = {'Happy': 2, 'Neutral': 1, 'Sad': 0, 'Anxious': 0}
    user_logs['mood_score'] = user_logs['mood'].map(mood_map)
    user_logs = user_logs.sort_values("date")
    user_logs['rolling_mood'] = user_logs['mood_score'].rolling(3, min_periods=1).mean()

    fig = px.line(user_logs, x='date', y='rolling_mood', title='Rolling Mood Score')
    st.plotly_chart(fig, use_container_width=True)

# --- Community Insights ---
with community_tab:
    st.subheader("Community Health Insights")
    col1, col2 = st.columns(2)

    # Pie chart: health personas
    persona_counts = clusters['health_cluster_label'].value_counts().reset_index()
    persona_counts.columns = ['Persona', 'Count']
    fig1 = px.pie(persona_counts, names='Persona', values='Count', title='Health Persona Distribution')
    col1.plotly_chart(fig1, use_container_width=True)

    # Top cities by activity
    top_cities = logs.merge(users, on='user_id')
    top_avg = top_cities.groupby('location')['steps'].mean().sort_values(ascending=False).head(5).reset_index()
    fig2 = px.bar(top_avg, x='location', y='steps', title='Top 5 Active Cities')
    col2.plotly_chart(fig2, use_container_width=True)

    # Mood trend overall
    mood_trend = logs.groupby(['date', 'mood']).size().reset_index(name='count')
    fig3 = px.line(mood_trend, x='date', y='count', color='mood', title='Mood Trends Over Time')
    st.plotly_chart(fig3, use_container_width=True)

# --- AI Coach Assistant (Mocked) ---
with ai_tab:
    st.subheader("🤖 Ask Your AI Health Coach")
    question = st.text_input("Ask something like: 'How can I feel better next week?'", "")
    if question:
        label = user_data['health_cluster_label']
        if label == "Hydrated & Active":
            reply = "You're doing great! Keep up your routines and stay consistent."
        elif label == "At Risk":
            reply = "Try drinking more water and taking a 15-min walk daily. Reflect on your mood before bed."
        else:
            reply = "You're doing okay, but consider small boosts in activity and hydration to elevate your wellbeing."
        st.success(f"💬 {reply}")
