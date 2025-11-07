# src/memory/short_term_memory.py
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class InterviewMode(str, Enum):
    PREPARATION = "preparation"
    PRACTICE = "practice"
    MOCK_INTERVIEW = "mock_interview"

class MockInterviewSession(BaseModel):
    generated_questions: List[Dict[str, Any]] = Field(default_factory=list)
    current_question_index: int = 0
    difficulty_level: str = "medium"
    performance_scores: List[float] = Field(default_factory=list)
    
class PracticeSession(BaseModel):
    questions_asked: List[str] = Field(default_factory=list)
    answers_given: List[str] = Field(default_factory=list)
    follow_ups_asked: List[str] = Field(default_factory=list)
    follow_up_answers: List[str] = Field(default_factory=list)
    critique_scores: List[Dict[str, float]] = Field(default_factory=list)
    iteration_history: List[Dict[str, Any]] = Field(default_factory=list)

class InterviewSession(BaseModel):
    # Job context
    job_description: Optional[str] = None
    company_name: Optional[str] = None
    position: Optional[str] = None
    key_requirements: List[str] = Field(default_factory=list)
    
    # Research data
    research_data: Optional[Dict[str, Any]] = None
    
    # Mode
    mode: InterviewMode = InterviewMode.PRACTICE
    
    # Sessions
    mock_session: MockInterviewSession = Field(default_factory=MockInterviewSession)
    practice_session: PracticeSession = Field(default_factory=PracticeSession)
    
    # Conversation
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
    current_question: Optional[str] = None
    current_answer: Optional[str] = None
    awaiting_follow_up: bool = False
    follow_up_depth: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ShortTermMemory:
    """Manages session-based interview context"""
    
    def __init__(self):
        self.current_session: Optional[InterviewSession] = None
    
    def create_session(
        self,
        job_description: str,
        company_name: str = "",
        position: str = "",
        mode: InterviewMode = InterviewMode.PRACTICE
    ) -> None:
        """Create a new interview session"""
        self.current_session = InterviewSession(
            job_description=job_description,
            company_name=company_name,
            position=position,
            mode=mode
        )
        print(f"✅ Created new {mode.value} session for {company_name} - {position}")
    
    def set_mode(self, mode: InterviewMode) -> None:
        """Change session mode"""
        if self.current_session:
            self.current_session.mode = mode
            self.current_session.updated_at = datetime.now()
    
    def add_research_data(self, research_data: Dict[str, Any]) -> None:
        """Add company research data to session"""
        if self.current_session:
            self.current_session.research_data = research_data
            self.current_session.updated_at = datetime.now()
    
    def add_mock_questions(self, questions: List[Dict[str, Any]]) -> None:
        """Add generated mock interview questions"""
        if self.current_session:
            self.current_session.mock_session.generated_questions = questions
            self.current_session.updated_at = datetime.now()
    
    def get_next_mock_question(self) -> Optional[Dict[str, Any]]:
        """Get next question in mock interview"""
        if not self.current_session:
            return None
        
        mock = self.current_session.mock_session
        if mock.current_question_index < len(mock.generated_questions):
            question = mock.generated_questions[mock.current_question_index]
            mock.current_question_index += 1
            return question
        return None
    
    def add_question(self, question: str) -> None:
        """Add a practice question"""
        if self.current_session:
            self.current_session.practice_session.questions_asked.append(question)
            self.current_session.current_question = question
            self.current_session.updated_at = datetime.now()
    
    def add_answer(self, answer: str, critique_score: Optional[Dict[str, float]] = None) -> None:
        """Add answer and optional critique score"""
        if self.current_session:
            self.current_session.practice_session.answers_given.append(answer)
            self.current_session.current_answer = answer
            
            if critique_score:
                self.current_session.practice_session.critique_scores.append(critique_score)
            
            self.current_session.updated_at = datetime.now()
    
    def add_iteration(self, iteration_data: Dict[str, Any]) -> None:
        """Add iteration history"""
        if self.current_session:
            self.current_session.practice_session.iteration_history.append({
                **iteration_data,
                "timestamp": datetime.now().isoformat()
            })
    
    def add_follow_up(self, question: str, answer: Optional[str] = None) -> None:
        """Add follow-up question and answer"""
        if self.current_session:
            self.current_session.practice_session.follow_ups_asked.append(question)
            if answer:
                self.current_session.practice_session.follow_up_answers.append(answer)
            
            self.current_session.follow_up_depth += 1
            self.current_session.awaiting_follow_up = answer is None
            self.current_session.updated_at = datetime.now()
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """Add message to conversation history"""
        if self.current_session:
            self.current_session.conversation_history.append({
                "role": role,
                "content": content,
                "timestamp": datetime.now().isoformat()
            })
            self.current_session.updated_at = datetime.now()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current session context for agent"""
        if not self.current_session:
            return {}
        
        return {
            "job_description": self.current_session.job_description,
            "company_name": self.current_session.company_name,
            "position": self.current_session.position,
            "key_requirements": self.current_session.key_requirements,
            "research_data": self.current_session.research_data,
            "mode": self.current_session.mode.value,
            "conversation_history": self.current_session.conversation_history[-10:],  # Last 10 messages
            "follow_up_depth": self.current_session.follow_up_depth,
            "awaiting_follow_up": self.current_session.awaiting_follow_up
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for adaptive difficulty"""
        if not self.current_session:
            return {}
        
        scores = self.current_session.practice_session.critique_scores
        if not scores:
            return {"average_score": 0, "question_count": 0}
        
        avg_score = sum(s.get("overall", 0) for s in scores) / len(scores)
        
        return {
            "average_score": avg_score,
            "question_count": len(self.current_session.practice_session.questions_asked),
            "follow_up_count": len(self.current_session.practice_session.follow_ups_asked),
            "latest_scores": scores[-5:] if len(scores) > 5 else scores
        }
    
    def clear_session(self) -> None:
        """Clear current session"""
        self.current_session = None
        print("✅ Cleared short-term memory session")
    
    def export_session(self) -> Dict[str, Any]:
        """Export session data for saving"""
        if not self.current_session:
            return {}
        
        return self.current_session.model_dump()
    
    def import_session(self, session_data: Dict[str, Any]) -> None:
        """Import saved session data"""
        self.current_session = InterviewSession(**session_data)
        print("✅ Imported session data")