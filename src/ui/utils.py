# src/ui/utils.py
import streamlit as st
from typing import Dict, Any, List
import json
from datetime import datetime

def init_session_state():
    """Initialize Streamlit session state"""
    if 'orchestrator' not in st.session_state:
        from src.agents.orchestrator import InterviewPrepOrchestrator
        st.session_state.orchestrator = InterviewPrepOrchestrator()
    
    if 'current_mode' not in st.session_state:
        st.session_state.current_mode = "practice"
    
    if 'mock_interview_active' not in st.session_state:
        st.session_state.mock_interview_active = False
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    if 'preparation_complete' not in st.session_state:
        st.session_state.preparation_complete = False
    
    if 'mock_questions' not in st.session_state:
        st.session_state.mock_questions = []
    
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

def display_score_card(scores: Dict[str, float], title: str = "Answer Quality Scores"):
    """Display score card with visual indicators"""
    st.markdown(f"### {title}")
    
    cols = st.columns(3)
    
    score_items = [
        ("Authenticity", scores.get("authenticity", 0)),
        ("Relevance", scores.get("relevance", 0)),
        ("Structure", scores.get("structure", 0)),
        ("Specificity", scores.get("specificity", 0)),
        ("Impact", scores.get("impact", 0)),
        ("Length", scores.get("length", 0))
    ]
    
    for idx, (label, score) in enumerate(score_items):
        col = cols[idx % 3]
        with col:
            # Color based on score
            if score >= 8:
                color = "🟢"
            elif score >= 6:
                color = "🟡"
            else:
                color = "🔴"
            
            st.metric(
                label=label,
                value=f"{score:.1f}/10",
                delta=None
            )
            st.progress(score / 10)
    
    # Overall score
    overall = scores.get("overall", sum(s for _, s in score_items) / len(score_items))
    st.markdown("---")
    st.markdown(f"### Overall Score: **{overall:.1f}/10**")
    st.progress(overall / 10)

def display_answer_section(result: Dict[str, Any]):
    """Display complete answer section with all details"""
    
    # Main Answer
    st.markdown("### 💬 Your Answer")
    st.markdown(f"**Iterations:** {result.get('iterations', 0)}")
    
    with st.expander("📝 Full Answer", expanded=True):
        st.markdown(result.get("answer", ""))
    
    # Scores
    if result.get("critique_scores"):
        scores = result["critique_scores"].get("scores", {})
        scores["overall"] = result["critique_scores"].get("overall", 0)
        display_score_card(scores)
    
    # Key Points
    st.markdown("### 🎯 Key Points to Remember")
    key_points = result.get("key_points", [])
    if key_points:
        for point in key_points:
            st.markdown(f"- {point}")
    else:
        st.info("No key points extracted")
    
    # Delivery Tips
    st.markdown("### 💡 Delivery Tips")
    delivery_tips = result.get("delivery_tips", [])
    if delivery_tips:
        for tip in delivery_tips:
            st.markdown(f"- {tip}")
    else:
        st.info("No delivery tips available")
    
    # Strengths and Improvements
    if result.get("critique_scores"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ✅ Strengths")
            strengths = result["critique_scores"].get("strengths", [])
            for strength in strengths:
                st.success(strength)
        
        with col2:
            st.markdown("#### 🔧 Areas to Improve")
            improvements = result["critique_scores"].get("improvements", [])
            for improvement in improvements:
                st.warning(improvement)
    
    # Follow-up Questions
    st.markdown("### 🔮 Predicted Follow-up Questions")
    follow_ups = result.get("follow_up_questions", [])
    if follow_ups:
        for i, fu in enumerate(follow_ups, 1):
            with st.expander(f"Follow-up {i}: {fu.get('question', '')[:60]}..."):
                st.markdown(f"**Question:** {fu.get('question', '')}")
                st.markdown(f"**Why they might ask:** {fu.get('reason', '')}")
                st.markdown(f"**How to respond:** {fu.get('guidance', '')}")
    else:
        st.info("No follow-up questions predicted")

def display_question_analysis(analysis: Dict[str, Any]):
    """Display question analysis"""
    if not analysis:
        return
    
    st.markdown("### 🔍 Question Analysis")
    
    raw_analysis = analysis.get("raw_analysis", "")
    if raw_analysis:
        with st.expander("View Analysis", expanded=False):
            st.markdown(raw_analysis)

def format_conversation_message(role: str, content: str, timestamp: str = None):
    """Format a conversation message"""
    if role == "user":
        st.markdown(f"**You** ({timestamp or 'now'}):")
        st.info(content)
    else:
        st.markdown(f"**AI Coach** ({timestamp or 'now'}):")
        st.success(content)

def export_to_json(data: Dict[str, Any], filename: str):
    """Export data to JSON file"""
    json_str = json.dumps(data, indent=2)
    st.download_button(
        label="📥 Download as JSON",
        data=json_str,
        file_name=filename,
        mime="application/json"
    )

def display_progress_bar(current: int, total: int, label: str = "Progress"):
    """Display progress bar"""
    progress = current / total if total > 0 else 0
    st.progress(progress)
    st.caption(f"{label}: {current}/{total} ({progress*100:.0f}%)")