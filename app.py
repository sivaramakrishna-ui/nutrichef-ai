import streamlit as st
from huggingface_hub import InferenceClient
import time

# ---------------------------------------------------------
# 1. WEB CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(page_title="NutriChef AI", page_icon="🥗")

# SECURE AUTHENTICATION (Cloud Secrets)
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
def get_recipe(ingredients, spiciness_level, dietary_goals):
    # Convert list of goals to string
    goals_str = ", ".join(dietary_goals) if dietary_goals else "None"

    system_prompt = f"""
    You are NutriChef AI, a smart nutritionist and chef.
    1. Create a recipe using ONLY the selected ingredients (plus salt, oil, water).
    2. Spiciness Level: {spiciness_level}.
    3. DIETARY GOALS: {goals_str}. IMPORTANT: Adjust the recipe to meet these goals 
       (e.g., if 'Diabetic-Friendly', avoid sugar/high carbs; if 'Kid-Friendly', make it mild and fun).
    4. START with the Recipe Name as a # Header.
    5. Create a Markdown Table for nutrition.
    """
    
    ingredients_str = ", ".join(ingredients)
    user_prompt = f"Ingredients: {ingredients_str}. Goals: {goals_str}. Spiciness: {spiciness_level}."

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
st.markdown("Customize your meal exactly how you want it!")

# --- 🎯 NEW: DIETARY GOALS ---
col_opt1, col_opt2 = st.columns(2)

with col_opt1:
    spiciness = st.select_slider(
        "🌶️ Spiciness Level",
        options=["Mild", "Medium", "Spicy", "Fire"]
    )

with col_opt2:
    dietary_goals = st.multiselect(
        "🎯 Dietary Goals",
        options=["High Protein", "Low Calorie", "Diabetic-Friendly", "Kid-Friendly", "Keto", "Low Carb"],
        default=[]
    )

st.markdown("---")
st.markdown("##### 🛒 Select Ingredients")

# INVENTORY LIST
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
        # Create a friendly status message
        status_msg = f'Cooking a {spiciness} meal'
        if dietary_goals:
            status_msg += f' that is {", ".join(dietary_goals)}'
        
        with st.spinner(f'{status_msg}...'):
            # Pass all inputs to the function
            recipe_result = get_recipe(selected_items, spiciness, dietary_goals)
            
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
