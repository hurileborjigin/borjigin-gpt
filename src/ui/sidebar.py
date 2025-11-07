# src/ui/sidebar.py
import streamlit as st
from src.ui.utils import init_session_state

def render_sidebar():
    """Render the sidebar navigation"""
    init_session_state()
    
    with st.sidebar:
        st.title("🎯 Interview Prep AI")
        st.markdown("---")
        
        # Mode Selection
        st.header("Navigation")
        
        mode = st.radio(
            "Select Mode:",
            [
                "🏠 Home",
                "📋 Profile Setup",
                "🔍 Preparation",
                "💪 Practice",
                "🎭 Mock Interview",
                "📊 Analytics"
            ],
            index=0
        )
        
        # Update current mode
        mode_map = {
            "🏠 Home": "home",
            "📋 Profile Setup": "profile",
            "🔍 Preparation": "preparation",
            "💪 Practice": "practice",
            "🎭 Mock Interview": "mock_interview",
            "📊 Analytics": "analytics"
        }
        
        st.session_state.current_mode = mode_map[mode]
        
        st.markdown("---")
        
        # Session Info
        st.header("Session Info")
        
        session_context = st.session_state.orchestrator.get_session_context()
        
        if session_context:
            company = session_context.get('company_name', 'Not set')
            position = session_context.get('position', 'Not set')
            mode_active = session_context.get('mode', 'None')
            
            st.info(f"**Company:** {company}")
            st.info(f"**Position:** {position}")
            st.info(f"**Mode:** {mode_active.title()}")
            
            if st.button("🗑️ Clear Session"):
                st.session_state.orchestrator.clear_session()
                st.success("Session cleared!")
                st.rerun()
        else:
            st.warning("No active session")
        
        st.markdown("---")
        
        # Quick Stats
        st.header("Quick Stats")
        
        performance = st.session_state.orchestrator.get_mock_interview_summary()
        
        if performance and performance.get('question_count', 0) > 0:
            st.metric("Questions Practiced", performance.get('question_count', 0))
            st.metric("Average Score", f"{performance.get('average_score', 0):.1f}/10")
            st.metric("Follow-ups", performance.get('follow_up_count', 0))
        else:
            st.info("Start practicing to see stats!")
        
        st.markdown("---")
        
        # Settings
        with st.expander("⚙️ Settings"):
            st.markdown("### Agent Settings")
            
            new_temp = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Higher = more creative, Lower = more focused"
            )
            
            new_iterations = st.slider(
                "Max Iterations",
                min_value=1,
                max_value=5,
                value=3,
                help="Maximum self-critique iterations"
            )
            
            new_threshold = st.slider(
                "Critique Threshold",
                min_value=5.0,
                max_value=9.0,
                value=7.0,
                step=0.5,
                help="Minimum score to stop iterating"
            )
            
            if st.button("💾 Save Settings"):
                from src.config.settings import settings
                settings.temperature = new_temp
                settings.max_iterations = new_iterations
                settings.critique_threshold = new_threshold
                st.success("Settings saved!")
        
        st.markdown("---")
        
        # About
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Interview Prep AI Agent**
            
            An agentic RAG system powered by:
            - LangGraph for agent orchestration
            - Azure OpenAI for LLM
            - ChromaDB for vector storage
            - Tavily for web research
            
            **Features:**
            - Self-critique with iteration
            - Company research
            - Mock interviews
            - Follow-up handling
            - Performance analytics
            
            Version: 1.0.0
            """)
        
        st.markdown("---")
        
        # Footer
        st.caption("Made with ❤️ using LangGraph & Streamlit")
    
    return st.session_state.current_mode