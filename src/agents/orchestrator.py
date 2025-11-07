# src/agents/orchestrator.py
from typing import Dict, Any, Optional
from src.agents.graph import InterviewPrepAgent
from src.agents.mock_interview import MockInterviewGenerator
from src.memory.long_term_memory import LongTermMemory
from src.memory.short_term_memory import ShortTermMemory, InterviewMode
from src.memory.company_research_cache import CompanyResearchCache
from src.tools.web_search import WebSearchTool
from src.tools.generation_tools import GenerationTools

class InterviewPrepOrchestrator:
    """Main orchestrator for the interview prep system"""
    
    def __init__(self):
        # Initialize memory systems
        self.long_term_memory = LongTermMemory()
        self.short_term_memory = ShortTermMemory()
        self.research_cache = CompanyResearchCache()
        
        # Initialize tools
        self.web_search = WebSearchTool()
        self.generation_tools = GenerationTools()
        
        # Initialize agents
        self.agent = InterviewPrepAgent(
            self.long_term_memory,
            self.research_cache
        )
        
        self.mock_interview_gen = MockInterviewGenerator(
            self.web_search,
            self.generation_tools,
            self.research_cache
        )
    
    # ============= SESSION MANAGEMENT =============
    
    def create_session(
        self,
        job_description: str,
        company_name: str = "",
        position: str = "",
        mode: str = "practice"
    ) -> None:
        """Create a new interview session"""
        self.short_term_memory.create_session(
            job_description=job_description,
            company_name=company_name,
            position=position,
            mode=InterviewMode(mode)
        )
    
    def get_session_context(self) -> Dict[str, Any]:
        """Get current session context"""
        return self.short_term_memory.get_context()
    
    # ============= PREPARATION MODE =============
    
    def prepare_for_interview(
        self,
        company_name: str,
        position: str,
        job_description: str,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Preparation mode: Research company and generate mock questions.
        
        Returns:
            Complete preparation package
        """
        # Create session
        self.create_session(
            job_description=job_description,
            company_name=company_name,
            position=position,
            mode="preparation"
        )
        
        # Generate mock interview
        mock_interview = self.mock_interview_gen.prepare_mock_interview(
            company_name=company_name,
            position=position,
            job_description=job_description,
            force_refresh=force_refresh
        )
        
        # Store in session
        self.short_term_memory.add_research_data(mock_interview["research_data"])
        self.short_term_memory.add_mock_questions(mock_interview["questions"])
        
        return mock_interview
    
    # ============= PRACTICE MODE =============
    
    def practice_question(
        self,
        question: str,
        use_session_context: bool = True
    ) -> Dict[str, Any]:
        """
        Practice mode: Answer a single question.
        
        Args:
            question: The interview question
            use_session_context: Use current session context
        
        Returns:
            Complete answer package
        """
        context = {}
        if use_session_context and self.short_term_memory.current_session:
            context = self.short_term_memory.get_context()
        
        # Process question through agent
        result = self.agent.process_question(
            question=question,
            job_description=context.get("job_description", ""),
            company_name=context.get("company_name", ""),
            position=context.get("position", ""),
            research_data=context.get("research_data"),
            mode="practice"
        )
        
        # Store in session
        if self.short_term_memory.current_session:
            self.short_term_memory.add_question(question)
            self.short_term_memory.add_answer(
                result["answer"],
                result["critique_scores"]
            )
            
            # Store iteration history
            for i in range(result["iterations"]):
                self.short_term_memory.add_iteration({
                    "iteration": i + 1,
                    "score": result["critique_scores"].get("overall", 0)
                })
        
        return result
    
    def practice_follow_up(
        self,
        follow_up_question: str
    ) -> Dict[str, Any]:
        """
        Practice a follow-up question.
        
        Args:
            follow_up_question: The follow-up question
        
        Returns:
            Answer for the follow-up
        """
        if not self.short_term_memory.current_session:
            raise ValueError("No active session. Create a session first.")
        
        session = self.short_term_memory.current_session
        
        # Get last question and answer
        questions = session.practice_session.questions_asked
        answers = session.practice_session.answers_given
        
        if not questions or not answers:
            raise ValueError("No previous question to follow up on.")
        
        original_question = questions[-1]
        original_answer = answers[-1]
        
        context = self.short_term_memory.get_context()
        
        # Process follow-up
        result = self.agent.process_follow_up(
            follow_up_question=follow_up_question,
            original_question=original_question,
            original_answer=original_answer,
            context=context
        )
        
        # Store follow-up
        self.short_term_memory.add_follow_up(
            follow_up_question,
            result["answer"]
        )
        
        return result
    
    # ============= MOCK INTERVIEW MODE =============
    
    def start_mock_interview(self) -> Dict[str, Any]:
        """
        Start a mock interview using generated questions.
        
        Returns:
            First question and interview info
        """
        if not self.short_term_memory.current_session:
            raise ValueError("No active session. Run prepare_for_interview first.")
        
        self.short_term_memory.set_mode(InterviewMode.MOCK_INTERVIEW)
        
        # Get first question
        first_question = self.short_term_memory.get_next_mock_question()
        
        if not first_question:
            raise ValueError("No mock questions available.")
        
        return {
            "question": first_question,
            "total_questions": len(
                self.short_term_memory.current_session.mock_session.generated_questions
            ),
            "current_index": 1
        }
    
    def answer_mock_question(self) -> Dict[str, Any]:
        """
        Get answer for current mock interview question.
        
        Returns:
            Complete answer package
        """
        if not self.short_term_memory.current_session:
            raise ValueError("No active mock interview.")
        
        session = self.short_term_memory.current_session
        current_idx = session.mock_session.current_question_index - 1
        
        if current_idx < 0 or current_idx >= len(session.mock_session.generated_questions):
            raise ValueError("No current question.")
        
        current_question = session.mock_session.generated_questions[current_idx]
        
        # Process the question
        result = self.practice_question(
            question=current_question["question"],
            use_session_context=True
        )
        
        # Store performance score
        score = result["critique_scores"].get("overall", 0)
        session.mock_session.performance_scores.append(score)
        
        # Check if we should adjust difficulty (adaptive)
        if len(session.mock_session.performance_scores) % 3 == 0:  # Every 3 questions
            self._adjust_mock_difficulty()
        
        return result
    
    def get_next_mock_question(self) -> Optional[Dict[str, Any]]:
        """
        Get next question in mock interview.
        
        Returns:
            Next question or None if finished
        """
        next_q = self.short_term_memory.get_next_mock_question()
        
        if not next_q:
            return None
        
        session = self.short_term_memory.current_session
        
        return {
            "question": next_q,
            "current_index": session.mock_session.current_question_index,
            "total_questions": len(session.mock_session.generated_questions)
        }
    
    def _adjust_mock_difficulty(self) -> None:
        """Adjust difficulty for adaptive mock interview"""
        session = self.short_term_memory.current_session
        
        if not session:
            return
        
        performance = self.short_term_memory.get_performance_summary()
        avg_score = performance.get("average_score", 0)
        
        current_difficulty = session.mock_session.difficulty_level
        new_difficulty = self.generation_tools.adjust_difficulty(
            current_difficulty,
            avg_score
        )
        
        if new_difficulty != current_difficulty:
            session.mock_session.difficulty_level = new_difficulty
            print(f"🎚️ Difficulty adjusted: {current_difficulty} → {new_difficulty}")
    
    def get_mock_interview_summary(self) -> Dict[str, Any]:
        """
        Get summary of completed mock interview.
        
        Returns:
            Performance summary and statistics
        """
        performance = self.short_term_memory.get_performance_summary()
        
        if not self.short_term_memory.current_session:
            return performance
        
        session = self.short_term_memory.current_session
        
        return {
            **performance,
            "questions_answered": session.mock_session.current_question_index,
            "total_questions": len(session.mock_session.generated_questions),
            "difficulty_progression": session.mock_session.difficulty_level,
            "scores_by_question": session.mock_session.performance_scores
        }
    
    # ============= MEMORY MANAGEMENT =============
    
    def add_cv(self, cv_text: str, metadata: Optional[Dict] = None) -> None:
        """Add CV to long-term memory"""
        self.long_term_memory.add_cv(cv_text, metadata)
    
    def add_experience(self, experience: str, metadata: Optional[Dict] = None) -> None:
        """Add experience to long-term memory"""
        self.long_term_memory.add_experience(experience, metadata)
    
    def add_personality(self, personality_data: Dict[str, Any]) -> None:
        """Add personality profile to long-term memory"""
        self.long_term_memory.add_personality(personality_data)
    
    def clear_session(self) -> None:
        """Clear current session"""
        self.short_term_memory.clear_session()
    
    def export_session(self) -> Dict[str, Any]:
        """Export current session"""
        return self.short_term_memory.export_session()