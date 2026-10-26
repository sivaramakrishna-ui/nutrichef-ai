import streamlit as st
from openai import OpenAI
import time

# ---------------------------------------------------------
# 1. WEB CONFIGURATION & STATE
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="icon.png", layout="wide")

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
# 3. SIDEBAR UI (Settings)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Chef's Settings")
    spiciness = st.select_slider(
        "🌶️ Spiciness Level",
        options=["Mild", "Medium", "Spicy", "Fire"]
    )
    
    dietary_goals = st.multiselect(
        "🎯 Dietary Goals",
        options=["High Protein", "Low Calorie", "Diabetic-Friendly", "Kid-Friendly", "Keto"],
        default=[]
    )
    st.markdown("---")
    st.info("Tip: Select 3-4 ingredients for the most creative recipes!")

# ---------------------------------------------------------
# 4. MAIN UI (Title & Ingredients)
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 6])

with col_logo:
    try:
        st.image("icon.png", width=80)
    except:
        pass # Silently pass if icon isn't uploaded yet

with col_title:
    st.title("NutriChef AI")
    st.markdown("Your Personal AI Kitchen Assistant")

st.markdown("---")

fridge_inventory = [
    "Eggs", "Bread", "Milk",                    
    "Rice", "Lentils (Dal)", "Wheat Flour",     
    "Potatoes", "Onions", "Tomatoes",           
    "Spinach", "Green Peas", "Carrots",         
    "Chicken", "Yogurt (Curd)", "Paneer/Cheese",
    "Garlic", "Ginger", "Olive Oil"
]

# Modern Streamlit Pills for clean ingredient selection
selected_items = st.pills(
    "🛒 Select Available Ingredients (Click to toggle)", 
    options=fridge_inventory, 
    selection_mode="multi"
)

st.markdown("---")

# ---------------------------------------------------------
# 5. GENERATION LOGIC & HISTORY
# ---------------------------------------------------------
# Center the generate button
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    generate_btn = st.button("Generate Recipe 🥘", use_container_width=True)

if generate_btn:
    if selected_items and len(selected_items) > 0:
        status_msg = f'Cooking a {spiciness} meal'
        if dietary_goals: status_msg += f' that is {", ".join(dietary_goals)}'
        
        with st.spinner(f'{status_msg}...'):
            recipe_result = get_recipe(selected_items, spiciness, dietary_goals)
            
            # Save to history if successful
            if not recipe_result.startswith("⚠️ Error"):
                st.session_state.recipe_history.insert(0, recipe_result)
                st.toast("Bon Appétit! Your recipe is ready. 🍳")
                st.balloons() # Triggers the balloon animation
            else:
                st.error(recipe_result)
    else:
        st.warning("⚠️ Please select at least one ingredient.")

# --- 📜 RECIPE HISTORY DISPLAY ---
if st.session_state.recipe_history:
    st.markdown("### 📜 Your Menu")
    
    for i, recipe in enumerate(st.session_state.recipe_history):
        # Only expand the newest recipe automatically
        with st.expander(f"Recipe #{len(st.session_state.recipe_history) - i}", expanded=(i == 0)):
            st.markdown(recipe)
            
            # Download button for each recipe
            st.download_button(
                label=f"📥 Download Recipe #{len(st.session_state.recipe_history) - i}",
                data=recipe,
                file_name=f"NutriChef_Recipe_{len(st.session_state.recipe_history) - i}.txt",
                mime="text/plain",
                key=f"download_{i}" 
            )
