import streamlit as st
from PIL import Image
from pathlib import Path
import base64
import pandas as pd


# import neccessary files
amino_df = pd.read_csv('./dataFolder/Protein_MW_GCN.csv')
alc_df = pd.read_csv('./dataFolder/Alcohol_MW_GCN.csv')
sug_df = pd.read_csv('./dataFolder/Sugar_MW_GCN.csv')
 

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

amino_ratio = col1.slider('Amino Acid mol ratio', min_value=1, max_value=30, value=1)
if amino_ratio < 1 or amino_ratio > 30:
    col5.error("Amino acid mol ratio must be between 0 and 30.")

alc_ratio = col2.slider('Alcohol mol ratio', min_value=1, max_value=10, value=1)
if alc_ratio < 1 or alc_ratio > 10:
    col6.error("Alcohol mol ratio must be between 1 and 10.")

sug_ratio = col3.slider('Sugar mol ratio', min_value=0, max_value=10, value=0)
if sug_ratio < 0 or sug_ratio > 10:
    col7.error("Sugar mol ratio must be between 0 and 10.")

water_fraction = col4.slider('Water fraction', min_value=0.0, max_value=1.0, value=0.0, step=0.01)
if water_fraction < 0 or water_fraction > 1.0:
    col8.error("Water fraction must be between 0 and 1.")


# Dropdown for 'PM' and 'DP'
amino_dict = dict(zip(amino_df["Substance Name"].str.strip(), zip(amino_df["LD50"], amino_df["Normalized_LD50"], amino_df["GCN_pred"], amino_df["Normalized_GCN_pred"])))
alc_dict = dict(zip(alc_df["Substance Name"].str.strip(), zip(alc_df["LD50"], alc_df["Normalized_LD50"], alc_df["GCN_pred"], alc_df["Normalized_GCN_pred"])))
sug_dict = dict(zip(sug_df["Substance Name"].str.strip(), zip(sug_df["LD50"], sug_df["Normalized_LD50"], sug_df["GCN_pred"], sug_df["Normalized_GCN_pred"])))


# drop down menu options 
amino_options = list(amino_dict.keys())
amino_choice = col1.selectbox('Select amino acid name', amino_options)
amino_tox = amino_dict[amino_choice][0]
amino_tox_mw = amino_dict[amino_choice][1]
amino_tox_GCN = amino_dict[amino_choice][2]
amino_tox_GCN_mw = amino_dict[amino_choice][3]

alc_options = list(alc_dict.keys())
alc_choice = col2.selectbox('Select alcohol', alc_options)
alc_tox = alc_dict[alc_choice][0]
alc_tox_mw = alc_dict[alc_choice][1]
alc_tox_GCN = alc_dict[alc_choice][2]
alc_tox_GCN_mw = alc_dict[alc_choice][3]

sug_options = list(sug_dict.keys())
sug_choice = col3.selectbox('Select sugar', sug_options)
sug_tox = sug_dict[sug_choice][0]
sug_tox_mw = sug_dict[sug_choice][1]
sug_tox_GCN = sug_dict[sug_choice][2]
sug_tox_GCN_mw = sug_dict[sug_choice][3]

####
# Toxicity prediction function 
# which function should I choose?
def calculate_weighted_tox(water_fraction, alcohol_ratio, sugar_ratio, amino_ratio, alcohol_tox, sugar_tox, amino_tox):
    '''
    This function does not work currectly. DON'T USE THIS
    '''
    components_fraction = 1- water_fraction
    total_ratio = alcohol_ratio + sugar_ratio + amino_ratio
    alcohol_weight = components_fraction * (alcohol_ratio / total_ratio)
    sugar_weight = components_fraction * (sugar_ratio / total_ratio)
    protein_weight = components_fraction * (amino_ratio / total_ratio)
    
    weighted_tox = (alcohol_weight * alcohol_tox) + (sugar_weight * sugar_tox) + (protein_weight * amino_tox)

    return weighted_tox


def calculate_weighted_tox2(water_fraction, alcohol_ratio, sugar_ratio, amino_ratio, alcohol_tox, sugar_tox, amino_tox):
    components_fraction = 1- water_fraction
    total_ratio = alcohol_ratio + sugar_ratio + amino_ratio
    alcohol_weight = components_fraction * (alcohol_ratio / total_ratio)
    sugar_weight = components_fraction * (sugar_ratio / total_ratio)
    protein_weight = components_fraction * (amino_ratio / total_ratio)
    
    weighted_tox = (alcohol_weight * 1/alcohol_tox) + (sugar_weight * 1/sugar_tox) + (protein_weight * 1/amino_tox)
    
    return 1/weighted_tox



pred_tox = calculate_weighted_tox2(water_fraction, alc_ratio, 
                                       sug_ratio, amino_ratio, alc_tox, sug_tox, amino_tox)

pred_tox_mw = calculate_weighted_tox2(water_fraction, alc_ratio, 
                                       sug_ratio, amino_ratio, alc_tox_mw, sug_tox_mw, amino_tox_mw)

pred_tox_GCN = calculate_weighted_tox2(water_fraction, alc_ratio, 
                                       sug_ratio, amino_ratio, alc_tox_GCN, sug_tox_GCN, amino_tox_GCN)

pred_tox_GCN_mw = calculate_weighted_tox2(water_fraction, alc_ratio, 
                                       sug_ratio, amino_ratio, alc_tox_GCN_mw, sug_tox_GCN_mw, amino_tox_GCN_mw)

st.markdown(f'# prediction based on CATMOS model')
st.markdown(f'## NADE LD50 is {round(pred_tox, 2)} mg/kg')
st.markdown(f'## NADE molar toxicity is {round(pred_tox_mw/100, 2)} mol/kg')

st.markdown(f'# prediction based on GCN model')
st.markdown(f'## NADE LD50 is is {round(pred_tox_GCN, 2)} mg/kg')
st.markdown(f'## NADE molar toxicity is {round(pred_tox_GCN_mw/100, 2)} mol/kg')