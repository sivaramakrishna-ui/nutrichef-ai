import streamlit as st
from huggingface_hub import InferenceClient
import time

# ---------------------------------------------------------
# 1. CONFIGURATION & AUTHENTICATION
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="🥗")

# Hybrid Auth: Checks Cloud Secrets first, then local code
if "HF_TOKEN" in st.secrets:
    hf_token = st.secrets["HF_TOKEN"]
else:
    # 🔴 PASTE YOUR TOKEN HERE FOR LOCAL TESTING
    hf_token = "hf_..." 

if hf_token.startswith("hf_"):
    client = InferenceClient(token=hf_token)
else:
    st.error("⚠️ Hugging Face Token not found.")
    st.stop()

REPO_ID = "Qwen/Qwen2.5-7B-Instruct"

# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_recipe(ingredients):
    # --- UPDATED PROMPT: STRICT MODE ---
    system_prompt = """
    You are a resourceful home cook.
    1. Create a recipe using ONLY the selected ingredients.
    2. You may assume the user has basic pantry staples (Salt, Pepper, Oil, Water, Sugar) - but NOTHING else.
    3. Do NOT add extra vegetables, meats, or spices that are not in the list.
    4. START the response with the Recipe Name as a # Header.
    5. Create a Markdown Table for nutrition.
    """
    
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"I have these ingredients: {ingredients_str}. Make me a simple meal using ONLY these."

    for attempt in range(3):
        try:
            response = client.chat_completion(
                model=REPO_ID,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.5 # Lower temperature = Less creativity/randomness
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
st.caption("Strict Mode: I will only cook with what you have.")

st.markdown("Select your ingredients:")

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
