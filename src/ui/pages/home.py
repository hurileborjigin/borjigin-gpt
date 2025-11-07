# src/ui/pages/home.py
import streamlit as st
from src.ui.utils import init_session_state

def render_home():
    """Render the home page"""
    init_session_state()
    
    # Hero Section
    st.title("🎯 Welcome to Interview Prep AI")
    st.markdown("### Your AI-Powered Interview Coach")
    
    st.markdown("""
    Prepare for your dream job with an intelligent agent that:
    - 🔍 Researches companies and generates tailored questions
    - 💪 Helps you practice with self-improving answers
    - 🎭 Simulates realistic mock interviews
    - 📊 Tracks your progress and provides insights
    """)
    
    st.markdown("---")
    
    # Getting Started
    st.header("🚀 Getting Started")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 1️⃣ Setup Profile")
        st.markdown("""
        Upload your CV, add experiences, and set your personality profile.
        """)
        if st.button("📋 Go to Profile Setup", key="home_profile"):
            st.session_state.current_mode = "profile"
            st.rerun()
    
    with col2:
        st.markdown("### 2️⃣ Prepare")
        st.markdown("""
        Research a company and generate mock interview questions.
        """)
        if st.button("🔍 Start Preparation", key="home_prep"):
            st.session_state.current_mode = "preparation"
            st.rerun()
    
    with col3:
        st.markdown("### 3️⃣ Practice")
        st.markdown("""
        Practice questions and get AI-powered feedback.
        """)
        if st.button("💪 Start Practice", key="home_practice"):
            st.session_state.current_mode = "practice"
            st.rerun()
    
    st.markdown("---")
    
    # Features
    st.header("✨ Key Features")
    
    features = [
        {
            "icon": "🔄",
            "title": "Self-Critique & Iteration",
            "description": "Answers improve automatically through multiple iterations until they meet quality standards."
        },
        {
            "icon": "🔍",
            "title": "Company Research",
            "description": "Automatic web research to understand company culture, values, and recent news."
        },
        {
            "icon": "🎯",
            "title": "Tailored Questions",
            "description": "Mock questions generated specifically for your target company and role."
        },
        {
            "icon": "📚",
            "title": "Long-term Memory",
            "description": "Your CV and experiences are stored and retrieved contextually for every answer."
        },
        {
            "icon": "🔮",
            "title": "Follow-up Prediction",
            "description": "Predicts likely follow-up questions and helps you prepare responses."
        },
        {
            "icon": "📊",
            "title": "Analytics Dashboard",
            "description": "Track your progress, identify strengths, and get personalized recommendations."
        }
    ]
    
    cols = st.columns(2)
    
    for i, feature in enumerate(features):
        col = cols[i % 2]
        with col:
            st.markdown(f"### {feature['icon']} {feature['title']}")
            st.markdown(feature['description'])
            st.markdown("")
    
    st.markdown("---")
    
    # How It Works
    st.header("🔧 How It Works")
    
    st.markdown("""
    ### The Agent Workflow
    
    ```
    1. Question Analysis
       ↓
    2. Context Retrieval (CV, Experiences, Company Research)
       ↓
    3. Answer Generation
       ↓
    4. Self-Critique & Scoring
       ↓
    5. Iteration (if score < threshold)
       ↓
    6. Final Refinement
       ↓
    7. Key Points & Delivery Tips Extraction
       ↓
    8. Follow-up Prediction
    ```
    
    **Powered by:**
    - **LangGraph**: Agent orchestration with loops and conditionals
    - **Azure OpenAI**: GPT-4 for generation and critique
    - **ChromaDB**: Vector storage for semantic search
    - **Tavily**: Real-time web research
    """)
    
    st.markdown("---")
    
    # Quick Actions
    st.header("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Upload CV"):
            st.session_state.current_mode = "profile"
            st.rerun()
    
    with col2:
        if st.button("🎭 Mock Interview"):
            st.session_state.current_mode = "mock_interview"
            st.rerun()
    
    with col3:
        if st.button("📊 View Analytics"):
            st.session_state.current_mode = "analytics"
            st.rerun()
    
    with col4:
        if st.button("💾 Export Data"):
            session_data = st.session_state.orchestrator.export_session()
            if session_data:
                from src.ui.utils import export_to_json
                from datetime import datetime
                export_to_json(
                    session_data,
                    f"session_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
            else:
                st.info("No session data to export")
    
    st.markdown("---")
    
    # Tips
    st.header("💡 Pro Tips")
    
    tips = [
        "**Complete your profile first** - The more context the AI has, the better your answers will be.",
        "**Use real experiences** - The agent retrieves from your actual CV and experience library.",
        "**Review iterations** - See how answers improve through self-critique cycles.",
        "**Practice follow-ups** - Interviewers often dig deeper, so prepare for follow-up questions.",
        "**Track your progress** - Use the analytics dashboard to identify patterns and improve.",
        "**Export your work** - Download Q&As for offline review and practice."
    ]
    
    for tip in tips:
        st.markdown(f"- {tip}")
    
    st.markdown("---")
    
    # Status Check
    st.header("✅ System Status")
    
    col1, col2, col3 = st.columns(3)
    
    # Check if CV uploaded
    try:
        cv_results = st.session_state.orchestrator.long_term_memory.search("CV", k=1, filter_type="cv")
        cv_status = "✅ CV Uploaded" if cv_results else "⚠️ No CV"
    except:
        cv_status = "⚠️ No CV"
    
    # Check if experiences added
    try:
        exp_results = st.session_state.orchestrator.long_term_memory.search("experience", k=1, filter_type="experience")
        exp_status = "✅ Experiences Added" if exp_results else "⚠️ No Experiences"
    except:
        exp_status = "⚠️ No Experiences"
    
    # Check if session active
    session_context = st.session_state.orchestrator.get_session_context()
    session_status = "✅ Session Active" if session_context else "⚠️ No Session"
    
    col1.info(cv_status)
    col2.info(exp_status)
    col3.info(session_status)