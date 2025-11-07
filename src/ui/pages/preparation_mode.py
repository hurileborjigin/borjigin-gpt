# src/ui/pages/preparation_mode.py
import streamlit as st
from src.ui.utils import init_session_state, display_progress_bar
from datetime import datetime

def render_preparation_mode():
    """Render the preparation mode page"""
    init_session_state()
    
    st.title("🔍 Preparation Mode")
    st.markdown("Research the company and generate mock interview questions tailored to the role.")
    
    # Job Details Input
    with st.container():
        st.header("Job Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name *",
                placeholder="e.g., Google, Microsoft, Amazon"
            )
            position = st.text_input(
                "Position Title *",
                placeholder="e.g., Senior Software Engineer"
            )
        
        with col2:
            application_deadline = st.date_input("Application Deadline (Optional)")
            force_refresh = st.checkbox(
                "Force new research (ignore cache)",
                help="Check this to perform fresh research even if cached data exists"
            )
        
        job_description = st.text_area(
            "Job Description *",
            height=200,
            placeholder="Paste the full job description here..."
        )
        
        start_research = st.button(
            "🚀 Start Research & Generate Questions",
            type="primary",
            disabled=not all([company_name, position, job_description])
        )
    
    # Research Results
    if start_research:
        with st.spinner("🔍 Researching company and generating questions... This may take 1-2 minutes."):
            try:
                result = st.session_state.orchestrator.prepare_for_interview(
                    company_name=company_name,
                    position=position,
                    job_description=job_description,
                    force_refresh=force_refresh
                )
                
                st.session_state.preparation_complete = True
                st.session_state.mock_questions = result["questions"]
                st.session_state.research_data = result["research_data"]
                
                st.success("✅ Research complete! Mock interview ready.")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error during preparation: {e}")
                st.session_state.preparation_complete = False
    
    # Display Results
    if st.session_state.preparation_complete:
        st.markdown("---")
        
        # Research Summary
        st.header("📊 Research Summary")
        
        research_tabs = st.tabs([
            "🏢 Company Overview",
            "🎨 Company Culture",
            "📰 Recent News",
            "💼 Position Analysis"
        ])
        
        research_data = st.session_state.get('research_data', {})
        
        with research_tabs[0]:
            st.markdown("### Company Overview")
            overview = research_data.get('overview', 'No data available')
            st.markdown(overview)
        
        with research_tabs[1]:
            st.markdown("### Company Culture")
            culture = research_data.get('culture', 'No data available')
            st.markdown(culture)
        
        with research_tabs[2]:
            st.markdown("### Recent News")
            news = research_data.get('news', 'No data available')
            st.markdown(news)
        
        with research_tabs[3]:
            st.markdown("### Position Analysis")
            position_analysis = research_data.get('position_analysis', 'No data available')
            st.markdown(position_analysis)
        
        st.markdown("---")
        
        # Mock Questions
        st.header("💭 Generated Mock Interview Questions")
        
        questions = st.session_state.mock_questions
        
        if questions:
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            
            behavioral = sum(1 for q in questions if q.get('type') == 'behavioral')
            technical = sum(1 for q in questions if q.get('type') == 'technical')
            situational = sum(1 for q in questions if q.get('type') == 'situational')
            
            col1.metric("Total Questions", len(questions))
            col2.metric("Behavioral", behavioral)
            col3.metric("Technical", technical)
            col4.metric("Situational", situational)
            
            st.markdown("---")
            
            # Filter options
            filter_type = st.selectbox(
                "Filter by type:",
                ["All", "Behavioral", "Technical", "Situational"]
            )
            
            filter_difficulty = st.selectbox(
                "Filter by difficulty:",
                ["All", "Easy", "Medium", "Hard"]
            )
            
            # Display questions
            filtered_questions = questions
            
            if filter_type != "All":
                filtered_questions = [q for q in filtered_questions if q.get('type', '').lower() == filter_type.lower()]
            
            if filter_difficulty != "All":
                filtered_questions = [q for q in filtered_questions if q.get('difficulty', '').lower() == filter_difficulty.lower()]
            
            st.info(f"Showing {len(filtered_questions)} questions")
            
            for i, q in enumerate(filtered_questions, 1):
                q_type = q.get('type', 'Unknown').title()
                q_difficulty = q.get('difficulty', 'Medium').title()
                q_text = q.get('question', '')
                themes = q.get('themes', [])
                
                # Color coding
                type_color = {
                    'Behavioral': '🔵',
                    'Technical': '🟢',
                    'Situational': '🟡'
                }.get(q_type, '⚪')
                
                difficulty_emoji = {
                    'Easy': '⭐',
                    'Medium': '⭐⭐',
                    'Hard': '⭐⭐⭐'
                }.get(q_difficulty, '⭐⭐')
                
                with st.expander(f"{type_color} Q{i}: {q_text[:80]}... {difficulty_emoji}"):
                    st.markdown(f"**Question:** {q_text}")
                    st.markdown(f"**Type:** {q_type}")
                    st.markdown(f"**Difficulty:** {q_difficulty}")
                    if themes:
                        st.markdown(f"**Themes:** {', '.join(themes)}")
                    st.markdown(f"**Framework:** {q.get('expected_framework', 'STAR')}")
            
            st.markdown("---")
            
            # Start Mock Interview
            if st.button("🎭 Start Mock Interview", type="primary"):
                st.session_state.current_mode = "mock_interview"
                st.session_state.mock_interview_active = True
                st.session_state.current_question_index = 0
                st.rerun()
        
        else:
            st.warning("No questions generated. Try running the research again.")