import streamlit as st
from huggingface_hub import InferenceClient
import time

# ---------------------------------------------------------
# 1. CONFIGURATION & AUTHENTICATION
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="🥗")

# 🔴 STEP 1: DEFINE THE TOKEN
# This logic handles both Cloud (Secrets) and Local (Hardcoded) modes
if "HF_TOKEN" in st.secrets:
    # Use the secret key if running on Streamlit Cloud
    hf_token = st.secrets["HF_TOKEN"]
else:
    # Use this backup key if running locally on your laptop
    # REPLACE THIS WITH YOUR ACTUAL TOKEN for local testing
    hf_token = "hf_..." 

# 🔴 STEP 2: INITIALIZE THE CLIENT (This was missing!)
# This creates the connection to the AI
if hf_token.startswith("hf_"):
    client = InferenceClient(token=hf_token)
else:
    # If the token is missing/invalid, stop the app nicely
    st.error("⚠️ Hugging Face Token not found.")
    st.info("If running locally: Paste your token in line 18 of app.py.")
    st.info("If running on Cloud: Add HF_TOKEN to Streamlit Secrets.")
    st.stop()

# Select the Model
REPO_ID = "Qwen/Qwen2.5-7B-Instruct"

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_recipe(ingredients):
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
            # We use the 'client' variable here. It must be defined above!
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
                        f"**Troubleshooting:** Check your HF_TOKEN.")
            time.sleep(2)

# ---------------------------------------------------------
# 3. STREAMLIT UI
# ---------------------------------------------------------
st.title("🥗 NutriChef AI")
st.markdown("Select your ingredients, and I'll generate a recipe card for you.")

# INVENTORY
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
            
            with st.container(border=True):
                st.markdown(recipe_result)
            
            st.download_button(
                label="📥 Download Recipe",
                data=recipe_result,
                file_name="NutriChef_Recipe.md",
                mime="text/markdown"
            )
    else:
        st.warning("⚠️ Please select at least one ingredient.")
