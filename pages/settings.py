import streamlit as st

st.title("⚙ Settings")

st.subheader("Account")
name = st.text_input("Name")
email = st.text_input("Email")

st.subheader("Preferences")

language = st.selectbox(
    "Language",
    ["English","Hindi","Kannada","Tamil","Telugu"]
)

ai = st.toggle("Enable AI Assistant")
voice = st.toggle("Enable Voice Assistant")
notifications = st.toggle("Notifications")

st.subheader("Security")
twofa = st.toggle("Enable Two Step Verification")

if st.button("Sign Out"):
    st.session_state.clear()
    st.success("Signed out")