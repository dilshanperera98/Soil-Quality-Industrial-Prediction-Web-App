import streamlit as st
import pickle
import os
import hashlib
import json
from pathlib import Path

# File to store user credentials
USER_DB_FILE = "users.pkl"

def initialize_user_db():
    """Initialize the user database if it doesn't exist"""
    if not os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, "wb") as f:
            pickle.dump({}, f)

def hash_password(password):
    """Create a hashed version of the password"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from the pickle file"""
    try:
        with open(USER_DB_FILE, "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError):
        return {}

def save_users(users):
    """Save users dictionary to pickle file"""
    with open(USER_DB_FILE, "wb") as f:
        pickle.dump(users, f)

def register_user(username, password, email):
    """Register a new user"""
    users = load_users()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists"
    
    # Create new user entry
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "created_at": st.session_state.get("current_time", "")
    }
    
    save_users(users)
    return True, "Registration successful"

def authenticate_user(username, password):
    """Authenticate a user"""
    users = load_users()
    
    if username not in users:
        return False, "Invalid username or password"
    
    if users[username]["password"] != hash_password(password):
        return False, "Invalid username or password"
    
    return True, "Authentication successful"

def login_page():
    """Display the login page"""
    st.title("Welcome to Soil Condition Predictor – Analyze Your Soil Better")
    
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if not username or not password:
                st.error("Please enter both username and password")
                return False
                
            success, message = authenticate_user(username, password)
            if success:
                st.success(message)
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()  # 🔁 This forces rerun to redirect immediately
                return True
            else:
                st.error(message)
                return False

    col1, col2, col3 = st.columns([1, 0.6, 1])
    with col2:            
            if st.button("Don't have an account? Register here"):
                st.session_state.show_register = True
                st.session_state.show_login = False
                st.rerun()
        
    return False


def register_page():
    """Display the registration page"""
    st.title("Welcome to Soil Condition Predictor – Analyze Your Soil Better")
    
    with st.form("register_form"):
        st.subheader("Register")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Register")
        
        if submit:
            if not username or not email or not password or not confirm_password:
                st.error("Please fill in all fields")
                return
                
            if len(username) < 4:
                st.error("Username must be at least 4 characters")
                return
                
            if len(password) < 6:
                st.error("Password must be at least 6 characters")
                return
                
            if password != confirm_password:
                st.error("Passwords do not match")
                return
                
            if "@" not in email or "." not in email:
                st.error("Please enter a valid email")
                return
                
            success, message = register_user(username, password, email)
            
            if success:
                st.success(message)
                st.session_state.show_login = True
                st.session_state.show_register = False
                st.rerun()

            else:
                st.error(message)

    col1, col2, col3 = st.columns([1, 0.6, 1])
    with col2:                
        if st.button("Already have an account? Login here"):
            st.session_state.show_login = True
            st.session_state.show_register = False
            st.rerun()
    return False

def initialize_auth_state():
    """Initialize session state variables for authentication"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        
    if "username" not in st.session_state:
        st.session_state.username = None
        
    if "show_login" not in st.session_state:
        st.session_state.show_login = True
        
    if "show_register" not in st.session_state:
        st.session_state.show_register = False

# def logout():
#     """Log out the current user"""
#     st.session_state.logged_in = False
#     st.session_state.username = None
#     st.session_state.show_login = True
#     st.experimental_rerun()

def logout():
    if 'logged_in' in st.session_state:
        st.session_state['logged_in'] = False
    if 'user' in st.session_state:
        del st.session_state['user']
    
    st.rerun()

def check_authentication():
    """Check if user is authenticated and handle auth flow"""
    initialize_auth_state()
    initialize_user_db()
    
    if not st.session_state.logged_in:
        if st.session_state.show_login:
            login_page()
        elif st.session_state.show_register:
            register_page()
        st.stop()
    
    return True