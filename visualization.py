import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Music & Social Connectedness", layout="wide", page_icon="🎵")

# Country code to full name mapping
COUNTRY_NAMES = {
    'AE': 'United Arab Emirates', 'AR': 'Argentina', 'AT': 'Austria', 'AU': 'Australia',
    'BE': 'Belgium', 'BG': 'Bulgaria', 'BO': 'Bolivia', 'BR': 'Brazil', 'BY': 'Belarus',
    'CA': 'Canada', 'CH': 'Switzerland', 'CL': 'Chile', 'CO': 'Colombia', 'CR': 'Costa Rica',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark', 'DO': 'Dominican Republic',
    'EC': 'Ecuador', 'EE': 'Estonia', 'EG': 'Egypt', 'ES': 'Spain', 'FI': 'Finland',
    'FR': 'France', 'GB': 'United Kingdom', 'GR': 'Greece', 'GT': 'Guatemala',
    'HN': 'Honduras', 'HU': 'Hungary', 'ID': 'Indonesia', 'IE': 'Ireland', 'IL': 'Israel',
    'IN': 'India', 'IS': 'Iceland', 'IT': 'Italy', 'JP': 'Japan', 'KR': 'South Korea',
    'KZ': 'Kazakhstan', 'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia',
    'MA': 'Morocco', 'MX': 'Mexico', 'MY': 'Malaysia', 'NG': 'Nigeria', 'NL': 'Netherlands',
    'NO': 'Norway', 'NZ': 'New Zealand', 'PA': 'Panama', 'PE': 'Peru', 'PH': 'Philippines',
    'PK': 'Pakistan', 'PL': 'Poland', 'PT': 'Portugal', 'PY': 'Paraguay', 'RO': 'Romania',
    'SA': 'Saudi Arabia', 'SE': 'Sweden', 'SG': 'Singapore', 'SK': 'Slovakia', 'SV': 'El Salvador',
    'TH': 'Thailand', 'TR': 'Turkey', 'TW': 'Taiwan', 'UA': 'Ukraine', 'US': 'United States',
    'UY': 'Uruguay', 'VE': 'Venezuela', 'VN': 'Vietnam', 'ZA': 'South Africa',
}

import pycountry

def to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

@st.cache_data
def load_data():
    df = pd.read_excel('Final_data_combined.xlsx')
    country_df = pd.read_excel('final_final_dataset_RQ2_single_countries.xlsx')
    
    country_df = country_df.rename(columns={
        'Country Code': 'Code',
        'Average_Valence': 'Valence',
        'Average_Energy': 'Energy',
        'Average_Danceability': 'Danceability',
        'Financial Stress': 'Financial_Stress',
        'Cost of Living': 'Cost_of_Living',
        'Local Purchasing Power': 'Purchasing_Power',
        'Music Mood': 'Music_Mood'
    })
    
    country_df['Name'] = country_df['Code'].map(COUNTRY_NAMES).fillna(country_df['Code'])
    country_df['Code3'] = country_df['Code'].apply(to_iso3)
    return df, country_df

df, country_df = load_data()

def get_pairs_for_country(code):
    mask_a = df['Country_A'] == code
    mask_b = df['Country_B'] == code
    pairs_a = df[mask_a][['Country_B', 'Music_Distance', 'Jaccard_Similarity_Songs', 'SCI_Score_normalized']].rename(columns={'Country_B': 'Other'})
    pairs_b = df[mask_b][['Country_A', 'Music_Distance', 'Jaccard_Similarity_Songs', 'SCI_Score_normalized']].rename(columns={'Country_A': 'Other'})
    pairs = pd.concat([pairs_a, pairs_b]).reset_index(drop=True)
    pairs['Other_Name'] = pairs['Other'].map(COUNTRY_NAMES).fillna(pairs['Other'])
    return pairs

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.title("🎵 Music Preferences & Social Connectedness")
st.markdown("**Technical Communication Dashboard** — Exploring how Facebook social ties and economic conditions relate to national music taste across 70 countries.")
with st.expander("📖 What do the metrics mean?"):
    st.markdown("**🎶 Music Distance**\nsays how much the vibe of music differs (based on energy, happiness and danceability). **Lower = more similar music.**")
    st.markdown("**🔀 Jaccard Similarity**\nis the number of top 50 songs shared between two countries. **Higher = more songs in common.**")
    st.markdown("**👥 SCI (Social Connectedness)**\nsays how closely connected two countries are based on Facebook friendships. **Higher = more social ties.**")
    st.markdown("**🎸 Music Mood**\n says how energetic, positive and danceable music is. **Higher = more energetic/happy.**")
    st.markdown("**😔 Mood-congruency theory**\nclaims that people listen to music matching their current emotional state. It assumes that in countries with **high financial stress**, people listen to more **melancholic and lower-energy music**.")
    st.markdown("**✨ Mood-regulation theory**\nclaims that people listen to music to escape their mood. It assumes that in countries with **high financial stress**, people listen to more **energetic and uplifting music** to escape their problems and everyday stress.")

st.divider()

# ─── TAB LAYOUT ───────────────────────────────────────────────────────────────
# Użyj tego:
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "🔍 Country Explorer" # Ustaw domyślną na tę, na której pracujesz

# To sprawi, że Streamlit nie będzie "skakał" do pierwszej zakładki
tab1, tab2, tab3 = st.tabs(["🗺️ World Map", "🔍 Country Explorer", "📊 Correlations"])
# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — WORLD MAP
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Country-level music & economic profiles")
    map_metric = st.selectbox(
        "Color countries by:",
        ["Music_Mood", "Financial_Stress", "Valence", "Energy", "Danceability", "Cost_of_Living", "Purchasing_Power"],
        format_func=lambda x: {
            "Music_Mood": "🎸 Music Mood (higher = more energetic/happy)",
            "Financial_Stress": "💸 Financial Stress (higher = more economic pressure)",
            "Valence": "😊 Valence (positivity of music)",
            "Energy": "⚡ Energy (intensity of music)",
            "Danceability": "💃 Danceability",
            "Cost_of_Living": "🏠 Cost of Living Index",
            "Purchasing_Power": "💰 Local Purchasing Power"
        }[x]
    )

    color_labels = {
        "Music_Mood": "Music Mood",
        "Financial_Stress": "Financial Stress",
        "Valence": "Valence",
        "Energy": "Energy",
        "Danceability": "Danceability",
        "Cost_of_Living": "Cost of Living",
        "Purchasing_Power": "Purchasing Power"
    }

    # Ensure Code3 is available BEFORE creating the map
    country_df['Code3'] = country_df['Code'].apply(to_iso3)

    fig_map = px.choropleth(
        country_df,
        locations="Code3",
        locationmode="ISO-3",
        color=map_metric,
        hover_name="Name",
        hover_data={
            "Code3": False,
            "Music_Mood": ":.3f",
            "Financial_Stress": ":.2f",
            "Valence": ":.3f",
            "Energy": ":.3f",
            "Danceability": ":.3f"
        },
        color_continuous_scale="RdYlGn" if map_metric != "Financial_Stress" else "RdYlGn_r",
        labels={map_metric: color_labels[map_metric]},
        title=f"World Map: {color_labels[map_metric]}"
    )

    # ZAKTUALIZOWANE USTAWIENIA WYGLĄDU:
    fig_map.update_geos(
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor="#E5E5E5", # Szary dla krajów bez danych
        coastlinecolor="white"
    )

    fig_map.update_layout(
        height=700, 
        margin={"r":0, "t":40, "l":0, "b":0} 
    )
    
    st.plotly_chart(fig_map, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COUNTRY EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Explore a specific country")

    country_options = sorted(country_df['Code'].tolist(), key=lambda x: COUNTRY_NAMES.get(x, x))
    selected_code = st.selectbox(
        "Select a country:",
        country_options,
        format_func=lambda x: f"{COUNTRY_NAMES.get(x, x)} ({x})",
        index=country_options.index('PL') if 'PL' in country_options else 0
    )

    selected_country = country_df[country_df['Code'] == selected_code].iloc[0]
    pairs = get_pairs_for_country(selected_code)

    # Country profile
    st.markdown(f"### 🌍 {COUNTRY_NAMES.get(selected_code, selected_code)}")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🎸 Music Mood", f"{selected_country['Music_Mood']:.3f}")
    c2.metric("😊 Valence", f"{selected_country['Valence']:.3f}")
    c3.metric("⚡ Energy", f"{selected_country['Energy']:.3f}")
    c4.metric("💸 Financial Stress", f"{selected_country['Financial_Stress']:.2f}")
    c5.metric("💰 Purchasing Power", f"{selected_country['Purchasing_Power']:.1f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🎶❤️ Most similar music (lowest Music Distance)")
        top_similar = pairs.nsmallest(10, 'Music_Distance')[['Other_Name', 'Music_Distance', 'Jaccard_Similarity_Songs', 'SCI_Score_normalized']]
        top_similar.columns = ['Country', 'Music Distance ↓', 'Jaccard', 'SCI']
        top_similar = top_similar.reset_index(drop=True)
        top_similar.index += 1
        st.dataframe(top_similar.style.format({'Music Distance ↓': '{:.4f}', 'Jaccard': '{:.4f}', 'SCI': '{:.3f}'}), use_container_width=True)

    with col_right:
        st.markdown("#### 🎶❌ Least similar music (highest Music Distance)")
        top_dissimilar = pairs.nlargest(10, 'Music_Distance')[['Other_Name', 'Music_Distance', 'Jaccard_Similarity_Songs', 'SCI_Score_normalized']]
        top_dissimilar.columns = ['Country', 'Music Distance ↑', 'Jaccard', 'SCI']
        top_dissimilar = top_dissimilar.reset_index(drop=True)
        top_dissimilar.index += 1
        st.dataframe(top_dissimilar.style.format({'Music Distance ↑': '{:.4f}', 'Jaccard': '{:.4f}', 'SCI': '{:.3f}'}), use_container_width=True)

    st.divider()

    col_left2, col_right2 = st.columns(2)

    with col_left2:
        st.markdown("#### 🔀❤️ Most song overlap (highest Jaccard)")
        top_jaccard = pairs.nlargest(10, 'Jaccard_Similarity_Songs')[['Other_Name', 'Jaccard_Similarity_Songs', 'Music_Distance', 'SCI_Score_normalized']]
        top_jaccard.columns = ['Country', 'Jaccard ↑', 'Music Distance', 'SCI']
        top_jaccard = top_jaccard.reset_index(drop=True)
        top_jaccard.index += 1
        st.dataframe(top_jaccard.style.format({'Jaccard ↑': '{:.4f}', 'Music Distance': '{:.4f}', 'SCI': '{:.3f}'}), use_container_width=True)

    with col_right2:
        st.markdown("#### 🔀❌ Least song overlap (lowest Jaccard)")
        top_jaccard_low = pairs.nsmallest(10, 'Jaccard_Similarity_Songs')[['Other_Name', 'Jaccard_Similarity_Songs', 'Music_Distance', 'SCI_Score_normalized']]
        top_jaccard_low.columns = ['Country', 'Jaccard ↓', 'Music Distance', 'SCI']
        top_jaccard_low = top_jaccard_low.reset_index(drop=True)
        top_jaccard_low.index += 1
        st.dataframe(top_jaccard_low.style.format({'Jaccard ↓': '{:.4f}', 'Music Distance': '{:.4f}', 'SCI': '{:.3f}'}), use_container_width=True)

    st.divider()

    # --- ENHANCED MAP SECTION WITH TOGGLE ---
    st.markdown(f"#### 🗺️ Map Explorer: {COUNTRY_NAMES.get(selected_code, selected_code)}")
    
    map_mode = st.radio(
        "Highlight top 10 countries by:",
        ["Music Mood (Lowest Music Distance)", "Song Overlap (Jaccard Similarity)"],
        horizontal=True
    )

    if "Jaccard" in map_mode:
        metric_col = 'Jaccard_Similarity_Songs'
        color_scale = 'Blues'  
        hover_label = 'Jaccard Similarity'
    else:
        metric_col = 'Music_Distance'
        color_scale = 'Purples_r' # Ciemna zieleń = mały dystans (podobny vibe)
        hover_label = 'Music Distance'

    map_df = country_df.copy()
    map_df = map_df.merge(
        pairs[['Other', metric_col]].rename(columns={'Other': 'Code'}),
        on='Code', how='left'
    )

    fig_highlight = px.choropleth(
        map_df[map_df['Code'] != selected_code],
        locations="Code3",
        locationmode="ISO-3",
        color=metric_col,
        hover_name="Name",
        hover_data={"Code3": False, metric_col: ":.4f"},
        color_continuous_scale=color_scale,
        labels={metric_col: hover_label},
        title=f"{COUNTRY_NAMES.get(selected_code, selected_code)}: {hover_label}"
    )

    selected_row = map_df[map_df['Code'] == selected_code]
    fig_highlight.add_trace(go.Choropleth(
        locations=selected_row['Code3'],
        z=[1],
        colorscale=[[0, '#e74c3c'], [1, '#e74c3c']],
        showscale=False,
        hovertemplate=f"<b>{COUNTRY_NAMES.get(selected_code, selected_code)}</b><br>Selected<extra></extra>"
    ))

    # To ustawienie sprawi, że kraje bez danych będą jasnoszare
    fig_highlight.update_geos(
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor="#E5E5E5", 
        coastlinecolor="white"
    )

    fig_highlight.update_layout(
        height=750,
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(title=hover_label)
    )

    st.plotly_chart(fig_highlight, use_container_width=True)

    # Scatter: all pairs for this country
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("#### 👥 SCI vs 🎶 Music Distance")
        pairs['Other_Name_Full'] = pairs['Other'].map(COUNTRY_NAMES).fillna(pairs['Other'])
        fig_scatter = px.scatter(
            pairs,
            x='SCI_Score_normalized',
            y='Music_Distance',
            hover_name='Other_Name_Full',
            color='Music_Distance', # Kolor pasuje do osi Y
            color_continuous_scale='Purples_r',
            labels={
                'SCI_Score_normalized': 'Social Connection Strength',
                'Music_Distance': 'Music vibe similarity',
            },
            title=f"Music vibe similarity: {COUNTRY_NAMES.get(selected_code, selected_code)}"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("Lower Music Distance (music vibe similarity) with higher SCI (dots densly going from top left side to low right side) = more similar music taste between socially connected countries")

    with col_s2:
        st.markdown("#### 👥SCI vs 🔀 Jaccard Similarity")
        fig_scatter2 = px.scatter(
            pairs,
            x='SCI_Score_normalized',
            y='Jaccard_Similarity_Songs',
            hover_name='Other_Name_Full',
            color='Jaccard_Similarity_Songs', # Kolor pasuje do osi Y
            color_continuous_scale='Blues',
            labels={
                'SCI_Score_normalized': 'Social Connection Strength',
                'Jaccard_Similarity_Songs': '% of Shared Songs',
            },
            title=f"% of Shared Songs: {COUNTRY_NAMES.get(selected_code, selected_code)}"
        )
        fig_scatter2.update_layout(height=400)
        st.plotly_chart(fig_scatter2, use_container_width=True)
        st.caption("Higher Jaccard similarity (\% \of shared songs) with higher SCI (dots densly going from bottom left side to top right side) = more songs in common between socially connected countries")
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Global correlations: SCI, Economics & Music")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 👥 SCI vs 🎶 Music Distance (all 2,415 pairs)")
        fig1 = px.scatter(
            df, x='SCI_Score_normalized', y='Music_Distance',
            opacity=0.4,
            trendline='ols',
            labels={'SCI_Score_normalized': 'SCI Normalized', 'Music_Distance': 'Music Distance'},
            color_discrete_sequence=['#9b59b6']
        )
        fig1.update_layout(height=380)
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("r = -0.33: stronger social ties → more similar music, weak/moderate negative relation, meaning that the more socially related countries are, the more similar music they listen to")

    with col2:
        st.markdown("#### 👥 SCI vs 🔀 Jaccard Similarity (all 2,415 pairs)")
        fig2 = px.scatter(
            df, x='SCI_Score_normalized', y='Jaccard_Similarity_Songs',
            opacity=0.4,
            trendline='ols',
            labels={'SCI_Score_normalized': 'SCI Normalized', 'Jaccard_Similarity_Songs': 'Jaccard Songs'},
            color_discrete_sequence=['#3498db']
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("r = 0.54: stronger social ties → more songs in common - moderate positive relation, meaning that the more socially related countries are, the more similar music they listen to")

    st.divider()
    st.markdown("#### 💸 Financial Stress vs 🎸 Music Mood (70 countries)")
    fig3 = px.scatter(
        country_df, x='Financial_Stress', y='Music_Mood',
        hover_name='Name', trendline='ols',
        labels={'Financial_Stress': 'Financial Stress', 'Music_Mood': 'Music Mood'},
        color_discrete_sequence=['#e74c3c']
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("r = 0.24 (p = 0.043): very weak positive - neither mood-congruency nor mood-regulation clearly supported")

st.divider()
st.caption("Data: Facebook SCI (Meta AI) · Spotify Top 50 (Kaggle) · Cost of Living (Numbeo) | Technical Communication — Maja Rzeszotarska")
