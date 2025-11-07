# src/ui/pages/mock_interview.py
import streamlit as st
from src.ui.utils import init_session_state, display_answer_section, display_progress_bar
import datetime

def render_mock_interview():
    """Render the mock interview mode page"""
    init_session_state()
    
    st.title("🎭 Mock Interview Mode")
    
    # Check if preparation is complete
    if not st.session_state.preparation_complete:
        st.warning("⚠️ Please complete Preparation Mode first to generate mock questions.")
        if st.button("Go to Preparation Mode"):
            st.session_state.current_mode = "preparation"
            st.rerun()
        return
    
    # Start Interview
    if not st.session_state.mock_interview_active:
        st.markdown("### Ready to start your mock interview?")
        
        total_questions = len(st.session_state.mock_questions)
        st.info(f"📊 **{total_questions} questions** prepared for you")
        
        st.markdown("""
        **How it works:**
        1. You'll be presented with one question at a time
        2. Click "Show Answer" to see the AI-generated response
        3. Review the answer, scores, and feedback
        4. Move to the next question when ready
        5. Get a performance summary at the end
        """)
        
        if st.button("🚀 Start Mock Interview", type="primary"):
            try:
                st.session_state.orchestrator.start_mock_interview()
                st.session_state.mock_interview_active = True
                st.session_state.current_question_index = 0
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error starting interview: {e}")
        
        return
    
    # Active Interview
    total_questions = len(st.session_state.mock_questions)
    current_idx = st.session_state.current_question_index
    
    # Progress
    display_progress_bar(current_idx + 1, total_questions, "Interview Progress")
    
    st.markdown("---")
    
    # Current Question
    if current_idx < total_questions:
        current_q = st.session_state.mock_questions[current_idx]
        
        st.header(f"Question {current_idx + 1} of {total_questions}")
        
        q_type = current_q.get('type', 'Unknown').title()
        q_difficulty = current_q.get('difficulty', 'Medium').title()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Type", q_type)
        col2.metric("Difficulty", q_difficulty)
        col3.metric("Framework", current_q.get('expected_framework', 'STAR'))
        
        st.markdown("---")
        
        # Display Question
        st.markdown("### 💬 Interview Question")
        st.info(current_q.get('question', ''))
        
        # Themes
        themes = current_q.get('themes', [])
        if themes:
            st.markdown(f"**Focus areas:** {', '.join(themes)}")
        
        st.markdown("---")
        
        # Show Answer Button
        if 'current_mock_answer' not in st.session_state or st.session_state.get('current_mock_question_idx') != current_idx:
            if st.button("🎯 Show AI Answer", type="primary"):
                with st.spinner("Generating your answer..."):
                    try:
                        result = st.session_state.orchestrator.answer_mock_question()
                        st.session_state.current_mock_answer = result
                        st.session_state.current_mock_question_idx = current_idx
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        
        # Display Answer
        if hasattr(st.session_state, 'current_mock_answer') and st.session_state.get('current_mock_question_idx') == current_idx:
            display_answer_section(st.session_state.current_mock_answer)
            
            st.markdown("---")
            
            # Navigation
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if current_idx > 0:
                    if st.button("⬅️ Previous Question"):
                        st.session_state.current_question_index -= 1
                        if 'current_mock_answer' in st.session_state:
                            del st.session_state.current_mock_answer
                        st.rerun()
            
            with col2:
                if st.button("🔄 Regenerate Answer"):
                    if 'current_mock_answer' in st.session_state:
                        del st.session_state.current_mock_answer
                    st.rerun()
            
            with col3:
                if current_idx < total_questions - 1:
                    if st.button("Next Question ➡️", type="primary"):
                        st.session_state.current_question_index += 1
                        if 'current_mock_answer' in st.session_state:
                            del st.session_state.current_mock_answer
                        st.rerun()
                else:
                    if st.button("🏁 Finish Interview", type="primary"):
                        st.session_state.mock_interview_active = False
                        st.session_state.interview_completed = True
                        st.rerun()
    
    # Interview Completed
    elif hasattr(st.session_state, 'interview_completed') and st.session_state.interview_completed:
        st.success("🎉 Mock Interview Completed!")
        
        # Get summary
        summary = st.session_state.orchestrator.get_mock_interview_summary()
        
        st.header("📊 Performance Summary")
        
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Questions Answered", summary.get('questions_answered', 0))
        col2.metric("Average Score", f"{summary.get('average_score', 0):.1f}/10")
        col3.metric("Final Difficulty", summary.get('difficulty_progression', 'Medium').title())
        
        # Score progression
        st.markdown("### 📈 Score Progression")
        scores = summary.get('scores_by_question', [])
        if scores:
            import pandas as pd
            df = pd.DataFrame({
                'Question': range(1, len(scores) + 1),
                'Score': scores
            })
            st.line_chart(df.set_index('Question'))
        
        # Performance breakdown
        st.markdown("### 🎯 Performance Breakdown")
        
        if scores:
            avg = sum(scores) / len(scores)
            
            if avg >= 8:
                st.success("🌟 Excellent performance! You're well-prepared.")
            elif avg >= 6:
                st.info("👍 Good performance! A bit more practice will make you interview-ready.")
            else:
                st.warning("💪 Keep practicing! Focus on the improvement areas highlighted in each answer.")
        
        # Actions
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Start New Mock Interview"):
                st.session_state.mock_interview_active = False
                st.session_state.interview_completed = False
                st.session_state.current_question_index = 0
                if 'current_mock_answer' in st.session_state:
                    del st.session_state.current_mock_answer
                st.rerun()
        
        with col2:
            if st.button("📥 Export Results"):
                from src.ui.utils import export_to_json
                export_to_json(summary, f"mock_interview_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")