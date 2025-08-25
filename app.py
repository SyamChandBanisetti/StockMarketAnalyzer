import streamlit as st
from utils.gemini_api import get_gemini_verdict

# --- Streamlit Setup ---
st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.markdown("""
<style>
.big-font {font-size:32px !important; font-weight:bold;}
.section-header {font-size:20px; color: #1F77B4; font-weight:bold; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 Stock Market Analyzer Dashboard</p>', unsafe_allow_html=True)

# --- 1️⃣ Company Name Input ---
st.markdown('<p class="section-header">Enter Company Name</p>', unsafe_allow_html=True)
company_name = st.text_input("Enter company name (e.g., Microsoft, Apple, Tesla):", "Apple")

if company_name:
    try:
        # --- Get Verdict & Insights directly from Gemini API ---
        verdict, confidence, insights = get_gemini_verdict(company_name)  # returns (str, float, str)

        # --- Display Recommendation ---
        st.markdown('<p class="section-header">💡 Recommendation & Insights</p>', unsafe_allow_html=True)
        color = "green" if verdict.upper() == "BUY" else "red" if verdict.upper() == "SELL" else "orange"
        st.markdown(f"<h3 style='color:{color};'>Recommendation: {verdict} (Confidence: {int(confidence*100)}%)</h3>", unsafe_allow_html=True)

        # --- Display Textual Insights ---
        if insights:
            st.markdown(f"**Insights:** {insights}")
        else:
            st.info("No additional insights available.")

    except Exception as e:
        st.error(f"Error fetching analysis: {e}")
