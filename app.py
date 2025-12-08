import streamlit as st
from huggingface_hub import InferenceClient
import time

# ---------------------------------------------------------
# 1. CONFIGURATION
# ---------------------------------------------------------
import streamlit as st

# We use st.secrets so your key stays private on the web
# You will set this up in the Streamlit Cloud dashboard later
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except:
    st.error("Secrets not found. Please set HF_TOKEN in Streamlit Cloud settings.")
    st.stop()

# ... rest of the code remains the same ...

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_recipe(ingredients):
    # Updated prompt to ensure the Title is huge (#)
    system_prompt = """
    You are NutriChef AI.
    1. Create a simple, comforting recipe using the selected ingredients.
    2. START the response with the Recipe Name formatted as a top-level Markdown Header (use #).
    3. Provide step-by-step cooking instructions.
    4. Create a Markdown Table for estimated nutrition.
    """
    
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"I have these ingredients: {ingredients_str}. Make me a simple home-cooked meal."

    for attempt in range(3):
        try:
            response = client.chat_completion(
                model=REPO_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == 2: 
                return (f"⚠️ **Error:** {e}\n\n"
                        f"**Troubleshooting:** Check your HF_TOKEN or try again later.")
            time.sleep(2)

# ---------------------------------------------------------
# 3. STREAMLIT UI
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="🏠")

st.title("🏠 NutriChef AI: Home Edition")
st.markdown("Select your ingredients, and I'll generate a recipe card for you.")

# SIMPLE HOME INVENTORY
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
# 4. GENERATION & CARD DISPLAY
# ---------------------------------------------------------
if st.button("Generate Recipe 🥘"):
    if len(selected_items) > 0:
        st.info(f"Selected: {', '.join(selected_items)}")
        
        with st.spinner('Checking the pantry...'):
            recipe_result = get_recipe(selected_items)
            
            st.markdown("### 🍽️ Your Recipe Card")
            
            # --- VISUAL CHANGE: RECIPE TILE ---
            # We use a container with a border to create the "Tile" look
            with st.container(border=True):
                # The prompt ensures the first line is a big # Header
                st.markdown(recipe_result)
            # ----------------------------------
            
            st.download_button(
                label="📥 Download Recipe",
                data=recipe_result,
                file_name="NutriChef_Recipe.md",
                mime="text/markdown"
            )
    else:
        st.warning("⚠️ Please select at least one ingredient.")
