import streamlit as st
import random
import json
import requests
from streamlit_extras.let_it_rain import rain
from ollama import chat

def random_emoji():
    emojis = ['🥯', '🥐', '🥘', '🍣', '🌯', '🥑', '🍖', '🍯', '🥗', '🔪']
    return random.choice(emojis)

def success():
    rain(
        emoji=random_emoji(),
        font_size=54,
        falling_speed=5,
        animation_length="5s",
    )

def generate_recipe(jpeg, name, link):
    st.image(jpeg)
    st.write(name)
    st.markdown(f'<a href={link} target="_blank" style="color:gray; text-decoration:none;">View more ➜</a></p>',
    unsafe_allow_html=True)

def my_chat(model, messagi):
    if model == "llama3.2":
        url = "http://localhost:11434/v1/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "temperature": 0.0,
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": messagi}
            ],
            "stream": True
        }
        response = requests.post(url, headers=headers, json=data, stream=True)
        response.raise_for_status()

        for line in response.iter_lines():
            line = line.decode("utf-8")

            if line.startswith("data: ") and not line.endswith("[DONE]"):
                data = json.loads(line[len("data: "):])
                yield data["choices"][0]["delta"].get("content", "")

    if model == "mistral":
        messages = [
        {
            'role': 'user',
            'content': messagi,
        },
    ] 
        
        for part in chat(model, messages=messages, stream=True, options={"temperature":0.0}):
            yield part['message']['content']
        
#Titel
colo, colu = st.columns ([4,1])

with colo:
    st.title("Kochbuch")
# with colu:
    # st.image("logo3.jpg")
st.caption("Das hier ist dein ganz Persönlicher Rezeptgenerator. Hier kannst du dir ganz nach Wunsch ein Rezept mit Zutatenliste und Anleitung zusammenstellen lassen.")

st.sidebar.title("Persönliche Anpassung")
mahlzeit = st.sidebar.selectbox("Mahlzeit: ", ['Frühstück', 'Mittagessen', 'Abendessen', 'Dessert', 'Sonstiges'])
personen = st.sidebar.slider("Personenzahl:", 1, 8)
sprache = st.sidebar.selectbox("Sprache: ", ['Englisch', 'Deutsch', 'Französisch'])
model = st.sidebar.selectbox("Sprachmodell: ", ['mistral', 'llama3.2', 'sonstiges'])

#Textinputfeld
kategorien = st.multiselect("Kategorien: ", ['Ausgewogen', 'Low-Carb', 'Proteinreich', 'Vegan', 'Vegetarisch'])
input = st.text_area("Hier kannst du zusätzliche Wünsche für dein Rezept hinzufügen, wie etwas Lebensmittel, die du gerne einbringen und verwerten würdest:", "Außerdem ist mir für mein Rezept wichtig, dass...")

defined_text = f"Bitte erstelle mir ein Rezept mit einer Zutatenliste und einer Anleitung. Gebe dem Rezept außerdem einen Namen, der das Endergebnis möglichst gut anhand der Zutaten berschreibt. Das Rezept soll ein {mahlzeit} für {personen} Personen sein. Zudem soll es {kategorien} sein. Schreibe das Rezept einheitlich auf {sprache}. "

text = defined_text + input

recipe_container = st.empty()

#Button
if(st.button("Enter")):
    
    englischtext = ""
    prompt = f"""Please translate the following text to englisch word for word without any additional text. Don't give me a recipe yet.
    Use these examples for how the output should look after an input:
    
    Example 1: 
    Input: "Bitte erstelle mir ein Rezept mit einer Zutatenliste und einer Anleitung. Gebe dem Rezept außerdem einen Namen, der das Endergebnis möglichst gut anhand der Zutaten berschreibt. Das Rezept soll ein Abendessen für 4 Personen sein. Zudem soll es ['Low-Carb', 'Ausgewogen'] sein. Schreibe das Rezept einheitlich auf Englisch. Außerdem ist mir für mein Rezept wichtig, dass Möhren und Zucchinis verwendet werden. Ich besitze keinen Ofen."
    Output: Please create a breakfast recipe for 4 people with a name that accurately describes the end result based on the ingredients. This dish should be low-carb and balanced. Give me a list of the ingredients and instructions which should be written in English. Additionally, carrots and zucchinis should be used in this recipe. I do not own an oven.

    Example 2:
    Input: "Bitte erstelle mir ein Rezept mit einer Zutatenliste und einer Anleitung. Gebe dem Rezept außerdem einen Namen, der das Endergebnis möglichst gut anhand der Zutaten berschreibt. Das Rezept soll ein Abendessen für 4 Personen sein. Zudem soll es ['Proteinreich'] sein. Schreibe das Rezept einheitlich auf Englisch. Außerdem ist mir für mein Rezept wichtig, dass es italienisch inspiriert ist. Ich möchte gerne Nudeln als Kohlenhydratquelle verwenden."
    Output: Please create an evening meal recipe for 4 people with a name that accurately describes the end result based on the ingredients. This dish should be high in protein. Give me a list of the ingredients and instructions which should be written in English. Additionally, pasta (noodles) should be used as a source of carbohydrates. Furthermore, the recipe should be inspired by Italian cuisine.

    Example 3:
    Input: "Bitte erstelle mir ein Rezept mit einer Zutatenliste und einer Anleitung. Gebe dem Rezept außerdem einen Namen, der das Endergebnis möglichst gut anhand der Zutaten berschreibt. Das Rezept soll ein Dessert für 4 Personen sein. Zudem soll es ['Low-Carb'] sein. Schreibe das Rezept einheitlich auf Englisch. Außerdem ist mir für mein Rezept wichtig, dass ich allergisch gegen Mandeln bin. Außerdem würde ich gerne etwas mit Schokolade machen."
    Output: Please create a dessert recipe for 8 people with a name that accurately describes the end result based on the ingredients. This dish should be low-carb. Give me a list of the ingredients and instructions which should be written in English. Additionally, I am allergic to almonds. Furthermore, I would like to make something with chocolate.

    Input: "{text}"
    """

    englischtext = my_chat(model, prompt)
    tostring = "".join(englischtext)
    recipe_prompt = f"""I want you to write me a recipe using a prompt with guidelines that I can use in a cookbook. Use these following examples for how the output should look after an input.

    Example 1:
    Input: "Please create a dessert recipe for 8 people with a name that accurately describes the end result based on the ingredients. This dish should be low-carb. Give me a list of the ingredients and instructions which should be written in English. Additionally, I am allergic to almonds. Furthermore, I would like to make something with chocolate."
    Output: 
    
    Chocolate Avocado Mousse

    Ingredients (Serves 8):
    - 4 ripe avocados
    - 1/2 cup unsweetened cocoa powder
    - 1/2 cup erythritol or your preferred low-carb sweetener
    - 1/2 cup unsweetened coconut milk
    - 1 teaspoon vanilla extract
    - A pinch of salt
    - Dark chocolate shavings (for garnish, optional)
    - Fresh berries (for garnish, optional)
    
    Instructions:
    1. Cut the avocados in half, remove the pits, and scoop the flesh into a food processor. Add the unsweetened cocoa powder, erythritol, coconut milk, vanilla extract, and a pinch of salt to the food processor.
    2. Blend until the mixture is smooth and creamy, scraping down the sides as needed. Taste the mousse and adjust the sweetness if desired.
    3. Spoon the mousse into individual serving dishes or a large bowl.
    4. Chill in the refrigerator for at least 30 minutes to firm up.
    5. Before serving, garnish with dark chocolate shavings and fresh berries if desired.
    
    Enjoy your rich and creamy Chocolate Avocado Mousse!

    Example 2:
    Input: "Please create an evening meal recipe for 4 people with a name that accurately describes the end result based on the ingredients. This dish should be high in protein. Give me a list of the ingredients and instructions which should be written in English. Additionally, pasta (noodles) should be used as a source of carbohydrates. Furthermore, the recipe should be inspired by Italian cuisine."
    Output:

    High-Protein Italian Chicken Pasta Bake

    Ingredients (Serves 4):
    - 300g whole wheat pasta (e.g., penne or fusilli)
    - 500g boneless, skinless chicken breast, diced
    - 2 tablespoons olive oil
    - 2 cloves garlic, minced
    - 1 medium onion, chopped
    - 1 red bell pepper, diced
    - 1 can (400g) crushed tomatoes
    - 1 teaspoon dried oregano
    - 1 teaspoon dried basil
    - Salt and pepper to taste
    - 150g low-fat mozzarella cheese, shredded
    - 50g grated Parmesan cheese
    - Fresh basil leaves for garnish (optional)
    
    Instructions:
    1. Preheat your oven to 200°C (400°F).
    2. Bring a large pot of salted water to a boil. Add the whole wheat pasta and cook according to package instructions until al dente. Drain and set aside.
    3. In a large skillet, heat the olive oil over medium heat. Add the diced chicken and season with salt and pepper. Cook for about 5-7 minutes, or until the chicken is browned and cooked through. Remove the chicken from the skillet and set aside.
    4. In the same skillet, add the chopped onion, minced garlic, and diced red bell pepper. Sauté for about 5 minutes, until the vegetables are softened.
    5. Add the crushed tomatoes, oregano, and basil to the skillet. Stir to combine and bring to a simmer. Add the cooked chicken and pasta to the skillet, mixing everything together.
    6. Transfer the chicken and pasta mixture to a large baking dish. Spread it out evenly.
    7. Sprinkle the shredded mozzarella and grated Parmesan cheese evenly over the top.
    8. Bake in the preheated oven for 20-25 minutes, or until the cheese is melted and bubbly.
    9. Remove from the oven and let it cool slightly. Garnish with fresh basil leaves if desired. Serve warm.

    Enjoy your High-Protein Italian Chicken Pasta Bake! This dish is perfect for a fulfilling evening meal packed with protein and delicious Italian flavors.

    Example 3:
    Input: "Please create a breakfast recipe for 4 people with a name that accurately describes the end result based on the ingredients. This dish should be vegetarian balanced. Give me a list of the ingredients and instructions which should be written in English. Additionally, oats should be used in this recipe. I do not own an oven. Please also add nutrional information per serving."
    Output:
    
    Creamy Oatmeal with Fresh Fruits and Nuts

    Ingredients (Serves 4):
    - 1 cup rolled oats
    - 4 cups water or plant-based milk (such as almond milk or soy milk)
    - 2 tablespoons maple syrup or honey (optional)
    - 1 teaspoon vanilla extract
    - 1 teaspoon cinnamon
    - 1 cup mixed fresh fruits (such as berries, bananas, or apples)
    - 1/2 cup chopped nuts (such as walnuts, almonds, or pecans)
    - 1/4 cup yogurt (optional for serving)
    - Pinch of salt
    
    Instructions
    1. In a large saucepan, combine the rolled oats, water (or plant-based milk), and a pinch of salt. Bring to a boil over medium heat.
    Once boiling, reduce the heat to low and simmer for about 5-10 minutes, stirring occasionally, until the oats are soft and have absorbed most of the liquid.
    2. Stir in the maple syrup (or honey), vanilla extract, and cinnamon. Cook for an additional 1-2 minutes until well combined and creamy.
    3. While the oats are cooking, chop the mixed fresh fruits and nuts.
    4. Divide the creamy oatmeal among four bowls. Top each bowl with fresh fruits, chopped nuts, and a dollop of yogurt if desired.
    5. Serve warm and enjoy your nutritious breakfast!
    
    Nutritional Information (per serving):
    Calories: 290
    Protein: 9g
    Fat: 10g
    Carbohydrates: 42g
    
    This recipe provides a balanced meal with healthy fats, fiber, and protein, making it a great start to your day! Enjoy your creamy oatmeal!

    This is the prompt you should use: "{tostring}"
    """

    recipe = ""

    for part in my_chat(model, recipe_prompt):
        recipe += part
        if sprache == "Englisch":
            recipe_container.markdown(
            f"""
            <div style="background-color: #FFDDC1; padding: 10px; border-radius: 5px;">
                <h3 style="color: black;">Dein Rezept</h3>
                <p>{recipe}</p>
            </div>
            """,
            unsafe_allow_html=True)
        else:
            tostring2 = "".join(recipe)
            translate_prompt = f"""Please translate the following text to {sprache}.
            """
            translate_recipe = ""
            for d in my_chat(model, translate_prompt):
                translate_recipe += d
                recipe_container.markdown(
                f"""
                <div style="background-color: #FFDDC1; padding: 10px; border-radius: 5px;">
                    <h3 style="color: black;">Dein Rezept</h3>
                    <p>{translate_recipe}</p>
                </div>
                """,
                unsafe_allow_html=True)
    success()
    if(st.download_button(label="Speichern", data = recipe, file_name="mein_rezept.txt")):
        success()


st.header("Rezeptbuch")
st.write("Staples")
st.markdown(
    "<hr style='border: 2.5px solid #800000;'>",
    unsafe_allow_html=True
)

col1, cola, col2, colb, col3, colc, col4 = st.columns([3, 1, 3, 1, 3, 1, 3])

with col1:
    generate_recipe("hackpfanne.jpg","Hackpfanne", "https://www.chefkoch.de/rezepte/")

with col2:
    generate_recipe("kürbissuppe.jpg", "Kürbissuppe", "https://www.chefkoch.de/rezepte/")

with col3:
    generate_recipe("Lammeintopf.jpg", "Lammeintopf mit weißen Bohnen", "https://www.chefkoch.de/rezepte/")

with col4:
    generate_recipe("schokokuchen.jpg", "Schokokuchen", "https://www.chefkoch.de/rezepte/")


st.link_button("View more", 'https://www.chefkoch.de/rezepte/', help=None, type="secondary", disabled=False, use_container_width=False)
