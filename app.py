import streamlit as st
from PIL import Image
from pathlib import Path
import base64
import pandas as pd


# import neccessary files
amino_df = pd.read_csv('./dataFolder/Protein.csv')
alc_df = pd.read_csv('./dataFolder/Alcohol.csv')
sug_df = pd.read_csv('./dataFolder/Sugar.csv')
 

# Page layout
## Page expands to full width
st.set_page_config(page_title='Coating fouling release ML-predictor', page_icon=":computer:", layout='wide')
st.title('NADE toxicity prediction tool', )
######
# Function to put a picture as header   
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    encoded = base64.b64encode(img_bytes).decode()
    return encoded

image = Image.open('rat_toxicity_image.png')
resized_image = image.resize((1600, 800))
st.image(resized_image)

# Create a layout with 4 columns
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)

# Input for amino acid mol ratio'
amino_ratio = col1.number_input('Amino Acid mol ratio', max_value=30)

if amino_ratio < 1 or amino_ratio > 30:
    col5.error("Amino acid mol ratio must be between 0 and 30.")

# Input for alcohol mol ratio
alc_ratio = col2.number_input('Alcohol mol ratio', max_value=10)
if alc_ratio < 1 or alc_ratio > 30:
    col6.error("alcohol mol ratio must be between 1 and 10")

# Input for sugar
sug_ratio = col3.number_input('Sugar mol ratio',max_value=10)
if sug_ratio < 0 or sug_ratio > 10:
    col7.error("sugar mol ratio must be between 0 and 10")


# Input for sugar
water_fraction = col4.number_input('Water fraction',max_value=1.0)
if water_fraction < 0 or water_fraction > 1.0:
    col8.error("water fraction must be between 0 and 1")


# Dropdown for 'PM' and 'DP'
amino_dict = dict(zip(amino_df["Substance Name"].str.strip(), amino_df["LD50"]))
alc_dict = dict(zip(alc_df["Substance Name"].str.strip(), alc_df["LD50"]))
sug_dict = dict(zip(sug_df["Substance Name"].str.strip(), sug_df["LD50"]))


# drop down menu options 
amino_options = list(amino_dict.keys())
amino_choice = col1.selectbox('Select amino acid name', amino_options)
amino_tox = amino_dict[amino_choice]

alc_options = list(alc_dict.keys())
alc_choice = col2.selectbox('Select alcohol', alc_options)
alc_tox = alc_dict[alc_choice]

sug_options = list(sug_dict.keys())
sug_choice = col3.selectbox('Select sugar', sug_options)
sug_tox = sug_dict[sug_choice]

####
# Toxicity prediction function 

def calculate_weighted_tox(water_fraction, alcohol_ratio, sugar_ratio, amino_ratio, alcohol_tox, sugar_tox, amino_tox):
    components_fraction = 1- water_fraction
    total_ratio = alcohol_ratio + sugar_ratio + amino_ratio
    alcohol_weight = components_fraction * (alcohol_ratio / total_ratio)
    sugar_weight = components_fraction * (sugar_ratio / total_ratio)
    protein_weight = components_fraction * (amino_ratio / total_ratio)
    
    weighted_tox = (alcohol_weight * alcohol_tox) + (sugar_weight * sugar_tox) + (protein_weight * amino_tox)
    
    return weighted_tox

predicted_tox = calculate_weighted_tox(water_fraction, alc_ratio, 
                                       sug_ratio, amino_ratio, alc_tox, sug_tox, amino_tox)
st.markdown(f'## the NADE toxicity is {round(predicted_tox, 2)} mg/kg')
