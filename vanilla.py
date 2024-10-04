import streamlit as st
import random
import json
import requests
from streamlit_extras.let_it_rain import rain
from ollama import chat

st.set_page_config(layout="wide")
# value = "zero"

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

def generate_recipe(jpeg, name, recipe, recipe_key):
    st.image(jpeg)
    st.write(name)
    if st.button(f"View more ➜", key=recipe_key):
        st.session_state['selected_recipe'] = recipe

def generate_own_recipe(jpeg, name, link):
    st.image(jpeg)
    st.write(name)
    st.markdown(f"""
    <div style="background-color: #FFDDC1; padding: 10px; border-radius: 5px;">
    <h3 style="color: black;">Dein Rezept</h3>
    <p>{link}</p>
    </div>
    """,
    unsafe_allow_html=True)

def show_selected_recipe():
    if 'selected_recipe' in st.session_state:
        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background-color: #FFDDC1; padding: 20px; border-radius: 10px;">
            <h2 style="color: black;">Dein Rezept</h2>
            <p>{st.session_state['selected_recipe']}</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("\n")
        if st.button("Schließen"):
            del st.session_state['selected_recipe']

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

    if model == "mistral" or model == "mistral:7b-instruct-q3_K_M":
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
model = st.sidebar.selectbox("Sprachmodell: ", ['mistral', 'llama3.2', 'mistral:7b-instruct-q3_K_M'])

#Textinputfeld
kategorien = st.multiselect("Kategorien: ", ['Ausgewogen', 'Low-Carb', 'Proteinreich', 'Vegan', 'Vegetarisch'])
input = st.text_area("Hier kannst du zusätzliche Wünsche für dein Rezept hinzufügen, wie etwas Lebensmittel, die du gerne einbringen und verwerten würdest:", "Außerdem ist mir für mein Rezept wichtig, dass...")

defined_text = f"Bitte erstelle mir ein Rezept mit einer Zutatenliste und einer Anleitung. Gebe dem Rezept außerdem einen Namen, der das Endergebnis möglichst gut anhand der Zutaten berschreibt. Das Rezept soll ein {mahlzeit} für {personen} Personen sein. Zudem soll es {kategorien} sein. Schreibe das Rezept einheitlich auf {sprache}. "

text = defined_text + input

recipe_container = st.empty()

#Button
if(st.button("Enter")):
    
    englischtext = ""
    prompt = f"""
        Please translate the following text to englisch word for word without any additional text. Don't give me a recipe yet.
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
    recipe_prompt = f"""
        Please create a recipe following these exact instructions:
        - The output should be only the recipe and nothing else.
        - The recipe must include a clear title, ingredients list (with quantities), and step-by-step instructions.
        - The output should not contain explanations, additional text, or information that is not part of the recipe.

        For example:

        Chocolate Avocado Mousse

        Ingredients (Serves 8):
        - 4 ripe avocados
        - 1/2 cup unsweetened cocoa powder
        - 1/2 cup erythritol
        - 1/2 cup unsweetened coconut milk
        - 1 teaspoon vanilla extract
        - A pinch of salt

        Instructions:
        1. Cut the avocados in half, remove the pits, and scoop the flesh into a food processor...
        ...
        Make sure the recipe follows this format. The recipe must be for {mahlzeit} for {personen} people, and should be {kategorien}. The recipe should be written in {sprache}.

        Input: {text}
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
    if sprache == "Deutsch":
        tostring2 = "".join(recipe)
        print(tostring2)
        translate_prompt = f"""
            Please translate the following recipe to {sprache}, keeping the structure and formatting intact. Here's an example of how the translation should look:
            Example Input (English):
            "Chocolate Avocado Mousse

            Ingredients (Serves 8):
            - 4 ripe avocados
            - 1/2 cup unsweetened cocoa powder
            - 1/2 cup erythritol
            - 1/2 cup unsweetened coconut milk
            - 1 teaspoon vanilla extract
            - A pinch of salt

            Instructions:
            1. Cut the avocados in half, remove the pits, and scoop the flesh into a food processor...
            2. Blend until smooth and creamy.
            3. Chill in the refrigerator for at least 30 minutes before serving.
            4. Garnish with berries if desired."

            Example Output ({sprache}):
            "Schokoladen-Avocado-Mousse

            Zutaten (für 8 Personen):
            - 4 reife Avocados
            - 1/2 Tasse ungesüßtes Kakaopulver
            - 1/2 Tasse Erythrit
            - 1/2 Tasse ungesüßte Kokosmilch
            - 1 Teelöffel Vanilleextrakt
            - Eine Prise Salz

            Zubereitung:
            1. Die Avocados halbieren, die Kerne entfernen und das Fruchtfleisch in einen Mixer geben...
            2. Mixen, bis die Masse glatt und cremig ist.
            3. Vor dem Servieren mindestens 30 Minuten im Kühlschrank kühlen.
            4. Nach Wunsch mit Beeren garnieren."

            Now, translate this recipe: {recipe}
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
st.markdown(
    "<hr style='border: 2.5px solid #800000;'>",
    unsafe_allow_html=True
)

col1, cola, col2, colb, col3, colc, col4 = st.columns([3, 1, 3, 1, 3, 1, 3])

with col1:
    hackpfanne = """
        Arnes Hackpfanne

        Zutaten für 4 Portionen:
        - 500 g Hackfleisch
        - 2 Zucchinis
        - 4 Möhren
        - 1 große Zwiebel
        - Knoblauch
        - 250 g Basmati Reis
        - Sojasauce, Salz, Pfeffer, Paprika, Schwarzkümmel, weitere Gewürze nach Wahl

        Anleitung:
        1. Den Reis kochen.
        2. Parallel in einer Pfanne Öl scharf erhitzen und Zwiebeln, Knoblauch und Hack dazugeben.
        3. Gemüse nach Wassergehalt hinzugeben, von weniger zu mehr.
        4. Optional Sojasauce, Gemüsebrühe oder Fleischbrühe hinzugeben.
        5. Würzen und vom Herd nehmen, bevor das Gemüse matschig wird.
        6. Genießen!"""
    generate_recipe("hackpfanne.jpg","Hackpfanne", hackpfanne, recipe_key="Hackpfanne")

with col2:
    kürbissuppe = """

        Zutaten für 4 Portionen:
        - 1 Hokkaido-Kürbis
        - 1 Zwiebel
        - 2 Knoblauchzehen
        - 500 ml Gemüsebrühe
        - 100 ml Sahne
        - Salz, Pfeffer, Muskatnuss

        Anleitung:
        1. Den Kürbis waschen, entkernen und in Würfel schneiden.
        2. Zwiebel und Knoblauch hacken und in einem großen Topf andünsten.
        3. Kürbis hinzugeben und kurz mitdünsten.
        4. Gemüsebrühe hinzugeben und alles ca. 20 Minuten köcheln lassen.
        5. Mit einem Pürierstab die Suppe cremig pürieren.
        6. Sahne hinzufügen und mit Salz, Pfeffer und Muskatnuss abschmecken.
        7. Genießen!"""
    generate_recipe("kürbissuppe.jpg", "Kürbissuppe",  kürbissuppe, recipe_key="kürbissuppe")

with col3:
    lammeintopf = """
        Lammeintopf mit weißen Bohnen

        Zutaten für 4 Portionen:
        - 600 g Lammfleisch
        - 1 Dose weiße Bohnen
        - 2 Karotten
        - 1 Zwiebel
        - 2 Knoblauchzehen
        - 500 ml Lammbrühe
        - Rosmarin, Salz, Pfeffer

        Anleitung:
        1. Das Lammfleisch in Würfel schneiden und in einem großen Topf anbraten.
        2. Zwiebel, Knoblauch und Karotten hinzugeben und mitdünsten.
        3. Die Lammbrühe hinzugeben und alles etwa 1 Stunde köcheln lassen.
        4. Die weißen Bohnen hinzufügen und weitere 10 Minuten köcheln lassen.
        5. Mit Rosmarin, Salz und Pfeffer abschmecken.
        6. Genießen!"""
    generate_recipe("Lammeintopf.jpg", "Lammeintopf", lammeintopf, recipe_key="lammeintopf")

with col4:
    schokokuchen = """
        Schokokuchen mit flüssigem Kern

        Zutaten (Für 4 Portionen):
        - 200g Zartbitterschokolade (70% Kakao)
        - 100g ungesalzene Butter, plus etwas mehr zum Einfetten
        - 2 große Eier
        - 2 große Eigelbe
        - 50g Zucker
        - 20g Mehl
        - Eine Prise Salz
        - Kakaopulver (zum Bestäuben)

        Zubereitung:
        1. Den Ofen auf 200°C vorheizen. 4 Förmchen (Ramekins) mit Butter einfetten und mit Kakaopulver bestäuben. Zur Seite stellen.
        2. Die Zartbitterschokolade und Butter in einer hitzebeständigen Schüssel über einem Wasserbad (Doppelkocher-Methode) schmelzen. Gelegentlich umrühren, bis die Masse glatt ist.
        3. In einer separaten Schüssel die Eier, Eigelbe und Zucker verquirlen, bis die Mischung blass und dickflüssig wird.
        4. Vorsichtig die geschmolzene Schokoladenmischung unter die Ei-Zucker-Mischung heben.
        5. Das Mehl und eine Prise Salz über den Teig sieben und vorsichtig unterheben, bis alles gut vermischt ist.
        6. Die Mischung gleichmäßig auf die vorbereiteten Förmchen verteilen.
        7. 10-12 Minuten backen. Die Ränder sollten fest sein, aber die Mitte weich bleiben.
        8. Aus dem Ofen nehmen und 1 Minute abkühlen lassen. Mit einem Messer vorsichtig an den Rändern entlangfahren, um die Kuchen zu lösen.
        9. Die Kuchen auf Teller stürzen und die Förmchen vorsichtig entfernen.
        10. Sofort servieren, optional mit Puderzucker bestäubt oder mit einer Kugel Vanilleeis.

        Genießen Sie Ihren köstlichen Schokokuchen mit perfekt flüssigem Kern!"""
    generate_recipe("schokokuchen.jpg", "Schokokuchen", schokokuchen, recipe_key="schokokuchen")

show_selected_recipe()

st.markdown(
    "<hr style='border: 2.5px solid #800000;'>",
    unsafe_allow_html=True
)

col5, cold, col6, cole, col7, colf, col8 = st.columns([3, 1, 3, 1, 3, 1, 3])

with col5:
    oats = """
        Overnight Oats mit Beeren

        Zutaten (für 4 Portionen):
        - 2 Tassen Haferflocken
        - 2 Tassen Mandelmilch (oder jede andere pflanzliche Milch)
        - 2 EL Chiasamen
        - 2 TL Honig oder Ahornsirup (optional)
        - 200g gemischte Beeren (z.B. Heidelbeeren, Erdbeeren, Himbeeren)
        - 2 EL gehackte Mandeln oder Nüsse nach Wahl
        - 2 TL Zimt (optional)
        
        Zubereitung:
        1. Die Haferflocken, Chiasamen, Mandelmilch und den Honig/Ahornsirup in einer großen Schüssel vermischen.
        2. Über Nacht im Kühlschrank ziehen lassen.
        3. Am nächsten Morgen mit den Beeren, gehackten Nüssen und Zimt garnieren.
        """
    generate_recipe("oats.jpg","Overnight Oats", oats, recipe_key="Overnight Oats mit Beeren")

with col6:
    avocadotoast = """
        Avocado-Toast mit pochiertem Ei

        Zutaten (für 4 Portionen):
        - 4 Scheiben Vollkornbrot
        - 2 reife Avocados
        - 4 Eier
        - Ein Spritzer Zitronensaft
        - Salz und Pfeffer
        - Chiliflocken (optional)
        
        Zubereitung:
        1. Die Avocados mit einer Gabel zerdrücken und mit Zitronensaft, Salz und Pfeffer würzen.
        2. Das Vollkornbrot toasten und die Avocado darauf verteilen.
        3. Die Eier pochieren und auf den Avocado-Toast legen.
        4. Nach Belieben mit Chiliflocken bestreuen."""
    generate_recipe("avocadotoast.jpg", "avocadotoast",  avocadotoast, recipe_key="Avocado-Toast mit pochiertem Ei")

with col7:
    bananenpfannkuchen = """
        Bananen-Pfannkuchen:

        Zutaten (für 4 Portionen):
        - 4 reife Bananen
        - 4 Eier
        - 1/2 Tasse Haferflocken
        - 2 TL Backpulver
        - 2 TL Zimt
        - Kokosöl zum Braten
        - Frische Beeren oder Joghurt zum Garnieren
        
        Zubereitung:
        1. Die Bananen in einer Schüssel zerdrücken. Eier, Haferflocken, Backpulver und Zimt hinzufügen und gut vermischen.
        2. Eine Pfanne mit etwas Kokosöl erhitzen und den Teig portionsweise hineingeben.
        3. Die Pfannkuchen auf beiden Seiten goldbraun braten.
        4. Mit Beeren oder Joghurt serviere!
        """
    generate_recipe("pfannkuchen.jpg", "Bananenpfannkuchen", bananenpfannkuchen, recipe_key="Bananen-Pfannkuchen")

with col8:
    chiapudding = """
        Chia-Pudding

        Zutaten (für 4 Portionen):
        - 8 EL Chiasamen
        - 500 ml Mandelmilch (oder jede andere pflanzliche Milch)
        - 2 TL Vanilleextrakt
        - 2 TL Honig oder Ahornsirup
        - 200g frische Früchte (z.B. Erdbeeren, Blaubeeren)
        - 2 EL gehackte Nüsse oder Mandeln

        Zubereitung:
        1. Die Chiasamen, Mandelmilch, Vanilleextrakt und Honig/Ahornsirup in einer Schüssel gut vermischen.
        2. Über Nacht im Kühlschrank quellen lassen.
        3. Mit frischen Früchten und gehackten Nüssen garnieren und genießen.
        """
    generate_recipe("chia.jpg", "Chia-Pudding", chiapudding, recipe_key="Chia-Pudding")

if st.button("View more"):
    st.markdown(
    "<hr style='border: 2.5px solid #800000;'>",
    unsafe_allow_html=True
    )
