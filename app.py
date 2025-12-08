import streamlit as st
from huggingface_hub import InferenceClient
import time

# ---------------------------------------------------------
# 1. WEB CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="🥗")

# This looks for the token in the secure cloud settings
# If it's missing, it stops the app to protect you
try:
    HF_TOKEN = st.secrets["HF_TOKEN"]
except:
    st.error("⚠️ Token not found in Secrets!")
    st.info("Go to Streamlit Cloud -> App Settings -> Secrets and add your HF_TOKEN.")
    st.stop()

client = InferenceClient(token=HF_TOKEN)
REPO_ID = "Qwen/Qwen2.5-7B-Instruct"

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_recipe(ingredients):
    system_prompt = """
    You are NutriChef AI, a resourceful home cook.
    1. Create a recipe using ONLY the selected ingredients.
    2. Assume basic pantry staples (Salt, Oil, Water) exist.
    3. START the response with the Recipe Name as a # Header.
    4. Create a Markdown Table for nutrition.
    """
    
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"I have these ingredients: {ingredients_str}. Make me a simple meal."

    for attempt in range(3):
        try:
            response = client.chat_completion(
                model=REPO_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == 2: return f"⚠️ Error: {e}"
            time.sleep(2)

# ---------------------------------------------------------
# 3. WEB UI
# ---------------------------------------------------------
st.title("🥗 NutriChef AI")
st.markdown("Select your ingredients to generate a recipe!")

fridge_inventory = [
    "Eggs", "Bread", "Milk", "Rice", "Lentils (Dal)", "Wheat Flour",     
    "Potatoes", "Onions", "Tomatoes", "Spinach", "Green Peas", "Carrots",         
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

if st.button("Generate Recipe 🥘"):
    if len(selected_items) > 0:
        with st.spinner('Chef is thinking...'):
            recipe_result = get_recipe(selected_items)
            st.markdown("### 🍽️ Your Recipe Card")
            with st.container(border=True):
                st.markdown(recipe_result)
            st.download_button("📥 Download (.txt)", recipe_result, "Recipe.txt", "text/plain")
    else:
        st.warning("⚠️ Select at least one item.")
