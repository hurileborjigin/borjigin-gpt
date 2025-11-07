# src/ui/pages/practice_mode.py
import streamlit as st
from src.ui.utils import init_session_state, display_answer_section, display_question_analysis
import datetime

def render_practice_mode():
    """Render the practice mode page"""
    init_session_state()
    
    st.title("💪 Practice Mode")
    st.markdown("Practice answering interview questions with AI-powered feedback and iteration.")
    
    # Session Context (Optional)
    with st.expander("📋 Set Job Context (Optional but Recommended)"):
        col1, col2 = st.columns(2)
        
        with col1:
            context_company = st.text_input("Company Name", key="practice_company")
            context_position = st.text_input("Position", key="practice_position")
        
        with col2:
            use_context = st.checkbox("Use this context for answers", value=True)
        
        context_job_desc = st.text_area(
            "Job Description",
            height=150,
            key="practice_job_desc"
        )
        
        if st.button("💾 Save Context"):
            st.session_state.orchestrator.create_session(
                job_description=context_job_desc,
                company_name=context_company,
                position=context_position,
                mode="practice"
            )
            st.success("✅ Context saved for this session")
    
    st.markdown("---")
    
    # Question Input
    st.header("Ask a Question")
    
    question_source = st.radio(
        "Question source:",
        ["Enter manually", "Select from mock questions"]
    )
    
    question = None
    
    if question_source == "Enter manually":
        question = st.text_area(
            "Enter your interview question:",
            height=100,
            placeholder="e.g., Tell me about a time you faced a challenging technical problem..."
        )
    else:
        if st.session_state.mock_questions:
            question_options = [
                f"{q.get('type', 'Q').upper()}: {q.get('question', '')[:80]}..."
                for q in st.session_state.mock_questions
            ]
            
            selected_idx = st.selectbox(
                "Select a question:",
                range(len(question_options)),
                format_func=lambda i: question_options[i]
            )
            
            question = st.session_state.mock_questions[selected_idx].get('question', '')
            st.info(f"**Selected Question:** {question}")
        else:
            st.warning("No mock questions available. Go to Preparation Mode to generate questions first.")
    
    # Generate Answer Button
    generate_button = st.button(
        "✨ Generate Answer",
        type="primary",
        disabled=not question
    )
    
    # Process Question
    if generate_button and question:
        with st.spinner("🤔 Analyzing question and generating answer... This may take 30-60 seconds."):
            try:
                result = st.session_state.orchestrator.practice_question(
                    question=question,
                    use_session_context=use_context if question_source == "Enter manually" else True
                )
                
                # Store in session state
                st.session_state.last_result = result
                st.session_state.last_question = question
                
                st.success("✅ Answer generated!")
                
            except Exception as e:
                st.error(f"❌ Error generating answer: {e}")
                st.session_state.last_result = None
    
    # Display Results
    if hasattr(st.session_state, 'last_result') and st.session_state.last_result:
        st.markdown("---")
        st.header("📝 Your Interview Answer")
        
        result = st.session_state.last_result
        
        # Question Analysis
        if result.get('question_analysis'):
            display_question_analysis(result['question_analysis'])
        
        # Answer Section
        display_answer_section(result)
        
        st.markdown("---")
        
        # Follow-up Section
        st.header("🔄 Practice Follow-up Questions")
        
        follow_up_question = st.text_input(
            "Ask a follow-up question (or use predicted ones above):",
            placeholder="e.g., What would you do differently next time?"
        )
        
        if st.button("Generate Follow-up Answer", disabled=not follow_up_question):
            with st.spinner("Generating follow-up answer..."):
                try:
                    follow_up_result = st.session_state.orchestrator.practice_follow_up(
                        follow_up_question=follow_up_question
                    )
                    
                    st.success("✅ Follow-up answer generated!")
                    
                    st.markdown("### Follow-up Answer")
                    st.markdown(follow_up_result.get('answer', ''))
                    
                    # Show scores
                    if follow_up_result.get('critique_scores'):
                        from src.ui.utils import display_score_card
                        scores = follow_up_result['critique_scores'].get('scores', {})
                        scores['overall'] = follow_up_result['critique_scores'].get('overall', 0)
                        display_score_card(scores, "Follow-up Answer Quality")
                
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        
        st.markdown("---")
        
        # Export
        st.header("💾 Export")
        
        if st.button("📥 Export This Q&A"):
            from src.ui.utils import export_to_json
            export_data = {
                "question": st.session_state.last_question,
                "answer": result.get('answer', ''),
                "scores": result.get('critique_scores', {}),
                "key_points": result.get('key_points', []),
                "delivery_tips": result.get('delivery_tips', []),
                "follow_ups": result.get('follow_up_questions', []),
                "timestamp": datetime.now().isoformat()
            }
            export_to_json(export_data, f"practice_qa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    
    # Conversation History
    if st.session_state.conversation_history:
        st.markdown("---")
        st.header("📜 Practice History")
        
        with st.expander("View All Practice Sessions"):
            for i, conv in enumerate(st.session_state.conversation_history, 1):
                st.markdown(f"### Session {i}")
                st.markdown(f"**Q:** {conv.get('question', '')}")
                st.markdown(f"**A:** {conv.get('answer', '')[:200]}...")
                st.markdown("---")