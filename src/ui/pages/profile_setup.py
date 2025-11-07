# src/ui/pages/profile_setup.py
import streamlit as st
from src.utils.document_parser import DocumentParser
from src.ui.utils import init_session_state
from typing import Optional
import tempfile
import os
import datetime

def render_profile_setup():
    """Render the profile setup page"""
    init_session_state()
    
    st.title("📋 Profile Setup")
    st.markdown("Build your interview preparation profile by adding your CV, experiences, and personality traits.")
    
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📄 CV Upload",
        "💼 Experience Library",
        "🎭 Personality Profile",
        "🗂️ Data Management"
    ])
    
    with tab1:
        render_cv_upload()
    
    with tab2:
        render_experience_library()
    
    with tab3:
        render_personality_profile()
    
    with tab4:
        render_data_management()

def render_cv_upload():
    """Render CV upload section"""
    st.header("Upload Your CV")
    
    upload_method = st.radio(
        "Choose upload method:",
        ["Upload File (PDF/DOCX/TXT)", "Paste Text Directly"]
    )
    
    cv_text = None
    
    if upload_method == "Upload File (PDF/DOCX/TXT)":
        uploaded_file = st.file_uploader(
            "Choose your CV file",
            type=['pdf', 'docx', 'txt'],
            help="Upload your CV in PDF, DOCX, or TXT format"
        )
        
        if uploaded_file is not None:
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            try:
                cv_text = DocumentParser.parse_document(tmp_path)
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
                with st.expander("Preview extracted text"):
                    st.text_area("CV Content", cv_text, height=300, disabled=True)
            except Exception as e:
                st.error(f"❌ Error parsing file: {e}")
            finally:
                os.unlink(tmp_path)
    
    else:
        cv_text = st.text_area(
            "Paste your CV text here:",
            height=300,
            placeholder="Paste your CV content here..."
        )
    
    # Metadata
    st.subheader("Additional Information (Optional)")
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name")
        email = st.text_input("Email")
    
    with col2:
        phone = st.text_input("Phone")
        linkedin = st.text_input("LinkedIn URL")
    
    # Save button
    if st.button("💾 Save CV to Profile", type="primary", disabled=not cv_text):
        metadata = {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin
        }
        
        with st.spinner("Saving CV to long-term memory..."):
            st.session_state.orchestrator.add_cv(cv_text, metadata)
        
        st.success("✅ CV saved successfully!")
        st.balloons()

def render_experience_library():
    """Render experience library section"""
    st.header("Experience Library")
    st.markdown("Add your professional experiences using the STAR framework for better interview answers.")
    
    # Add new experience
    with st.expander("➕ Add New Experience", expanded=True):
        st.subheader("STAR Framework Guide")
        st.markdown("""
        - **Situation**: Set the context (1-2 sentences)
        - **Task**: Describe the challenge or goal (1-2 sentences)
        - **Action**: Explain what YOU did specifically (2-3 sentences)
        - **Result**: Share the outcome with metrics if possible (1-2 sentences)
        """)
        
        experience_title = st.text_input("Experience Title", placeholder="e.g., Led migration to microservices")
        
        col1, col2 = st.columns(2)
        with col1:
            situation = st.text_area("Situation", height=100, placeholder="Describe the context...")
        with col2:
            task = st.text_area("Task", height=100, placeholder="What was the challenge?")
        
        col3, col4 = st.columns(2)
        with col3:
            action = st.text_area("Action", height=100, placeholder="What did YOU do?")
        with col4:
            result = st.text_area("Result", height=100, placeholder="What was the outcome?")
        
        # Tags
        tags_input = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., leadership, python, cloud, problem-solving"
        )
        tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
        
        if st.button("💾 Save Experience", type="primary"):
            if all([situation, task, action, result]):
                # Format as STAR
                experience_text = f"""
**{experience_title}**

**Situation:** {situation}

**Task:** {task}

**Action:** {action}

**Result:** {result}
                """.strip()
                
                metadata = {
                    "title": experience_title,
                    "tags": tags,
                    "framework": "STAR"
                }
                
                with st.spinner("Saving experience..."):
                    st.session_state.orchestrator.add_experience(experience_text, metadata)
                
                st.success("✅ Experience saved!")
                st.balloons()
            else:
                st.error("❌ Please fill in all STAR fields")
    
    # View existing experiences
    st.subheader("📚 Your Experiences")
    
    try:
        experiences = st.session_state.orchestrator.long_term_memory.get_all_experiences()
        
        if experiences:
            st.info(f"Total experiences: {len(experiences)}")
            
            for i, exp in enumerate(experiences, 1):
                with st.expander(f"Experience {i}: {exp.metadata.get('title', 'Untitled')[:50]}..."):
                    st.markdown(exp.page_content)
                    
                    if exp.metadata.get('tags'):
                        st.markdown(f"**Tags:** {', '.join(exp.metadata['tags'])}")
        else:
            st.info("No experiences added yet. Add your first experience above!")
    
    except Exception as e:
        st.warning("Unable to load experiences. Add some experiences to get started!")

def render_personality_profile():
    """Render personality profile section"""
    st.header("Personality Profile")
    st.markdown("Help the AI understand your communication style and work preferences.")
    
    # Communication Style
    st.subheader("Communication Style")
    comm_style = st.selectbox(
        "How would you describe your communication style?",
        [
            "Direct and concise",
            "Detailed and thorough",
            "Collaborative and inclusive",
            "Analytical and data-driven",
            "Creative and innovative"
        ]
    )
    
    # Work Values
    st.subheader("Work Values")
    work_values = st.multiselect(
        "What do you value most in your work? (Select up to 5)",
        [
            "Innovation",
            "Collaboration",
            "Independence",
            "Growth",
            "Impact",
            "Work-life balance",
            "Leadership",
            "Technical excellence",
            "Mentorship",
            "Diversity"
        ],
        max_selections=5
    )
    
    # Strengths
    st.subheader("Strengths")
    strengths = st.multiselect(
        "What are your key strengths? (Select up to 5)",
        [
            "Problem-solving",
            "Leadership",
            "Technical skills",
            "Communication",
            "Creativity",
            "Analytical thinking",
            "Adaptability",
            "Team collaboration",
            "Project management",
            "Strategic thinking"
        ],
        max_selections=5
    )
    
    # Areas for Improvement
    st.subheader("Areas for Improvement")
    weaknesses = st.multiselect(
        "What areas are you working to improve? (Select up to 3)",
        [
            "Public speaking",
            "Delegation",
            "Time management",
            "Saying no",
            "Technical depth in specific areas",
            "Patience",
            "Detail orientation",
            "Big picture thinking",
            "Networking"
        ],
        max_selections=3
    )
    
    # Career Goals
    st.subheader("Career Goals")
    career_goals = st.text_area(
        "What are your career goals for the next 2-3 years?",
        height=150,
        placeholder="Describe your career aspirations..."
    )
    
    # Save button
    if st.button("💾 Save Personality Profile", type="primary"):
        personality_data = {
            "communication_style": comm_style,
            "work_values": work_values,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "career_goals": career_goals
        }
        
        with st.spinner("Saving personality profile..."):
            st.session_state.orchestrator.add_personality(personality_data)
        
        st.success("✅ Personality profile saved!")
        st.balloons()

def render_data_management():
    """Render data management section"""
    st.header("Data Management")
    
    st.warning("⚠️ These actions will permanently delete data from your profile.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear All CV Data", type="secondary"):
            if st.checkbox("I confirm I want to delete all CV data"):
                st.session_state.orchestrator.long_term_memory.delete_by_type("cv")
                st.success("CV data cleared")
    
    with col2:
        if st.button("🗑️ Clear All Experiences", type="secondary"):
            if st.checkbox("I confirm I want to delete all experiences"):
                st.session_state.orchestrator.long_term_memory.delete_by_type("experience")
                st.success("Experiences cleared")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear ALL Profile Data", type="secondary"):
        if st.checkbox("I confirm I want to delete EVERYTHING"):
            st.session_state.orchestrator.long_term_memory.clear_all()
            st.success("All profile data cleared")
            st.balloons()
    
    st.markdown("---")
    
    # Export data
    st.subheader("Export Data")
    if st.button("📥 Export Session Data"):
        session_data = st.session_state.orchestrator.export_session()
        if session_data:
            from src.ui.utils import export_to_json
            export_to_json(session_data, f"interview_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        else:
            st.info("No active session to export")