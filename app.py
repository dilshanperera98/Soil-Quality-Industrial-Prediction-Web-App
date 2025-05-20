import streamlit as st
import pickle
import pandas as pd
import base64
import datetime
import os
from auth import check_authentication, logout
from auth import load_users, save_users, hash_password


# Set page configuration
st.set_page_config(
    page_title="Soil Quality Predictor",
    page_icon="🏷️",
    layout="wide"
)

# Apply custom CSS
def load_css():
    with open("style.css", "r") as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

try:
    load_css()
except FileNotFoundError:
    pass



# Check authentication first
st.session_state.current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
authenticated = check_authentication()

# Load models
@st.cache_resource
def load_models():
    models = {}
    if os.path.exists("rf_soil_quality_model.pkl"):
        with open("rf_soil_quality_model.pkl", "rb") as f:
            models["rf_soil_quality"] = pickle.load(f)

    if os.path.exists("rf_industrial_use_model.pkl"):
        with open("rf_industrial_use_model.pkl", "rb") as f:
            models["rf_industrial_use"] = pickle.load(f)

    if os.path.exists("rf_soil_quality_model_LG.pkl"):
        with open("rf_soil_quality_model_LG.pkl", "rb") as f:
            models["rf_soil_quality_LG"] = pickle.load(f)

    if os.path.exists("rf_industrial_use_model_LG.pkl"):
        with open("rf_industrial_use_model_LG.pkl", "rb") as f:
            models["rf_industrial_use_LG"] = pickle.load(f)
            
    return models

models = load_models()

# Define mappings
soil_quality_mapping = {0: "Poor", 1: "Moderate", 2: "Good"}
industrial_use_mapping = {0: "Agriculture", 1: "Construction", 2: "Landscaping"}

# Sidebar Navigation
st.sidebar.title("🏷️ Soil Quality Predictor")
st.sidebar.write(f"Welcome, {st.session_state.username}!")
page = st.sidebar.radio("Navigate", ["Home", "Predict [RandomForest]", "Predict [Logistic Regression]", "Resources","About Us", "Profile"])

# Add logout button
if st.sidebar.button("Logout"):
    logout()

# Add a horizontal separator
st.sidebar.markdown("---")

# Create some spacing to push the text towards the end of the sidebar
for _ in range(15):
    st.sidebar.write(" ")

# Add centered text at the bottom using HTML
st.sidebar.markdown(
    """
    <div style='text-align: center;'>
        
    </div>
    """,
    unsafe_allow_html=True
)

if page == "Home":
    st.header("Welcome to Soil Quality & Industrial Use Prediction")

    st.write("##### This web Application predicts soil quality and its potential industrial use based on key parameters such as texture, moisture, organic matter, pH, and electrical conductivity.")
    
    st.write("### 📌 **How It Works:**")
    st.write("##### 1️⃣ **Navigate to the Predict page using the sidebar.**")
    st.write("##### 2️⃣ **Enter the required soil parameters.**")
    st.write("##### 3️⃣ **Click Predict to get the results.**")
    st.write("### Let's get started! 🚀")

elif page == "About Us":
    st.header("📖 About Us")
    st.write("### Who We Are")
    st.write("##### We are a team of developers who developed this app to help farmers, agronomists, and industrialists understand the soil quality and its potential uses in different sectors.")
    st.write("##### Our mission is to provide reliable AI-driven predictions for optimal soil management and industrial use.")
    st.write("### Our Goal:")
    st.write("##### To empower industries and agriculture with insights on soil quality and its suitability for different industrial uses.")
    st.write("### Real-World Impact")
    st.write("##### This app has already helped several farmers optimize soil management practices, reduce costs, and enhance productivity. We're constantly working to improve the accuracy of our models and add new features that will help a wider range of industries.")
    st.write("### Contact Us")
    st.write("##### We value your feedback! Feel free to reach out to us for any inquiries or suggestions. Stay connected:")
    st.write("##### [Email Us](mailto:contact@soilpredictions.com)")
    st.write("Follow us on  [LinkedIn](https://www.linkedin.com/) | [Twitter](https://twitter.com/)")

elif page == "Predict [RandomForest]":
    st.header("🔍 Soil Quality & Industrial Use Prediction")
    st.write("##### 📍 The Random Forest model achieves a 99% accuracy level.")
    
    st.write("Enter soil parameters below to predict its quality and industrial usability.")
    
    # Input fields
    texture_options = {"Clayey": 0, "Sandy": 1, "Sandy Loam": 2, "Loamy": 3}
    texture = st.selectbox("Select Texture Type:", list(texture_options.keys()))
    texture_input = texture_options[texture]
    moisture_input = st.slider("Moisture (%)", 0.0, 100.0, 20.0)
    organic_matter_input = st.slider("Organic Matter (%)", 0.0, 10.0, 2.5)
    ph_input = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
    conductivity_input = st.number_input("Electrical Conductivity (dS/m)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

    # Prediction function
    def predict_soil_quality_industrial_use(texture, moisture, organic_matter, ph, conductivity):
        input_data = pd.DataFrame([[texture, moisture, organic_matter, ph, conductivity]],
                                 columns=['Texture', 'Moisture (%)', 'Organic Matter (%)', 'pH', 'Electrical Conductivity (dS/m)'])
        
        if "rf_soil_quality" in models and "rf_industrial_use" in models:
            soil_quality_pred = models["rf_soil_quality"].predict(input_data)[0]
            industrial_use_pred = models["rf_industrial_use"].predict(input_data)[0]
            return soil_quality_mapping.get(soil_quality_pred, "Unknown"), industrial_use_mapping.get(industrial_use_pred, "Unknown")
        else:
            return "Model not loaded", "Model not loaded"

    # Predict button
    if st.button("Predict"):  
        soil_quality, industrial_use = predict_soil_quality_industrial_use(texture_input, moisture_input, organic_matter_input, ph_input, conductivity_input)
        
        # Save prediction to user history
        if "prediction_history" not in st.session_state:
            st.session_state.prediction_history = []
            
        st.session_state.prediction_history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "RandomForest",
            "texture": texture,
            "moisture": moisture_input,
            "organic_matter": organic_matter_input,
            "ph": ph_input,
            "conductivity": conductivity_input,
            "soil_quality": soil_quality,
            "industrial_use": industrial_use
        })
        
        st.success(f"##### 🌱 **Predicted Soil Quality:** {soil_quality}")
        st.info(f"##### 🏗 **Predicted Industrial Use:** {industrial_use}")

elif page == "Predict [Logistic Regression]":
    st.header("🔍 Soil Quality & Industrial Use Prediction")
    st.write("##### 📍 The Logistic Regression model achieves a 72% accuracy level.")
    st.write("Enter soil parameters below to predict its quality and industrial usability.")
    
    # Input fields
    texture_options = {"Clayey": 0, "Sandy": 1, "Sandy Loam": 2, "Loamy": 3}
    texture = st.selectbox("Select Texture Type:", list(texture_options.keys()))
    texture_input = texture_options[texture]
    moisture_input = st.slider("Moisture (%)", 0.0, 100.0, 20.0)
    organic_matter_input = st.slider("Organic Matter (%)", 0.0, 10.0, 2.5)
    ph_input = st.number_input("pH", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
    conductivity_input = st.number_input("Electrical Conductivity (dS/m)", min_value=0.0, max_value=10.0, value=1.0, step=0.1)

    # Prediction function
    def predict_soil_quality_industrial_use(texture, moisture, organic_matter, ph, conductivity):
        input_data = pd.DataFrame([[texture, moisture, organic_matter, ph, conductivity]],
                                 columns=['Texture', 'Moisture (%)', 'Organic Matter (%)', 'pH', 'Electrical Conductivity (dS/m)'])
        
        if "rf_soil_quality_LG" in models and "rf_industrial_use_LG" in models:
            soil_quality_pred = models["rf_soil_quality_LG"].predict(input_data)[0]
            industrial_use_pred = models["rf_industrial_use_LG"].predict(input_data)[0]
            return soil_quality_mapping.get(soil_quality_pred, "Unknown"), industrial_use_mapping.get(industrial_use_pred, "Unknown")
        else:
            return "Model not loaded", "Model not loaded"

    # Predict button
    if st.button("Predict"):  
        soil_quality, industrial_use = predict_soil_quality_industrial_use(texture_input, moisture_input, organic_matter_input, ph_input, conductivity_input)
        
        # Save prediction to user history
        if "prediction_history" not in st.session_state:
            st.session_state.prediction_history = []
            
        st.session_state.prediction_history.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "model": "Logistic Regression",
            "texture": texture,
            "moisture": moisture_input,
            "organic_matter": organic_matter_input,
            "ph": ph_input,
            "conductivity": conductivity_input,
            "soil_quality": soil_quality,
            "industrial_use": industrial_use
        })
        
        st.success(f"##### 🌱 **Predicted Soil Quality:** {soil_quality}")
        st.info(f"##### 🏗 **Predicted Industrial Use:** {industrial_use}")

elif page == "Resources":
    st.header("📚 Learning About Soils")
    
    with st.expander("##### Introduction to Soil Science"):
        st.write("Definition of Soil :")
        st.write("Soil is a natural resource that forms on the Earth's surface. It consists of mineral particles, organic matter, water, and air. Soil is crucial for plant growth, water filtration, and supporting ecosystems.'")
        st.write("Importance of Soil :")
        st.write("Soil provides nutrients, water retention, and mechanical support for plants. It also serves as a habitat for diverse organisms, plays a vital role in carbon sequestration, and helps filter water")
        st.write("Soil and Ecosystem Balance :")
        st.write("Healthy soil maintains the balance of various ecosystems, sustaining plant life and contributing to biodiversity")

    with st.expander("##### Key Soil Properties"):
        st.write("Soil Texture :")
        st.write("Soil texture refers to the proportion of sand, silt, and clay in the soil. It determines how water and air move through the soil and affects plant growth")
        st.write("pH Levels :")
        st.write("Soil pH influences nutrient availability for plants. Most plants thrive in neutral to slightly acidic soils (pH 6-7).")
        st.write("Organic Matter :")
        st.write("The decayed remains of plants and animals. Organic matter improves soil structure, moisture retention, and nutrient content.")
        st.write("Soil Moisture :")
        st.write("The amount of water present in the soil is essential for plant growth. Proper moisture levels promote healthy crops.")
        st.write("Electrical Conductivity :")
        st.write("Indicates the level of salts and minerals in the soil, which can affect plant growth if too high.")

    with st.expander("##### Types of Soil"):
        st.write("**Clay Soil:** Clay particles are small and dense, which makes the soil sticky when wet. It is nutrient-rich but poorly drained.")
        st.write("**Sandy Soil:** Sandy soil drains quickly and is warm, but it often lacks nutrients and moisture retention.")
        st.write("**Loamy Soil:** Loam is considered the best soil for most plants, with a balanced texture that holds moisture yet drains well.")
        st.write("**Peaty Soil:** High in organic material, peat soil retains moisture and is very fertile.")
        st.write("**Saline Soil:** Contains a high amount of salts, which can negatively affect plant growth. Usually requires specific treatments to make it fertile.")

    with st.expander("##### Soil Fertility and Management"):
        st.write("**Fertility Factors:** Soil fertility is determined by the availability of essential nutrients like nitrogen, phosphorus, potassium, and other micronutrients.")
        st.write("**Soil Amendments:** Organic materials such as compost, mulch, and green manure can enhance soil fertility.")
        st.write("**Soil Erosion:** Soil erosion is caused by wind, water, or human activity and can degrade soil quality. Proper management practices, such as planting cover crops, can prevent erosion.")
        st.write("**Soil Conservation:** Methods to protect soil from degradation, including contour farming, terracing, and no-till agriculture.")

    with st.expander("##### Importance of Soil in Agriculture"):
        st.write("**Role in Crop Production:** Soil provides essential nutrients and water to crops. Fertile soil improves yields and ensures the sustainability of agricultural practices.")
        st.write("**Soil and Irrigation:** Proper soil moisture is essential for irrigation practices. Different soil types require different irrigation techniques to maintain optimal moisture.")
        st.write("**Soil Testing:** Soil testing helps determine nutrient levels and pH, allowing farmers to amend soil and optimize fertilizer use.")
        st.write("**Soil and Climate Change:** Soil plays a significant role in climate change by sequestering carbon and affecting greenhouse gas emissions. Sustainable farming practices help mitigate the impacts of climate change.")

    with st.expander("##### Soil and Environmental Sustainability"):
        st.write("**Soil as a Carbon Sink:** Healthy soils store carbon, which helps mitigate climate change by reducing atmospheric CO2 levels.")
        st.write("**Soil and Biodiversity:** Soils host a wide range of organisms, from bacteria to insects, which support ecosystems and contribute to biodiversity.")
        st.write("**Soil Pollution:** Soil can become polluted by chemicals, heavy metals, and industrial waste. Contaminated soils require treatment and restoration to restore their health.")

    with st.expander("##### Recommended Resources"):
        st.write("### Books")
        st.write("- *The Nature and Properties of Soils* by Nyle C. Brady")
        st.write("- *Soil Science Simplified* by Donald H. L. Bracey")
        st.write("- *Introduction to Soil and Water Conservation Technology* by R. D. Gupta")
    
        st.write("### Online Courses")
        st.write("- [Soil Science Online Course (Coursera)](https://www.coursera.org/learn/soil-science)")
        st.write("- [Soil Management and Fertility (Udemy)](https://www.udemy.com/course/soil-management/)")

elif page == "Profile":
    st.header("👤 User Profile")
    
    # Display user information
    st.subheader("Account Information")
    st.write(f"##### **Username:** {st.session_state.username}")
    
    # Prediction History
    st.subheader("Prediction History")
    
    if "prediction_history" in st.session_state and st.session_state.prediction_history:
        history_df = pd.DataFrame(st.session_state.prediction_history)
        st.dataframe(history_df)
        
        # Option to download history as CSV
        csv = history_df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="prediction_history.csv">Download History as CSV</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.info("No prediction history available. Make some predictions to see your history here.")
    
    # Account settings
    st.subheader("Account Settings")
    
    # Change password section
    # with st.expander("Change Password"):
    #     with st.form("change_password_form"):
    #         current_password = st.text_input("Current Password", type="password")
    #         new_password = st.text_input("New Password", type="password")
    #         confirm_new_password = st.text_input("Confirm New Password", type="password")
    #         submit = st.form_submit_button("Update Password")
            
    #         if submit:
    #             st.warning("Password change functionality is not implemented in this demo version.")

    with st.expander("##### Change Password"):
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_new_password = st.text_input("Confirm New Password", type="password")
            submit = st.form_submit_button("Update Password")

            if submit:
                if not current_password or not new_password or not confirm_new_password:
                    st.error("Please fill in all fields.")
                elif new_password != confirm_new_password:
                    st.error("New passwords do not match.")
                else:
                    users = load_users()
                    username = st.session_state.get("username")

                    if username not in users:
                        st.error("User not found. Please login again.")
                    else:
                        # Check if current password matches
                        if users[username]["password"] != hash_password(current_password):
                            st.error("Current password is incorrect.")
                        else:
                            # Update password and save
                            users[username]["password"] = hash_password(new_password)
                            save_users(users)
                            st.success("Password updated successfully!")
