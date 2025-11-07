# src/agents/state.py
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """State for the interview prep agent"""
    
    # Messages
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Current question and context
    question: str
    question_analysis: Optional[Dict[str, Any]]
    
    # Retrieved context
    cv_context: Optional[str]
    experience_context: Optional[str]
    personality_context: Optional[str]
    company_context: Optional[str]
    
    # Answer generation
    current_answer: Optional[str]
    iteration_count: int
    
    # Critique and scoring
    critique_result: Optional[Dict[str, Any]]
    should_iterate: bool
    
    # Follow-ups
    follow_up_questions: Optional[List[Dict[str, Any]]]
    follow_up_depth: int
    
    # Session context
    job_description: Optional[str]
    company_name: Optional[str]
    position: Optional[str]
    research_data: Optional[Dict[str, Any]]
    mode: str  # "preparation", "practice", "mock_interview"
    
    # Output
    final_answer: Optional[str]
    key_points: Optional[List[str]]
    delivery_tips: Optional[List[str]]
    
    # Metadata
    error: Optional[str]