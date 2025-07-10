import streamlit as st
import requests
import pandas as pd

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

# --- Authentication ---
def login(username, password):
    """Attempt to login and return token."""
    try:
        response = requests.post(
            f"{BACKEND_URL}/token",
            data={"username": username, "password": password}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        st.error(f"Login failed: {e}")
        # More specific error for 401
        if e.response and e.response.status_code == 401:
            st.error("Incorrect username or password.")
        return None

def get_products(token):
    """Fetch products from the backend."""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BACKEND_URL}/products/", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch products: {e}")
        return []

# --- UI ---
st.title("Supermarket POS System")

# Initialize session state for token
if 'token' not in st.session_state:
    st.session_state.token = None

# Login Form
if st.session_state.token is None:
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            token = login(username, password)
            if token:
                st.session_state.token = token
                st.success("Login successful!")
                # Rerun the script to reflect the new state
                st.experimental_rerun()

# Main Application (if logged in)
if st.session_state.token:
    st.header("Product Management")
    
    products = get_products(st.session_state.token)
    
    if products:
        # Convert to DataFrame for better display
        df = pd.DataFrame(products)
        st.dataframe(df)
    else:
        st.warning("No products found.")

    # Logout Button
    if st.button("Logout"):
        st.session_state.token = None
        st.experimental_rerun() 