import streamlit as st
import pandas as pd
import feedparser
import os
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="HIIK Command Center", layout="wide", initial_sidebar_state="expanded")
st.title("🛰️ Advanced OSINT & Conflict Analysis Hub")
st.markdown("Monitoring regional defense dynamics, automated intelligence triage, and geopolitical shifts.")

# --- AUTOMATED NLP HEURISTIC ENGINE ---
# This function acts as a basic AI. It reads text and guesses the HIIK score based on keywords.
def auto_score_intelligence(text):
    text = str(text).lower()
    level_5_words = ['war', 'killed', 'strike', 'missile', 'offensive', 'airstrike', 'massacre', 'invasion']
    level_4_words = ['clash', 'artillery', 'troops', 'rebel', 'skirmish', 'gunfire', 'militia']
    level_3_words = ['protest', 'riot', 'tear gas', 'arrest', 'violence', 'clashes']
    level_2_words = ['threat', 'sanction', 'tension', 'deploy', 'warns', 'diplomatic', 'standoff']
    
    if any(word in text for word in level_5_words): return 5, "War"
    if any(word in text for word in level_4_words): return 4, "Limited War"
    if any(word in text for word in level_3_words): return 3, "Violent Crisis"
    if any(word in text for word in level_2_words): return 2, "Non-Violent Crisis"
    return 1, "Dispute"

# --- SIDEBAR: OSINT CONTROLS ---
st.sidebar.header("📡 OSINT Feed Controls")
st.sidebar.write("Select an intelligence source to monitor:")

# Dictionary of live RSS feeds
rss_feeds = {
    "🌍 BBC Global Top Stories": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "🌍 Al Jazeera Global": "https://www.aljazeera.com/xml/rss/all.xml",
    "🗺️ Asia Region": "http://feeds.bbci.co.uk/news/world/asia/rss.xml",
    "🗺️ Middle East Region": "http://feeds.bbci.co.uk/news/world/middle_east/rss.xml"
}

selected_feed = st.sidebar.selectbox("Select Network:", list(rss_feeds.keys()))
feed_url = rss_feeds[selected_feed]

st.sidebar.divider()
st.sidebar.header("Manual Override")
st.sidebar.write("Use sliders if automated NLP is incorrect.")
manual_intensity = st.sidebar.slider("Override HIIK Score", 1, 5, 1)

# --- TOP ROW: METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Status", "ONLINE", "Secure")
col2.metric("Active Feeds Monitored", len(rss_feeds))
col3.metric("Last Database Sync", "Today")
col4.metric("Threat Level", "Elevated", "-0.5", delta_color="inverse")

st.divider()

# --- MIDDLE ROW: MAP & ANALYTICS ---
map_col, chart_col = st.columns([2, 1]) # Map takes up 2/3 of the screen, chart takes 1/3

# Dummy Database for Map & Chart Visualization
map_data = pd.DataFrame({
    'Conflict Zone': ['Eastern Europe', 'Middle East', 'Sudan', 'Taiwan Strait', 'Myanmar', 'Sahel Region', 'Korean Peninsula'],
    'Lat': [48.3794, 31.5017, 15.5007, 23.6978, 21.9139, 13.5317, 38.3168],
    'Lon': [31.1656, 34.4668, 32.5599, 120.9605, 95.9562, 2.4604, 127.236],
    'HIIK Intensity': [5, 5, 4, 2, 4, 4, 1],
    'Actors': ['Russia vs Ukraine', 'Israel vs Hamas', 'SAF vs RSF', 'China vs Taiwan', 'Tatmadaw vs Resistance', 'State vs Insurgents', 'North vs South Korea']
})

with map_col:
    st.subheader("🌍 Global Conflict Map")
    fig_map = px.scatter_mapbox(
        map_data, lat="Lat", lon="Lon", hover_name="Conflict Zone", 
        hover_data=["HIIK Intensity", "Actors"], color="HIIK Intensity", 
        color_continuous_scale=px.colors.sequential.YlOrRd, size="HIIK Intensity", 
        zoom=1.2, height=450
    )
    fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with chart_col:
    st.subheader("📊 Global Conflict Distribution")
    # Count how many conflicts are at each intensity level
    intensity_counts = map_data['HIIK Intensity'].value_counts().reset_index()
    intensity_counts.columns = ['Level', 'Count']
    intensity_counts = intensity_counts.sort_values(by='Level')
    
    fig_bar = px.bar(
        intensity_counts, x='Level', y='Count', 
        color='Level', color_continuous_scale=px.colors.sequential.YlOrRd,
        height=450
    )
    fig_bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# --- BOTTOM ROW: LIVE AUTOMATED OSINT ---
st.subheader(f"🔴 Live Feed: {selected_feed}")

# Fetch Data
feed = feedparser.parse(feed_url)
live_data = []

# Process Data with the NLP Engine
for entry in feed.entries[:12]:
    # Pass the headline to our automated scorer
    auto_score, classification = auto_score_intelligence(entry.title)
    
    live_data.append({
        "Published": entry.published,
        "Auto-HIIK Level": auto_score,
        "Classification": classification,
        "Headline": entry.title,
        "Link": entry.link
    })

if live_data:
    df_osint = pd.DataFrame(live_data)
    
    # We highlight high-intensity rows using Pandas styling!
    def highlight_high_intensity(val):
        if val == 5: return 'background-color: darkred'
        elif val == 4: return 'background-color: darkorange'
        return ''
    
    styled_df = df_osint.style.map(highlight_high_intensity, subset=['Auto-HIIK Level'])
    st.dataframe(styled_df, use_container_width=True)
    
    # --- EXCEL CONNECTION ---
    st.write("Format and save these processed reports into your local 2026 Excel timeline.")
    if st.button("💾 Save Processed Feed to Excel"):
        excel_filename = "Timeline_2026.xlsx"
        formatted_for_excel = []
        for index, row in df_osint.iterrows():
            formatted_for_excel.append({
                "Date": row["Published"],          
                "Incident / Event": row["Headline"], 
                "Location (City/District)": "", 
                "Actors involved (BNP, Jamaat, AL, Police, etc)": "", 
                "Details of the Event (Injuries, Arrests, Clashes)": f"Auto-Scored Intensity: Level {row['Auto-HIIK Level']} ({row['Classification']})",
                "Sources / Links": row["Link"]        
            })
            
        new_data_df = pd.DataFrame(formatted_for_excel)
        try:
            if os.path.exists(excel_filename):
                existing_df = pd.read_excel(excel_filename)
                updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)
            else:
                updated_df = new_data_df
            updated_df.to_excel(excel_filename, index=False)
            st.success(f"Successfully added {len(new_data_df)} auto-scored reports to {excel_filename}!")
        except Exception as e:
            st.error(f"Error saving to Excel. Is the file closed? Error: {e}")
else:
    st.error("Could not fetch live data. Please check your internet connection or try another feed.")