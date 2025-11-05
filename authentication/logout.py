import streamlit as st
from utils.auth import logout_user
from utils.supabase_methods import get_student, get_user

user = get_user()
student = get_student() if user else None

if user:
    st.title(f"Hello, {student.name} {student.surname}!" if student else "Hello user!")
    if st.button("Logout", on_click=logout_user, type="primary"):
        st.success("You have been logged out.")
else:
    st.title("You are not logged in.")