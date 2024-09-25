import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

# File to store user data
user_data_file = "users.json"

# Load user data from the JSON file
def load_users():
    if os.path.exists(user_data_file):
        with open(user_data_file, 'r') as file:
            return json.load(file)
    return {}

# Save a new user to the JSON file
def save_user(user_data):
    users = load_users()
    users[user_data['email']] = user_data
    with open(user_data_file, 'w') as file:
        json.dump(users, file)

# Check if the user exists
def user_exists(email):
    users = load_users()
    return email in users

# Register new user
def register_user():
    st.title("Sign Up Page")
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    dob = st.date_input("Date of Birth")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if user_exists(email):
            st.error("User with this email already exists!")
        else:
            user_data = {
                "name": name,
                "phone": phone,
                "dob": str(dob),
                "email": email,
                "password": password
            }
            save_user(user_data)
            os.makedirs(name, exist_ok=True)  # Create unique folder for the user (using their name)
            st.success(f"User '{name}' registered successfully! You can now log in.")

# Login user
def login_user(email, password):
    users = load_users()
    if email in users and users[email]['password'] == password:
        return users[email]  # Return the user data on successful login
    return None

# Login Page
def login_page():
    st.title("Login Page")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.success(f"Welcome {user['name']}!")  # Use user's name instead of email
            st.session_state["user"] = user  # Store the entire user data in session
            return user["name"]
        else:
            st.error("Invalid email or password!")
    return None

# Input marks for subjects
def input_marks(user):
    st.title(f"Welcome {user['name']}")  # Display user's name instead of email
    subjects = ["Math", "English", "Science", "History", "Geography", "Physics", "Chemistry"]
    marks = {}

    for subject in subjects:
        marks[subject] = st.slider(f"Choose your marks for {subject}", 0, 100, 50)

    if st.button("Submit"):
        df = pd.DataFrame(marks.items(), columns=["Subject", "Marks"])
        df.to_csv(f"{user['name']}/marks.csv", index=False)  # Save marks in the user's folder as "marks.csv"
        st.success("Marks saved successfully!")

# Generate report with charts
def generate_report(user):
    st.title("Your Reports are Ready!")
    df = pd.read_csv(f"{user['name']}/marks.csv")  # Read the "marks.csv" from the user's folder

    # Bar Chart
    st.subheader("Average Marks - Bar Graph")
    bar_fig = px.bar(df, x="Subject", y="Marks", title="Marks per Subject")
    st.plotly_chart(bar_fig)

    # Line Graph
    st.subheader("Marks per Subject - Line Graph")
    line_fig = px.line(df, x="Subject", y="Marks", title="Marks Trend")
    st.plotly_chart(line_fig)

    # Pie Chart
    st.subheader("Marks per Subject - Pie Chart")
    pie_fig = px.pie(df, values="Marks", names="Subject", title="Marks Distribution")
    st.plotly_chart(pie_fig)

# Sign out user and reload the page
def sign_out():
    st.session_state.clear()  # Clear the session state
    st.success("You have been logged out.")
    
    # This will update the query params and cause a reload
    st.experimental_set_query_params(logged_out="true")

# Main Streamlit Application
def main():
    st.sidebar.title("Navigation")
    
    # Display different navigation options based on user state
    if "user" in st.session_state:
        choice = st.sidebar.radio(
            f"Hello, {st.session_state['user']['name']}",  # Show user's name in the sidebar
            ["Input Marks", "Generate Reports", "Sign Out"]
        )
    else:
        choice = st.sidebar.radio("Go to", ["Sign Up", "Log In"])
    
    # Control flow based on navigation choice
    if choice == "Sign Up":
        register_user()

    elif choice == "Log In":
        if "user" not in st.session_state:
            login_page()
        else:
            st.success(f"Already logged in as {st.session_state['user']['name']}")  # Display user's name

    elif choice == "Input Marks":
        if "user" in st.session_state:
            input_marks(st.session_state["user"])
        else:
            st.error("Please log in first!")

    elif choice == "Generate Reports":
        if "user" in st.session_state:
            generate_report(st.session_state["user"])
        else:
            st.error("Please log in first!")

    elif choice == "Sign Out":
        sign_out()  # Call the sign-out function when "Sign Out" is selected

if __name__ == "__main__":
    main()
