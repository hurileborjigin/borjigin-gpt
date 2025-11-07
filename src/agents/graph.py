# src/agents/graph.py
from typing import Literal
from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes import AgentNodes
from src.tools.retrieval_tools import RetrievalTools
from src.tools.analysis_tools import AnalysisTools
from src.tools.generation_tools import GenerationTools
from src.memory.long_term_memory import LongTermMemory
from src.memory.company_research_cache import CompanyResearchCache

class InterviewPrepAgent:
    """Main agent for interview preparation"""
    
    def __init__(
        self,
        long_term_memory: LongTermMemory,
        research_cache: CompanyResearchCache
    ):
        # Initialize tools
        self.retrieval_tools = RetrievalTools(long_term_memory, research_cache)
        self.analysis_tools = AnalysisTools()
        self.generation_tools = GenerationTools()
        
        # Initialize nodes
        self.nodes = AgentNodes(
            self.retrieval_tools,
            self.analysis_tools,
            self.generation_tools
        )
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze_question", self.nodes.analyze_question_node)
        workflow.add_node("retrieve_context", self.nodes.retrieve_context_node)
        workflow.add_node("generate_answer", self.nodes.generate_answer_node)
        workflow.add_node("critique_answer", self.nodes.critique_answer_node)
        workflow.add_node("refine_answer", self.nodes.refine_answer_node)
        workflow.add_node("extract_key_points", self.nodes.extract_key_points_node)
        workflow.add_node("predict_follow_ups", self.nodes.predict_follow_ups_node)
        workflow.add_node("handle_follow_up", self.nodes.handle_follow_up_node)
        
        # Set entry point
        workflow.set_entry_point("analyze_question")
        
        # Define edges
        workflow.add_edge("analyze_question", "retrieve_context")
        workflow.add_edge("retrieve_context", "generate_answer")
        workflow.add_edge("generate_answer", "critique_answer")
        
        # Conditional edge: iterate or refine?
        workflow.add_conditional_edges(
            "critique_answer",
            self._should_iterate,
            {
                "iterate": "generate_answer",  # Loop back
                "refine": "refine_answer"      # Move forward
            }
        )
        
        workflow.add_edge("refine_answer", "extract_key_points")
        workflow.add_edge("extract_key_points", "predict_follow_ups")
        workflow.add_edge("predict_follow_ups", END)
        
        # Compile graph
        return workflow.compile()
    
    def _should_iterate(self, state: AgentState) -> Literal["iterate", "refine"]:
        """Decide whether to iterate or move to refinement"""
        should_iterate = state.get("should_iterate", False)
        return "iterate" if should_iterate else "refine"
    
    def process_question(
        self,
        question: str,
        job_description: str = "",
        company_name: str = "",
        position: str = "",
        research_data: dict = None,
        mode: str = "practice"
    ) -> dict:
        """
        Process an interview question and generate answer.
        
        Args:
            question: The interview question
            job_description: Job description context
            company_name: Company name
            position: Position title
            research_data: Company research data
            mode: Interview mode (practice, mock_interview, etc.)
        
        Returns:
            Complete response with answer, key points, tips, and follow-ups
        """
        # Initialize state
        initial_state = {
            "messages": [],
            "question": question,
            "question_analysis": None,
            "cv_context": None,
            "experience_context": None,
            "personality_context": None,
            "company_context": None,
            "current_answer": None,
            "iteration_count": 0,
            "critique_result": None,
            "should_iterate": False,
            "follow_up_questions": None,
            "follow_up_depth": 0,
            "job_description": job_description,
            "company_name": company_name,
            "position": position,
            "research_data": research_data,
            "mode": mode,
            "final_answer": None,
            "key_points": None,
            "delivery_tips": None,
            "error": None
        }
        
        # Run the graph
        print(f"\n{'='*60}")
        print(f"🎯 Processing Question: {question[:50]}...")
        print(f"{'='*60}\n")
        
        final_state = self.graph.invoke(initial_state)
        
        # Extract results
        result = {
            "question": question,
            "answer": final_state.get("final_answer", ""),
            "key_points": final_state.get("key_points", []),
            "delivery_tips": final_state.get("delivery_tips", []),
            "follow_up_questions": final_state.get("follow_up_questions", []),
            "critique_scores": final_state.get("critique_result", {}),
            "iterations": final_state.get("iteration_count", 0),
            "question_analysis": final_state.get("question_analysis", {}),
            "error": final_state.get("error")
        }
        
        print(f"\n{'='*60}")
        print(f"✅ Question Processed Successfully!")
        print(f"   Iterations: {result['iterations']}")
        print(f"   Final Score: {result['critique_scores'].get('overall', 'N/A')}/10")
        print(f"{'='*60}\n")
        
        return result
    
    def process_follow_up(
        self,
        follow_up_question: str,
        original_question: str,
        original_answer: str,
        context: dict
    ) -> dict:
        """
        Process a follow-up question.
        
        Args:
            follow_up_question: The follow-up question
            original_question: The original question
            original_answer: The original answer
            context: Session context
        
        Returns:
            Response for the follow-up
        """
        # Build context that includes original Q&A
        enhanced_context = context.copy()
        enhanced_context["previous_qa"] = {
            "question": original_question,
            "answer": original_answer
        }
        
        # Process as a new question with enhanced context
        return self.process_question(
            question=follow_up_question,
            job_description=context.get("job_description", ""),
            company_name=context.get("company_name", ""),
            position=context.get("position", ""),
            research_data=context.get("research_data"),
            mode=context.get("mode", "practice")
        )