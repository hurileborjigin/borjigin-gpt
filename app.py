# app.py
import streamlit as st
from src.ui.sidebar import render_sidebar
from src.ui.pages.home import render_home
from src.ui.pages.profile_setup import render_profile_setup
from src.ui.pages.preparation_mode import render_preparation_mode
from src.ui.pages.practice_mode import render_practice_mode
from src.ui.pages.mock_interview import render_mock_interview
from src.ui.pages.analytics import render_analytics
from src.ui.utils import init_session_state

# Page config
st.set_page_config(
    page_title="Interview Prep AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .stButton>button {
        width: 100%;
    }
    
    .stProgress > div > div > div > div {
        background-color: #FF6B6B;
    }
    
    h1 {
        color: #FF6B6B;
    }
    
    .stMetric {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    .stExpander {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar and get current mode
    current_mode = render_sidebar()
    
    # Route to appropriate page
    if current_mode == "home":
        render_home()
    elif current_mode == "profile":
        render_profile_setup()
    elif current_mode == "preparation":
        render_preparation_mode()
    elif current_mode == "practice":
        render_practice_mode()
    elif current_mode == "mock_interview":
        render_mock_interview()
    elif current_mode == "analytics":
        render_analytics()
    else:
        render_home()

if __name__ == "__main__":
    main()