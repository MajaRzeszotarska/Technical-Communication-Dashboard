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

@st.cache_data
def load_data():
    df = pd.read_excel('Final_data_combined.xlsx')
    # Build single-country lookup
    countries_a = df[['Country_A', 'Music_Mood_A', 'Valence_A', 'Energy_A', 'Danceability_A',
                       'Financial_Stress_A', 'Cost_of_living_A', 'Local_Purchasing_Power_A']].copy()
    countries_a.columns = ['Code', 'Music_Mood', 'Valence', 'Energy', 'Danceability',
                           'Financial_Stress', 'Cost_of_Living', 'Purchasing_Power']
    countries_b = df[['Country_B', 'Music_Mood_B', 'Valence_B', 'Energy_B', 'Danceability_B',
                       'Financial_Stress_B', 'Cost_of_living_B', 'Local_Purchasing_Power_B']].copy()
    countries_b.columns = ['Code', 'Music_Mood', 'Valence', 'Energy', 'Danceability',
                           'Financial_Stress', 'Cost_of_Living', 'Purchasing_Power']
    country_df = pd.concat([countries_a, countries_b]).drop_duplicates('Code').reset_index(drop=True)
    country_df['Name'] = country_df['Code'].map(COUNTRY_NAMES).fillna(country_df['Code'])
    return df, country_df

df, country_df = load_data()

# Convert 2-letter to 3-letter ISO codes
import pycountry
def to_iso3(code):
    try:
        return pycountry.countries.get(alpha_2=code).alpha_3
    except:
        return None

country_df['Code3'] = country_df['Code'].apply(to_iso3)

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
st.markdown("**Bachelor Thesis Dashboard** — Exploring how Facebook social ties and economic conditions relate to national music taste across 70 countries.")

with st.expander("📖 What do the metrics mean?"):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🎶 Music Distance**\nEuclidean distance in valence–energy–danceability space. **Lower = more similar music.** Range: 0–0.4+")
    with col2:
        st.markdown("**🔀 Jaccard Similarity**\nFraction of Top 50 songs shared between two countries. **Higher = more songs in common.** Range: 0–1")
    with col3:
        st.markdown("**🌐 SCI (Social Connectedness)**\nNormalized Facebook friendship index. **Higher = more social ties.** Range: 0.2–0.65")

st.divider()

# ─── TAB LAYOUT ───────────────────────────────────────────────────────────────
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
            "Music_Mood": "🎵 Music Mood (higher = more energetic/happy)",
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

    # DODAJ TE LINIE:
    fig_map.update_layout(
        height=700, # Zwiększa wysokość mapy (domyślnie jest to ok. 450)
        margin={"r":0,"t":40,"l":0,"b":0} # Usuwa zbędne białe marginesy wokół mapy
    )
    
    # CRITICAL: This line was missing!
    st.plotly_chart(fig_map, use_container_width=True)
# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COUNTRY EXPLORER
# ══════════════════════════════════════════════════════════════════════════════
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
    c1.metric("🎵 Music Mood", f"{selected_country['Music_Mood']:.3f}")
    c2.metric("😊 Valence", f"{selected_country['Valence']:.3f}")
    c3.metric("⚡ Energy", f"{selected_country['Energy']:.3f}")
    c4.metric("💸 Financial Stress", f"{selected_country['Financial_Stress']:.2f}")
    c5.metric("💰 Purchasing Power", f"{selected_country['Purchasing_Power']:.1f}")

    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### 🎶 Most similar music (lowest Music Distance)")
        top_similar = pairs.nsmallest(10, 'Music_Distance')[['Other_Name', 'Music_Distance', 'Jaccard_Similarity_Songs', 'SCI_Score_normalized']]
        top_similar.columns = ['Country', 'Music Distance ↓', 'Jaccard Songs', 'SCI Normalized']
        top_similar = top_similar.reset_index(drop=True)
        top_similar.index += 1
        st.dataframe(
            top_similar.style.format({'Music Distance ↓': '{:.4f}', 'Jaccard Songs': '{:.4f}', 'SCI Normalized': '{:.3f}'}),
            use_container_width=True
        )

    with col_right:
        st.markdown("#### 🔀 Most song overlap (highest Jaccard)")
        top_jaccard = pairs.nlargest(10, 'Jaccard_Similarity_Songs')[['Other_Name', 'Jaccard_Similarity_Songs', 'Music_Distance', 'SCI_Score_normalized']]
        top_jaccard.columns = ['Country', 'Jaccard Songs ↑', 'Music Distance', 'SCI Normalized']
        top_jaccard = top_jaccard.reset_index(drop=True)
        top_jaccard.index += 1
        st.dataframe(
            top_jaccard.style.format({'Jaccard Songs ↑': '{:.4f}', 'Music Distance': '{:.4f}', 'SCI Normalized': '{:.3f}'}),
            use_container_width=True
        )

    st.divider()

    # --- ENHANCED MAP SECTION WITH TOGGLE ---
    st.markdown(f"#### 🗺️ Map Explorer: {COUNTRY_NAMES.get(selected_code, selected_code)}")
    
    # Selection for Map Mode
    map_mode = st.radio(
        "Highlight top 10 countries by:",
        ["Song Overlap (Jaccard Similarity)", "Music Mood (Lowest Music Distance)"],
        horizontal=True
    )

    # Logic for finding the Top 10 based on selection
    if "Jaccard" in map_mode:
        top10_data = pairs.nlargest(10, 'Jaccard_Similarity_Songs')
        metric_col = 'Jaccard_Similarity_Songs'
        label_text = '🔀 Top 10 Jaccard'
    else:
        top10_data = pairs.nsmallest(10, 'Music_Distance')
        metric_col = 'Music_Distance'
        label_text = '🎶 Top 10 Music Distance'

    top10_codes = top10_data['Other'].tolist()
    
    # Build Map DataFrame
    map_df = country_df.copy()
    map_df['Group'] = map_df['Code'].apply(
        lambda x: '🎯 Selected' if x == selected_code
        else (label_text if x in top10_codes else '⬜ Other')
    )
    
    # Color definition
    color_map = {'🎯 Selected': '#e74c3c', label_text: '#3498db', '⬜ Other': '#ecf0f1'}

    fig_highlight = px.choropleth(
        map_df,
        locations="Code3",
        locationmode="ISO-3",
        color="Group",
        hover_name="Name",
        hover_data={"Code3": False, "Group": False},
        color_discrete_map=color_map,
        title=f"{COUNTRY_NAMES.get(selected_code, selected_code)}: {label_text}"
    )

    # Apply BIGGER size and clean margins
    fig_highlight.update_layout(
        height=750, 
        margin=dict(l=0, r=0, t=50, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_highlight, use_container_width=True)

    st.divider()

    # Scatter: all pairs for this country
    st.markdown("#### 📉 SCI vs Music Distance for all pairs with this country")
    pairs['Other_Name_Full'] = pairs['Other'].map(COUNTRY_NAMES).fillna(pairs['Other'])
    fig_scatter = px.scatter(
        pairs,
        x='SCI_Score_normalized',
        y='Music_Distance',
        hover_name='Other_Name_Full',
        color='Jaccard_Similarity_Songs',
        color_continuous_scale='Blues',
        labels={
            'SCI_Score_normalized': 'Normalized SCI Score',
            'Music_Distance': 'Music Distance',
            'Jaccard_Similarity_Songs': 'Jaccard'
        },
        title=f"All pairs: {COUNTRY_NAMES.get(selected_code, selected_code)}"
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Global correlations: SCI, Economics & Music")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### SCI vs Music Distance (all 2,415 pairs)")
        fig1 = px.scatter(
            df, x='SCI_Score_normalized', y='Music_Distance',
            opacity=0.4,
            trendline='ols',
            labels={'SCI_Score_normalized': 'SCI Normalized', 'Music_Distance': 'Music Distance'},
            color_discrete_sequence=['#3498db']
        )
        fig1.update_layout(height=380)
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("r = -0.33: stronger social ties → more similar music")

    with col2:
        st.markdown("#### SCI vs Jaccard Similarity (all 2,415 pairs)")
        fig2 = px.scatter(
            df, x='SCI_Score_normalized', y='Jaccard_Similarity_Songs',
            opacity=0.4,
            trendline='ols',
            labels={'SCI_Score_normalized': 'SCI Normalized', 'Jaccard_Similarity_Songs': 'Jaccard Songs'},
            color_discrete_sequence=['#2ecc71']
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("r = 0.54: stronger social ties → more songs in common")

    st.divider()
    st.markdown("#### Financial Stress vs Music Mood (70 countries)")
    fig3 = px.scatter(
        country_df, x='Financial_Stress', y='Music_Mood',
        hover_name='Name', trendline='ols',
        labels={'Financial_Stress': 'Financial Stress', 'Music_Mood': 'Music Mood'},
        color_discrete_sequence=['#e74c3c']
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("r = 0.24 (p = 0.043): very weak positive — neither mood-congruency nor mood-regulation clearly supported")

st.divider()
st.caption("Data: Facebook SCI (Meta AI) · Spotify Top 50 (Kaggle) · Cost of Living (Numbeo) | Bachelor Thesis — Maja Rzeszotarska")