import streamlit as st
from openai import OpenAI
import time

# ---------------------------------------------------------
# 1. MOBILE-FIRST CONFIGURATION & CSS STYLING
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef", page_icon="icon.png", layout="centered")

# Inject Custom CSS for a vibrant, mobile-app feel
st.markdown("""
<style>
    /* Vibrant Gradient Title */
    h1 {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 3rem !important;
        font-weight: 800;
        margin-bottom: 0;
    }
    
    /* Massive, Colorful Gradient Main Button */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        border-radius: 30px;
        border: none;
        font-weight: bold;
        font-size: 20px;
        padding: 12px 24px;
        box-shadow: 0px 8px 15px rgba(255, 107, 107, 0.4);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0px 12px 20px rgba(255, 107, 107, 0.6);
    }
    
    /* Soften container backgrounds */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 20px;
        border: 2px solid #FFE4E1;
        background-color: #FFF9F9;
        padding: 10px;
    }
    
    /* Center text alignments */
    .subtitle { text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "recipe_history" not in st.session_state:
    st.session_state.recipe_history = []

# SECURE AUTHENTICATION
try:
    GROQ_TOKEN = st.secrets["GROQ_API_KEY"]
except:
    st.error("⚠️ Token not found in secrets!")
    st.stop()

client = OpenAI(api_key=GROQ_TOKEN, base_url="https://api.groq.com/openai/v1")
REPO_ID = "qwen/qwen3.8-27b"

# ---------------------------------------------------------
# 2. AI GENERATION FUNCTION
# ---------------------------------------------------------
def get_recipe(ingredients, spiciness_level, dietary_goals, max_time):
    goals_str = ", ".join(dietary_goals) if dietary_goals else "None"
    
    system_prompt = f"""
    You are NutriChef AI.
    1. Create a recipe using ONLY the selected ingredients.
    2. Spiciness Level: {spiciness_level}.
    3. DIETARY GOALS: {goals_str}.
    4. TIME LIMIT: The total prep and cook time must be {max_time} or less.
    5. START with the Recipe Name as a # Header.
    6. Include the estimated Prep Time and Cook Time right under the title.
    7. Create a Markdown Table for estimated nutrition.
    """
    user_prompt = f"Ingredients: {','.join(ingredients)}. Goals: {goals_str}. Spiciness: {spiciness_level}. Max Time: {max_time}."

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
# 3. MOBILE UI LAYOUT
# ---------------------------------------------------------
# App Header
st.markdown("<h1>NutriChef AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Your Smart Kitchen Assistant</p>", unsafe_allow_html=True)

# Center the icon
_, icon_col, _ = st.columns([2, 1, 2])
with icon_col:
    try:
        st.image("icon.png", use_container_width=True)
    except:
        pass 

# 📱 Settings 
with st.container(border=True):
    st.markdown("### 🎛️ Recipe Settings")
    
    spiciness = st.select_slider(
        "🌶️ Spiciness",
        options=["Mild", "Medium", "Spicy", "Fire"],
        value="Medium"
    )
    
    # ⬇️ NEW: Expanded Dietary Goals (10 Options) ⬇️
    dietary_goals = st.multiselect(
        "🎯 Dietary Goals",
        options=[
            "High Protein 💪", 
            "Low Calorie 📉", 
            "Low Carb 🚫🍞", 
            "Keto 🥑", 
            "Vegan 🌱", 
            "Vegetarian 🥗", 
            "Gluten-Free 🌾", 
            "Dairy-Free 🥛", 
            "Diabetic-Friendly 🩸", 
            "Heart-Healthy ❤️"
        ],
        placeholder="Tap to select..."
    )

    max_time = st.selectbox(
        "⏱️ Max Cooking Time",
        options=["15 mins ⚡", "30 mins ⏳", "45 mins 🕒", "1 hour 🍳", "Any Time 🕰️"],
        index=1 
    )

st.write("") # Spacer

# 📱 Ingredients 
with st.container(border=True):
    st.markdown("### 🛒 Pantry Ingredients")
    
    fridge_inventory = [
        "Eggs 🥚", "Bread 🍞", "Milk 🥛", "Rice 🍚", "Pasta 🍝",
        "Lentils 🍲", "Beans 🫘", "Potatoes 🥔", "Onions 🧅", "Tomatoes 🍅", 
        "Spinach 🥬", "Carrots 🥕", "Bell Peppers 🫑", "Mushrooms 🍄",
        "Chicken 🍗", "Beef 🥩", "Cheese 🧀", "Butter 🧈", "Garlic 🧄"
    ]
    
    selected_items = st.pills(
        "Tap main ingredients:", 
        options=fridge_inventory, 
        selection_mode="multi",
        default=[]
    )
    
    st.markdown("---")
    
    extra_options = [
        "Honey 🍯", "Lemon 🍋", "Lime 🍈", "Vinegar 🍾", 
        "Soy Sauce 🥢", "Cinnamon 🤎", "Vanilla Extract 🌼", 
        "Sugar 🧂", "Salt & Pepper 🧂", "Chili Flakes 🌶️",
        "Mayonnaise 🥚", "Ketchup 🍅", "Mustard 🌭"
    ]
    
    extra_ingredients = st.multiselect(
        "➕ Add Flavor & Extras",
        options=extra_options,
        placeholder="Tap to view dropdown menu..."
    )

st.write("") # Spacer

# ---------------------------------------------------------
# 4. ACTION BUTTON & RESULTS
# ---------------------------------------------------------
if st.button("Cook Now! ✨"):
    
    final_ingredients = list(selected_items) if selected_items else []
    if extra_ingredients:
        final_ingredients.extend(extra_ingredients)
        
    if len(final_ingredients) > 0:
        with st.spinner(f"🔥 Cooking a {max_time.split()[0]} minute recipe..."):
            recipe_result = get_recipe(final_ingredients, spiciness, dietary_goals, max_time)
            
            if not recipe_result.startswith("⚠️ Error"):
                st.session_state.recipe_history.insert(0, recipe_result)
                st.toast("Bon Appétit! 🍽️")
                st.balloons()
            else:
                st.error(recipe_result)
    else:
        st.warning("⚠️ Tap at least one ingredient first!")

# 📜 History displayed as mobile "Cards"
if st.session_state.recipe_history:
    st.markdown("---")
    st.markdown("### 🍽️ Your Menu")
    
    for i, recipe in enumerate(st.session_state.recipe_history):
        with st.container(border=True):
            with st.expander(f"✨ Recipe #{len(st.session_state.recipe_history) - i}", expanded=(i == 0)):
                st.markdown(recipe)
                st.download_button(
                    label="💾 Save Recipe",
                    data=recipe,
                    file_name=f"NutriChef_Recipe_{i}.txt",
                    mime="text/plain",
                    key=f"dl_{i}",
                    use_container_width=True
                )
