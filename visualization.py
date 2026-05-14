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
        'Financial Stress normalized': 'Financial_Stress',
        'Cost of Living Plus Rent Index Normalized': 'Cost_of_Living',
        'Local Purchasing Power Index normalized': 'Purchasing_Power',
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
st.title("🎵 Do socially connected countries listen to the same music?")
st.markdown("Social media connects people across the globe, but does that mean we all end up listening to the same music? Does countries' wealth influence what people listen to? Explore how social ties and economic conditions shape what 70 countries stream on Spotify, and what that reveals about culture, identity, and the global music scene.")
with st.expander("📖 What do the metrics mean?"):
    st.markdown("**🎶 Music Distance**\nsays how much the vibe of music differs (based on energy, happiness, and danceability). **Lower = more similar music.**")
    st.markdown("**🔀 Jaccard Similarity**\nis the number of songs two countries have in common in their Top 50 lists (in %). **Higher = more songs in common.**")
    st.markdown("**👥 SCI (Social Connectedness)**\nsays how closely connected two countries are based on Facebook friendships. **Higher = more social ties.**")
    st.markdown("**🎸 Music Mood**\n says how energetic, positive and danceable music is. **Higher = more energetic/happy.**")
    st.markdown("**😔 Mood-congruency theory**\nclaims that people listen to music matching their current emotional state - in countries with **high financial stress**, people listen to more **melancholic and lower-energy music**.")
    st.markdown("**✨ Mood-regulation theory**\nclaims that people listen to music to escape their mood - in countries with **high financial stress**, people listen to more **energetic and uplifting music** to escape their problems and everyday stress.")

with st.expander("🌍 About the data & countries"):
    st.markdown("""
    **What data is this based on?**
    This dashboard uses three datasets combined into one:
    - **Spotify Top 50** (via Kaggle): the top 50 most-streamed songs per country, with audio features like valence (happiness), energy, and danceability. Data is averaged per country across multiple snapshot dates, from 2023-10-18 to 2025-06-11.
    - **Facebook Social Connectedness Index** (Meta AI Research): measures how many Facebook friendships exist between countries, presented in a different scale so that patterns are visible.
    - **Numbeo Cost of Living**: cost of living, rent, groceries, and local purchasing power per country.
    
    **70 countries** are included across 6 continents (Asia, Africa, North America, South America, Europe and Australia), as shown on the world map on "World Map" tab. The detailed list is: Argentina, Australia, Austria, Belarus, Belgium, Bolivia, Brazil, Bulgaria, Canada, Chile, Colombia, Costa Rica, Czech Republic, Denmark, Dominican Republic, Ecuador, Egypt, El Salvador, Estonia, Finland, France, Germany, Greece, Guatemala, Honduras, Hungary, Iceland, India, Indonesia, Ireland, Israel, Italy, Japan, Kazakhstan, Latvia, Lithuania, Luxembourg, Malaysia, Mexico, Morocco, Netherlands, New Zealand, Nigeria, Norway, Pakistan, Panama, Paraguay, Peru, Philippines, Poland, Portugal, Romania, Saudi Arabia, Singapore, Slovakia, South Africa, South Korea, Spain, Sweden, Switzerland, Taiwan, Thailand, Turkey, Ukraine, United Arab Emirates, United Kingdom, United States, Uruguay, Venezuela, Vietnam.
    
    **2,415 country pairs** were created from these 70 countries to compare music similarity and social ties between every possible combination.
    """)

colorblind_mode = st.toggle("🎨 Colorblind-friendly mode (all maps)", value=False)

st.divider()
# ─── TAB LAYOUT ───────────────────────────────────────────────────────────────
# Użyj tego:
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "🔍 Country Explorer" # Ustaw domyślną na tę, na której pracujesz

# To sprawi, że Streamlit nie będzie "skakał" do pierwszej zakładki
tab1, tab2, tab3 = st.tabs(["🗺️ World Map", "🔍 Country Explorer", "📊 Patterns"])
# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — WORLD MAP
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("Explore the musical & economic values of each country")
    map_metric = st.selectbox(
        "Color countries by:",
        ["Music_Mood", "Financial_Stress", "Valence", "Energy", "Danceability", "Cost_of_Living", "Purchasing_Power"],
        format_func=lambda x: {
            "Music_Mood": "🎸 Music Mood (higher = more uplifting, positive, energetic music)",
            "Financial_Stress": "💸 Financial Stress (higher = more struggle to provide basic needs)",
            "Valence": "😊 Valence (higher = happier and more positive music)",
            "Energy": "⚡ Energy (higher = more intense and active music)",
            "Danceability": "💃 Danceability (higher = tempo and rythm better for dancing)",
            "Cost_of_Living": "🏠 Cost of Living (higher = more expensive everyday expenses)",
            "Purchasing_Power": "💰 Local Purchasing Power (higher = more wealth to buy goods and services)"
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

    # colorblind_mode = st.toggle("🎨 Colorblind-friendly mode", value=False)

    if colorblind_mode:
        chosen_scale = "Viridis" if map_metric != "Financial_Stress" else "Viridis_r"
    else:
        chosen_scale = "RdYlGn" if map_metric != "Financial_Stress" else "RdYlGn_r"

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
            "Danceability": ":.3f",
            "Cost_of_Living": ":.1f",
            "Purchasing_Power": ":.1f"
        },
        color_continuous_scale=chosen_scale,
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
    st.subheader("Explore a specific country - dive into its local vibes & global connections")

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
    # c1 - Music Mood
    with c1:
        st.metric("🎸 Music Mood", f"{selected_country['Music_Mood']:.3f}")
        st.caption("higher = more uplifting, positive, energetic")

    # c2 - Valence
    with c2:
        st.metric("😊 Valence", f"{selected_country['Valence']:.3f}")
        st.caption("higher = happier and more positive music")

    # c3 - Energy
    with c3:
        st.metric("⚡ Energy", f"{selected_country['Energy']:.3f}")
        st.caption("higher = more intense and active music")

    # c4 - Financial Stress
    with c4:
        st.metric("💸 Financial Stress", f"{selected_country['Financial_Stress']:.2f}")
        st.caption("higher = more struggle to provide basic needs")

    # c5 - Purchasing Power
    with c5:
        st.metric("💰 Purchasing Power", f"{selected_country['Purchasing_Power']:.1f}")
        st.caption("higher = more wealth to buy goods and services")

    st.divider()

    table_mode = st.radio(
        "Explore top 10 most & least similar countries by:",
        ["🎶 Music vibe (Music Distance)", "🔀 Shared songs (Jaccard Similarity)", "👥 Social connection (SCI)"],
        horizontal=True
    )

    col_left, col_right = st.columns(2)

    if table_mode == "🎶 Music vibe (Music Distance)":
        sort_col = 'Music_Distance'
        display_cols = ['Other_Name', 'Music_Distance', 'Jaccard_Similarity_Songs', 'SCI_Score_normalized']
        col_labels = ['Country', 'Music Distance', 'Jaccard', 'SCI']
        left_label = 'Most similar vibe'
        right_label = 'Most different vibe'
        best = pairs.nsmallest(10, sort_col)
        worst = pairs.nlargest(10, sort_col)
    elif table_mode == "🔀 Shared songs (Jaccard Similarity)":
        sort_col = 'Jaccard_Similarity_Songs'
        display_cols = ['Other_Name', 'Jaccard_Similarity_Songs', 'Music_Distance', 'SCI_Score_normalized']
        col_labels = ['Country', 'Jaccard', 'Music Distance', 'SCI']
        left_label = 'Most top 50 songs in common'
        right_label = 'Least song overlap'
        best = pairs.nlargest(10, sort_col)
        worst = pairs.nsmallest(10, sort_col)
    else:
        sort_col = 'SCI_Score_normalized'
        display_cols = ['Other_Name', 'SCI_Score_normalized', 'Music_Distance', 'Jaccard_Similarity_Songs']
        col_labels = ['Country', 'SCI', 'Music Distance', 'Jaccard']
        left_label = 'Most connected'
        right_label = 'Least connected'
        best = pairs.nlargest(10, sort_col)
        worst = pairs.nsmallest(10, sort_col)

    with col_left:
        st.markdown(f"#### {left_label}")
        top_df = best[display_cols].copy()
        top_df.columns = col_labels
        top_df = top_df.reset_index(drop=True)
        top_df.index += 1
        st.dataframe(top_df.style.format({k: '{:.4f}' for k in col_labels[1:]}), use_container_width=True)

    with col_right:
        st.markdown(f"#### {right_label}")
        bot_df = worst[display_cols].copy()
        bot_df.columns = col_labels
        bot_df = bot_df.reset_index(drop=True)
        bot_df.index += 1
        st.dataframe(bot_df.style.format({k: '{:.4f}' for k in col_labels[1:]}), use_container_width=True)

    # --- ENHANCED MAP SECTION WITH TOGGLE ---
    st.markdown(f"#### 🗺️ Map Explorer: {COUNTRY_NAMES.get(selected_code, selected_code)}")
    
    map_mode = st.radio(
        "Color countries by:",
        ["🎶 Music vibe (Music Distance)", "🔀 Shared songs (Jaccard Similarity)", "👥 Social connection (SCI)"],
        horizontal=True
    )

    if "Jaccard" in map_mode:
        metric_col = 'Jaccard_Similarity_Songs'
        color_scale = 'Viridis_r' if colorblind_mode else 'Blues'
        hover_label = 'Jaccard Similarity'
    elif "SCI" in map_mode:
        metric_col = 'SCI_Score_normalized'
        color_scale = 'Viridis' if colorblind_mode else 'Mint'
        hover_label = 'Social Connectedness'
    else:
        metric_col = 'Music_Distance'
        color_scale = 'Viridis' if colorblind_mode else 'Purples_r'
        hover_label = 'Music Distance'

    # if "Jaccard" in map_mode:
    #     metric_col = 'Jaccard_Similarity_Songs'
    #     color_scale = 'Blues'  
    #     hover_label = 'Jaccard Similarity'
    # elif "SCI" in map_mode:
    #     metric_col = 'SCI_Score_normalized'
    #     color_scale = 'Mint'
    #     hover_label = 'Social Connectedness'
    # else:
    #     metric_col = 'Music_Distance'
    #     color_scale = 'Purples_r'
    #     hover_label = 'Music Distance'

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
        colorscale=[[0, '#FF6600'], [1, '#FF6600']],
        showscale=False,
        hovertemplate=f"<b>{COUNTRY_NAMES.get(selected_code, selected_code)}</b><br>Selected<extra></extra>"
    ))

    # To ustawienie sprawi, że kraje bez danych będą jasnoszare
    fig_highlight.update_geos(
        showcountries=True,
        countrycolor="white",
        showland=True,
        landcolor="#E5E5E5", 
        coastlinecolor="white",
    )

    fig_highlight.update_layout(
        height=750,
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(title=hover_label)
    )

    st.plotly_chart(fig_highlight, use_container_width=True)

    # Scatter: all pairs for this country
    pairs['Other_Name_Full'] = pairs['Other'].map(COUNTRY_NAMES).fillna(pairs['Other'])

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("##### How similar is your chosen country's music vibe to other countries?")
        st.write(":grey[*Lower score = Higher similarity*]") # Styled muted/italic text
        fig_scatter = px.scatter(
            pairs,
            x='SCI_Score_normalized',
            y='Music_Distance',
            hover_name='Other_Name_Full',
            color='Music_Distance', # Kolor pasuje do osi Y
            color_continuous_scale='Viridis_r' if colorblind_mode else 'Purples_r',
            range_color=[pairs['Music_Distance'].min(), pairs['Music_Distance'].max() + 0.1],
            labels={
                'SCI_Score_normalized': 'Social Connection Strength',
                'Music_Distance': 'Music vibe similarity',
            },
            title=f"Music vibe similarity: {COUNTRY_NAMES.get(selected_code, selected_code)}"
        )
        fig_scatter.update_layout(height=400)
        fig_scatter.update_layout(
            height=400,
            hovermode="x",
            coloraxis_colorbar=dict(
                tickvals=[0, 0.1, 0.2, 0.3],
                ticktext=["0", "0.1", "0.2", "0.3"]
            )
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.markdown("""
        <div style="font-size: 16px; line-height: 1.6;">
        • dots closer to the <b>bottom</b> = countries with more similar <b>music vibe</b><br>
        • dots closer to the <b>right</b> = countries more <b>socially connected</b><br>
        • <b>best match</b> = dot in the <b>bottom right</b> corner
        </div>
        """, unsafe_allow_html=True)                                                                                                                                                                  

    with col_s2: 
        st.markdown("##### How many top 50 songs does your chosen country share with other countries?")
        st.write(":grey[*Higher score = Higher similarity*]") # Styled muted/italic text
        fig_scatter2 = px.scatter(
            pairs,
            x='SCI_Score_normalized',
            y='Jaccard_Similarity_Songs',
            hover_name='Other_Name_Full',
            color='Jaccard_Similarity_Songs', # Kolor pasuje do osi Y
            color_continuous_scale='Viridis' if colorblind_mode else 'Blues',
            range_color=[-0.1, pairs['Jaccard_Similarity_Songs'].max()],
            labels={
                'SCI_Score_normalized': 'Social Connection Strength',
                'Jaccard_Similarity_Songs': '% of Shared Songs',
            },
            title=f"% of Shared Songs: {COUNTRY_NAMES.get(selected_code, selected_code)}"
        )
        fig_scatter2.update_layout(height=400)
        fig_scatter2.update_layout(
            height=400,
            hovermode="x",
            coloraxis_colorbar=dict(
                tickvals=[0, 0.05, 0.1, 0.15],
                ticktext=["0%", "5%", "10%", "15%"] # Dodałem %, żeby było czytelniej
            )
        )
        st.plotly_chart(fig_scatter2, use_container_width=True)
        st.markdown("""
        <div style="font-size: 16px; line-height: 1.6;">
        • dots closer to the <b>top</b> = countries with more <b>songs in common</b><br>
        • dots closer to the <b>right</b> = countries more <b>socially connected</b><br>
        • <b>best match</b> = dot in the <b>top right</b> corner
        </div>
        """, unsafe_allow_html=True)                                                                                                              
# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CORRELATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("📊 What actually drives music similarity between countries?")
    st.markdown("""
    <div style="font-size: 16px; line-height: 1.6;">
        Two competing ideas: maybe countries listen to similar music because they're <b>socially connected</b> – 
        sharing songs through social media. Or maybe it's about <b>money</b> – richer or poorer countries develop 
        different musical tastes. Let's see what the data actually says.
        <br>
        • <b>Each dot</b> on the charts below represents a country pair (purple and blue plots) or a single country (red plot).<br>
        • <b>Hover over dots</b> to see specific country names or pairs they represent.<br>
        • <b>Hover over the line (trendline)</b> to see detailed statistics explained below. <i>Note: details are most visible when hovering near data points.</i><br>
        • <b>To zoom in</b>, click and drag your cursor over a specific area. <b>Double-click</b> anywhere on the graph to reset the view.
    </div>
    <div style="margin-bottom: 30px;"></div>
    """, unsafe_allow_html=True)

    with st.expander("🤓 How to read the statistics? (Correlation, r-value and trendline)"):
        st.markdown("""
        **What is 'r' (Correlation Coefficient)?**  
        It measures how much two things move together. For example, if stress in a country grows, so does the energy of the music - people listen to more energetic music. It does not have to mean that one influences the other though.
        
        *   **r = 1.0**: Perfect match (when one goes up, the other goes up exactly the same).
        *   **r = 0**: No connection at all (complete chaos).
        *   **r = -1.0**: Perfect opposite (when one goes up, the other goes down exactly opposite).

        **The 3 Key Findings:**
        1.  **Shared Hits (r = 0.54) → Strong Connection:** This is the strongest result. Social media and internet friendships are incredibly effective at spreading *specific* songs (the same top 50 hits) across borders.
        2.  **Music Vibe (r = -0.33) → Moderate Connection:** Social ties do influence the *general mood* of music people like, but less than specific hits. It's a piece of the puzzle, but not the whole story.
        3.  **Economic Pressure (r = 0.24) → Weak/No Connection:** Surprisingly, wealth doesn't dictate music taste. Whether a country is rich or poor has almost no impact on the 'mood' of its music. Local culture matters more than money.
                    
        **What do those technical terms in the pop-up when hovering over the graph (trend) line mean?**

        *   **OLS Trendline (The Line):** This is the 'best-fit' line. It shows the general direction of the data. If it goes up, the relationship is positive; if it goes down, it's negative.
        *   **R-Squared ($R^2$):** This tells us how much of the variation is actually explained by the trend. 
            *   **$R^2 = 0.29$ (Shared Songs):** High. Social ties explain nearly 30% of why countries share the same hits.
            *   **$R^2 = 0.05$ (Economic Pressure):** Very low. It confirms that money has almost nothing to do with music mood.
            *   **$R^2 = 0.11$ (Music Vibe):** Moderate-Low. Social ties explain about 11% of the differences in musical mood between countries."
        *   **The Equation (e.g., $y = ax + b$):** This is just the mathematical formula for the line. For every step you move right on the 'Social' (x - horizontal) axis, it tells you exactly how much the 'Music' value is expected to change (y - vertical axis).
        """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Do socially connected countries listen to music with a similar vibe?")
        st.write(":grey[*Each dot = one country pair. Right = more connected. Down = more similar music vibe.*]")
        fig1 = px.scatter(
            df, x='SCI_Score_normalized', y='Music_Distance',
            opacity=0.4,
            trendline='ols',
            labels={'SCI_Score_normalized': 'SCI Normalized', 'Music_Distance': 'Music Distance'},
            color_discrete_sequence=['#009E73'] if colorblind_mode else ['#9b59b6']
        )
        fig1.update_layout(height=380)
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("There's a real pattern here: countries with **stronger Facebook friendships** do tend to have a **more similar music vibe**. But the dots are quite spread out - social connection is only one piece of the puzzle, not the whole story. r = −0.33")

    with col2:
        st.markdown("#### Do socially connected countries share the same specific songs?")
        st.write(":grey[*Each dot = one country pair. Right = more connected. Up = more songs in common.*]")
        fig2 = px.scatter(
            df, x='SCI_Score_normalized', y='Jaccard_Similarity_Songs',
            opacity=0.4,
            trendline='ols',
            labels={'SCI_Score_normalized': 'SCI Normalized', 'Jaccard_Similarity_Songs': 'Jaccard Songs'},
            color_discrete_sequence=['#0077BB'] if colorblind_mode else ['#3498db']
        )
        fig2.update_layout(height=380)
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("This is the **clearest finding** (dots are more dense around the line): **socially connected countries** are much more likely to **share the same viral hits in their top 50**. Social media spreads specific songs across borders far more effectively than it shapes overall musical mood. r = 0.54")
    st.divider()
    st.markdown("#### Does economic pressure change the kind of music a country listens to?")
    st.write(":grey[*Each dot = one country. Right = higher financial stress. Up = more uplifting music.*]")
    fig3 = px.scatter(
        country_df, x='Financial_Stress', y='Music_Mood',
        hover_name='Name', trendline='ols',
        labels={'Financial_Stress': 'Financial Stress', 'Music_Mood': 'Music Mood'},
        color_discrete_sequence=['#CC6677'] if colorblind_mode else ['#e74c3c']
    )
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("Surprisingly, **whether a country is rich or poor** has almost **no effect on the music mood** people prefer. The dots are all over the place - no clear pattern. Local culture, language, and history appear to matter far more than economics when it comes to musical identity. r = 0.24")

st.divider()
st.markdown("### 🎯 Key takeaways")
st.success(
    "**1. Social connections shape which songs go viral across borders.**  \n"
    "Countries with strong Facebook ties are far more likely to share the same specific hits - "
    "social media is the engine behind global music trends."
)
st.warning(
    "**2. Local musical identity survives.**  \n"
    "Even highly connected countries don't always sound alike. The emotional vibe of a country's music - "
    "whether it's upbeat, melancholic, or energetic - stays rooted in local culture."
)
st.info(
    "**3. Money doesn't buy musical taste.**  \n"
    "Whether a country is wealthy or struggling economically has almost no consistent effect on "
    "what kind of music people prefer. Culture wins over economics."
)

st.divider()
st.caption("Data: Facebook SCI (Meta AI) · Spotify Top 50 (Kaggle) · Cost of Living (Numbeo) | Technical Communication - Maja Rzeszotarska")
