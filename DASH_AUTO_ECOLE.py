import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import numpy as np
import io
import base64
import os
import plotly.graph_objects as go


import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd


from datetime import datetime
from datetime import date


# In[7]:


DTJ=date.today()
print(DTJ)

current_year = DTJ.strftime("%Y")
print("Année actuelle =", current_year)


# ## 2. Reporting dynamique (DASH)

# ### 2.1 / Manipulations des données

# In[8]:



# Charger le fichier Excel depuis un chemin relatif ou en ligne
file_path = "02_INPUTS/_20250308_inputs_auto_ecole.xlsx"

# Vérification que le fichier existe
if not os.path.exists(file_path):
    raise FileNotFoundError(f"Le fichier {file_path} est introuvable !")

# Charger les données Excel
df = pd.read_excel(file_path, sheet_name="DATABASE")



df["Délais_inter_lecon"]=df["Délais_inter_lecon"].astype(int)
df=df.sort_values(by=["SCORE"],ascending=False)

# Conversion explicite des dates après la création du DataFrame
for col in ["Date_naissance", "Date_signature", "Date_obtention_code","Date_premiere_lecon", "Date_derniere_lecon"]:
    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')


print(df.shape)
print(df.dtypes)
df.head()


# ### 2.2 / Représentation Dash

# In[22]:


# Initialisation de l'application Dash avec Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#df = pd.DataFrame(df).head(10)  # Afficher uniquement les 10 premières lignes

df=df[["Prénom","Nom","Date_naissance","Date_signature","Date_obtention_code","Nb_presentations_code","Nb_lecons_conduite","Nb_heures_conduite","Anciennete_premiere_lecon","Anciennete_derniere_lecon","Délais_inter_lecon","Flag_deja_presente","SCORE"]]

df["SCORE"]=(df["SCORE"]*100).astype(int).astype(str) + '%'

# Conversion explicite des dates après la création du DataFrame
#date_columns = [
#    "Date_naissance", "Date_signature", "Date_obtention_code",
#    "Date_premiere_lecon", "Date_derniere_lecon"
#]
#for col in date_columns:
#    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')


# Mise en page de l'application
app.layout = dbc.Container(
    [
        # Bandeau supérieur dynamique
        dbc.Row(
            dbc.Col(
                html.Div(
                    id="header-banner",
                    className="header-banner",
                    style={"margin-top": "20px", "border": "1px solid black", "backgroundColor": "#d0e4ff"}  # Fond bleu clair
                ),
                width=12
            ),
            className="mb-4"
        ),
        
        # Tableau de données avec filtres et tri
        dbc.Row(
            dbc.Col(
                dash_table.DataTable(
                    id='data-table',
                    data=df.to_dict('records'),
                    columns=[
                        {"name": i.replace("_", " "), "id": i, "deletable": False, "selectable": False} 
                        for i in df.columns
                    ],
                    filter_action="native",  # Ajout du filtre par colonne
                    sort_action="native",  # Activation du tri
                    sort_mode="multi",  # Permettre le tri sur plusieurs colonnes
                    style_table={"overflowX": "auto", "width": "100%"},
                    style_header={"backgroundColor": "#e0e0e0", "fontWeight": "bold", "textAlign": "center", "fontSize": "0.75rem", "whiteSpace": "normal"},
                    style_data_conditional=[
                        {"if": {"row_index": "odd"}, "backgroundColor": "#d0e4ff"},  # Une ligne sur deux en bleu clair
                        {"if": {"row_index": "even"}, "backgroundColor": "white"}  # Fond blanc sinon
                    ],
                    style_data={"color": "black", "textAlign": "center", "fontSize": "0.9rem"},
                    page_size=10  # Afficher 10 lignes avec pagination
                ),
                width=12
            )
        )
    ],
    fluid=True,  # Assure la responsivité
    style={"backgroundColor": "white", "minHeight": "100vh"}  # Fond global blanc + fond sous le tableau blanc
    #style={"background-image": 'url("/assets/fonds_page.jpeg")', "background-size": "cover", "background-position": "center bottom"}  # Image de fond
)

# Callback pour mettre à jour le bandeau en fonction du premier résultat filtré
@app.callback(
    Output("header-banner", "children"),
    Input("data-table", "derived_virtual_data")
)
def update_banner(filtered_data):
    if filtered_data and len(filtered_data) > 0:
        first_row = filtered_data[0]
        score_value = int(first_row["SCORE"].replace('%', ''))
        
        # Déterminer l'image en fonction du score
        if 75 <= score_value <= 100:
            image_src = "/assets/feu_vert.jpg"
        elif 50 <= score_value < 75:
            image_src = "/assets/feu_orange.jpg"
        else:
            image_src = "/assets/feu_rouge.jpg"
        
        return [
            html.Span(first_row["Prénom"], className="info-box"),
            html.Span(first_row["Nom"], className="info-box"),
            html.Span(first_row["Date_naissance"], className="info-box", style={"margin": "0 10px"}),
            html.Span(first_row["SCORE"], className="info-box", style={"margin": "0 10px"}),
            html.Img(src=image_src, style={"height": "30px", "width": "30px", "margin-left": "5px"})
        ]
    return ""  # Affichage vide si aucune donnée

# CSS pour la mise en forme responsive
app.index_string = '''
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Mon Application Dash</title>
    {%metas%}
    {%favicon%}
    {%css%}
    <style>
        body { background-color: #d3d3d3; }
        .header-banner {
            display: flex;
            justify-content: space-around;
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
        }
        .info-box { font-weight: bold; font-size: 1.2rem; }
    </style>
</head>
<body>
    {%app_entry%}
    {%config%}
    {%scripts%}
    {%renderer%}
</body>
</html>
'''



# Définir server pour Gunicorn
server = app.server  

# Récupération du port attribué par Render (ou 8050 par défaut en local)
port = int(os.environ.get("PORT", 8050))

if __name__ == "__main__":
    app.run_server(debug=False, host="0.0.0.0", port=port)
