import streamlit as st
from huggingface_hub import InferenceClient
import time

# ---------------------------------------------------------
# 1. WEB CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="🥗")

# SECURE AUTHENTICATION
# This looks for the token in Streamlit Cloud Settings
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except:
    st.error("⚠️ Token not found!")
    st.info("Go to Streamlit Cloud -> App Settings -> Secrets and add: HF_TOKEN = 'hf_...'")
    st.stop()

# Initialize Client
client = InferenceClient(token=HF_TOKEN)
REPO_ID = "Qwen/Qwen2.5-7B-Instruct"

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_recipe(ingredients, spiciness_level):
    system_prompt = f"""
    You are NutriChef AI, a resourceful home cook.
    1. Create a recipe using ONLY the selected ingredients.
    2. Spiciness Level: {spiciness_level}. Adjust spices/chilies accordingly.
    3. You may assume the user has basic pantry staples (Salt, Oil, Water).
    4. START the response with the Recipe Name as a # Header.
    5. Create a Markdown Table for estimated nutrition.
    """
    
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"I have these ingredients: {ingredients_str}. Make me a {spiciness_level} meal."

    for attempt in range(3):
        try:
            response = client.chat_completion(
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
# 3. WEB UI
# ---------------------------------------------------------
st.title("🥗 NutriChef AI")
st.markdown("Select your ingredients & spice level:")

# 🌶️ SPICINESS SLIDER
spiciness = st.select_slider(
    "How spicy do you want it?",
    options=["Mild", "Medium", "Spicy", "Fire 🌶️"]
)

st.markdown("---")

# SIMPLE INVENTORY
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
# 4. GENERATION LOGIC
# ---------------------------------------------------------
if st.button("Generate Recipe 🥘"):
    if len(selected_items) > 0:
        with st.spinner(f'Chef is cooking something {spiciness}...'):
            recipe_result = get_recipe(selected_items, spiciness)
            
            st.markdown("### 🍽️ Your Recipe Card")
            
            with st.container(border=True):
                st.markdown(recipe_result)
            
            # Mobile Friendly Download
            st.download_button(
                label="📥 Download Recipe (.txt)",
                data=recipe_result,
                file_name="NutriChef_Recipe.txt",
                mime="text/plain"
            )
    else:
        st.warning("⚠️ Please select at least one ingredient.")
