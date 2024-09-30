import streamlit as st
import random
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

#Titel
colo, colu = st.columns ([4,1])

with colo:
    st.title("Kochbuch")
with colu:
    st.image("logo3.jpg")
st.caption("Das hier ist dein ganz Persönlicher Rezeptgenerator. Hier kannst du dir ganz nach Wunsch ein Rezept mit Zutatenliste und Anleitung zusammenstellen lassen.")

st.sidebar.title("Persönliche Anpassung")
mahlzeit = st.sidebar.selectbox("Mahlzeit: ", ['Frühstück', 'Mittagessen', 'Abendessen', 'Kuchen und Süßes', 'Sonstiges'])
personen = st.sidebar.slider("Personenzahl:", 1, 8)
sprache = st.sidebar.selectbox("Sprache: ", ['Englisch', 'Deutsch', 'Französisch'])

#Textinputfeld
kategorien = st.multiselect("Kategorien: ", ['Ausgewogen', 'Low-Carb', 'Proteinreich', 'Vegan', 'Vegetarisch'])
input = st.text_area("Hier kannst du zusätzliche Wünsche für dein Rezept hinzufügen, wie etwas Lebensmittel, die du gerne einbringen und verwerten würdest:", "Außerdem ist mir für mein Rezept wichtig, dass...")

defined_text = f"Please create a recipe with a list of ingredients and instructions. Also, give the recipe a name that describes as precisely as possible what it is. The recipe should be a {mahlzeit} for {personen} people. Additionally, it should be {kategorien}. Write the recipe uniformly in {sprache}."



text = defined_text + input

messages = [
  {
    'role': 'user',
    'content': text,
  },
]

recipe_container = st.empty()

#Button
if(st.button("Enter")):
    recipe = ""

    for part in chat('mistral', messages=messages, stream=True):
        recipe += part['message']['content']
        recipe_container.markdown(
    f"""
    <div style="background-color: #FFDDC1; padding: 10px; border-radius: 5px;">
        <h3 style="color: black;">Dein Rezept</h3>
        <p>{recipe}</p>
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
    st.image("hackpfanne.jpg")
    st.write("Hackpfanne")
    st.markdown('<a href="https://www.chefkoch.de/rezepte/" target="_blank" style="color:gray; text-decoration:none;">View more ➜</a></p>',
    unsafe_allow_html=True)
#Rezeptegalerie

with col2:
    st.image("kürbissuppe.jpg")
    st.write("Kürbissuppe")
    st.markdown('<a href="https://www.chefkoch.de/rezepte/" target="_blank" style="color:gray; text-decoration:none;">View more ➜</a></p>',
    unsafe_allow_html=True)

with col3:
    st.image("Lammeintopf.jpg")
    st.write("Lammeintopf mit weißen Bohnen")
    st.markdown('<a href="https://www.chefkoch.de/rezepte/" target="_blank" style="color:gray; text-decoration:none;">View more ➜</a></p>',
    unsafe_allow_html=True)

with col4:
    st.image("schokokuchen.jpg")
    st.write("Schokokuchen")
    st.markdown('<a href="https://www.chefkoch.de/rezepte/" target="_blank" style="color:gray; text-decoration:none;">View more ➜</a></p>',
    unsafe_allow_html=True)



st.link_button("View more", 'https://www.chefkoch.de/rezepte/', help=None, type="secondary", disabled=False, use_container_width=False)
