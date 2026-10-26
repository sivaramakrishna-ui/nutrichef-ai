import streamlit as st
from openai import OpenAI
import time

# ---------------------------------------------------------
# 1. WEB CONFIGURATION & STATE
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="icon.png")

# Initialize Session State for Recipe History
if "recipe_history" not in st.session_state:
    st.session_state.recipe_history = []

# SECURE AUTHENTICATION
try:
    GROQ_TOKEN = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Token not found!")
    st.info("Go to Streamlit Cloud -> App Settings -> Secrets and add: GROQ_API_KEY = 'gsk_...'")
    st.stop()

# Initialize Groq Client 
client = OpenAI(
    api_key=GROQ_TOKEN,
    base_url="https://api.groq.com/openai/v1"
)

# Using Qwen on Groq's Free Tier
REPO_ID = "qwen/qwen3.8-27b"

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_recipe(ingredients, spiciness_level, dietary_goals):
    goals_str = ", ".join(dietary_goals) if dietary_goals else "None"
    
    system_prompt = f"""
    You are NutriChef AI.
    1. Create a recipe using ONLY the selected ingredients.
    2. Spiciness Level: {spiciness_level}.
    3. DIETARY GOALS: {goals_str}.
    4. START with the Recipe Name as a # Header.
    5. Create a Markdown Table for estimated nutrition.
    """
    
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"Ingredients: {ingredients_str}. Goals: {goals_str}. Spiciness: {spiciness_level}."

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=REPO_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == 2: return f"⚠️ Error: {e}"
            time.sleep(2)

# ---------------------------------------------------------
# 3. STREAMLIT UI (Web Interface)
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        st.image("icon.png", width=100)
    except:
        st.warning("⚠️ Upload icon.png to GitHub")

with col_title:
    st.title("NutriChef AI")
    st.markdown("Your Personal AI Kitchen Assistant")

# --- 🎯 CONTROLS SECTION ---
col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    spiciness = st.select_slider(
        "🌶️ Spiciness Level",
        options=["Mild", "Medium", "Spicy", "Fire"]
    )

with col_opt2:
    dietary_goals = st.multiselect(
        "🎯 Dietary Goals",
        options=["High Protein", "Low Calorie", "Diabetic-Friendly", "Kid-Friendly", "Keto"],
        default=[]
    )

st.markdown("---")
st.markdown("##### 🛒 Select Ingredients")

fridge_inventory = [
    "Eggs", "Bread", "Milk",                    
    "Rice", "Lentils (Dal)", "Wheat Flour",     
    "Potatoes", "Onions", "Tomatoes",           
    "Spinach", "Green Peas", "Carrots",         
    "Chicken", "Yogurt (Curd)", "Paneer/Cheese" 
]

col1, col2, col3 = st.columns(3)
selected_items = []

for index, item in enumerate(fridge_inventory):
    if index % 3 == 0:
        with col1:
            if st.checkbox(item): selected_items.append(item)
    elif index % 3 == 1:
        with col2:
            if st.checkbox(item): selected_items.append(item)
    else:
        with col3:
            if st.checkbox(item): selected_items.append(item)

st.markdown("---")

# ---------------------------------------------------------
# 4. GENERATION LOGIC & HISTORY
# ---------------------------------------------------------
if st.button("Generate Recipe 🥘"):
    if len(selected_items) > 0:
        status_msg = f'Cooking a {spiciness} meal'
        if dietary_goals: status_msg += f' that is {", ".join(dietary_goals)}'
        
        with st.spinner(f'{status_msg}...'):
            recipe_result = get_recipe(selected_items, spiciness, dietary_goals)
            
            # Save to history (inserts at the beginning so newest is on top)
            if not recipe_result.startswith("⚠️ Error"):
                st.session_state.recipe_history.insert(0, recipe_result)
    else:
        st.warning("⚠️ Please select at least one ingredient.")

# --- 📜 RECIPE HISTORY DISPLAY ---
if st.session_state.recipe_history:
    st.markdown("### 📜 Your Recipe History")
    
    for i, recipe in enumerate(st.session_state.recipe_history):
        # Expanded=True only for the most recent recipe
        with st.expander(f"Recipe #{len(st.session_state.recipe_history) - i}", expanded=(i == 0)):
            st.markdown(recipe)
            st.download_button(
                label=f"📥 Download Recipe #{len(st.session_state.recipe_history) - i}",
                data=recipe,
                file_name=f"NutriChef_Recipe_{len(st.session_state.recipe_history) - i}.txt",
                mime="text/plain",
                key=f"download_{i}" # Unique key required for dynamic buttons
            )
