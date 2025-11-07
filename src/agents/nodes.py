# src/agents/nodes.py
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from src.config.settings import settings
from src.agents.state import AgentState
from src.tools.retrieval_tools import RetrievalTools
from src.tools.analysis_tools import AnalysisTools
from src.tools.generation_tools import GenerationTools
import json

class AgentNodes:
    """Node functions for the LangGraph agent"""
    
    def __init__(
        self,
        retrieval_tools: RetrievalTools,
        analysis_tools: AnalysisTools,
        generation_tools: GenerationTools
    ):
        self.retrieval_tools = retrieval_tools
        self.analysis_tools = analysis_tools
        self.generation_tools = generation_tools
        
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai_deployment_name,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            temperature=settings.temperature
        )
    
    def analyze_question_node(self, state: AgentState) -> Dict[str, Any]:
        """Analyze the interview question"""
        print("🔍 Analyzing question...")
        
        question = state["question"]
        job_context = state.get("job_description", "")
        
        # Use analysis tool
        analyzer = self.analysis_tools.create_question_analyzer_tool()
        analysis_result = analyzer.invoke({
            "question": question,
            "job_context": job_context
        })
        
        # Parse the analysis (it's a string, we'll keep it as is)
        return {
            "question_analysis": {
                "raw_analysis": analysis_result,
                "question": question
            },
            "messages": [AIMessage(content=f"Question analyzed: {question}")]
        }
    
    def retrieve_context_node(self, state: AgentState) -> Dict[str, Any]:
        """Retrieve relevant context from all memory sources"""
        print("📚 Retrieving context...")
        
        question = state["question"]
        question_analysis = state.get("question_analysis", {})
        
        # Get retrieval tools
        cv_tool = self.retrieval_tools.create_cv_retrieval_tool()
        exp_tool = self.retrieval_tools.create_experience_retrieval_tool()
        personality_tool = self.retrieval_tools.create_personality_retrieval_tool()
        company_tool = self.retrieval_tools.create_company_research_tool()
        
        # Retrieve from different sources
        cv_context = cv_tool.invoke({"query": question})
        experience_context = exp_tool.invoke({"query": question})
        personality_context = personality_tool.invoke({})
        
        # Get company context if available
        company_context = ""
        company_name = state.get("company_name")
        if company_name:
            company_context = company_tool.invoke({"company_name": company_name})
        
        return {
            "cv_context": cv_context,
            "experience_context": experience_context,
            "personality_context": personality_context,
            "company_context": company_context,
            "messages": [AIMessage(content="Context retrieved from all sources")]
        }
    
    def generate_answer_node(self, state: AgentState) -> Dict[str, Any]:
        """Generate interview answer"""
        iteration = state.get("iteration_count", 0)
        print(f"✍️ Generating answer (iteration {iteration + 1})...")
        
        question = state["question"]
        question_analysis = state.get("question_analysis", {})
        cv_context = state.get("cv_context", "")
        experience_context = state.get("experience_context", "")
        personality_context = state.get("personality_context", "")
        company_context = state.get("company_context", "")
        
        # Get previous critique if iterating
        previous_critique = state.get("critique_result")
        improvements = ""
        if previous_critique and iteration > 0:
            improvements = "\n".join(previous_critique.get("improvements", []))
        
        # Build comprehensive prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert interview coach helping a candidate prepare their answer.

Your task is to generate a compelling, authentic interview answer based on:
1. The candidate's real CV and experiences
2. Their personality and communication style
3. The company's culture and values
4. The specific question being asked

Guidelines:
- Be authentic - only use real experiences from the provided context
- Be specific - include concrete details, metrics, and outcomes
- Be concise - aim for 2-3 minutes when spoken (about 250-350 words)
- Use appropriate framework (STAR for behavioral, direct for technical)
- Align with company culture when relevant
- Show impact and value

{improvement_guidance}

Generate a polished, interview-ready answer."""),
            ("user", """**Interview Question:**
{question}

**Question Analysis:**
{analysis}

**Relevant CV Information:**
{cv_context}

**Relevant Experiences:**
{experience_context}

**Personality Profile:**
{personality_context}

**Company Context:**
{company_context}

{improvement_section}

Generate the interview answer:""")
        ])
        
        improvement_section = ""
        improvement_guidance = ""
        if improvements:
            improvement_section = f"\n**Previous Feedback to Address:**\n{improvements}"
            improvement_guidance = "IMPORTANT: Address the feedback from the previous iteration."
        
        chain = prompt | self.llm
        result = chain.invoke({
            "question": question,
            "analysis": question_analysis.get("raw_analysis", ""),
            "cv_context": cv_context,
            "experience_context": experience_context,
            "personality_context": personality_context,
            "company_context": company_context,
            "improvement_section": improvement_section,
            "improvement_guidance": improvement_guidance
        })
        
        answer = result.content
        
        return {
            "current_answer": answer,
            "iteration_count": iteration + 1,
            "messages": [AIMessage(content=f"Generated answer (iteration {iteration + 1})")]
        }
    
    def critique_answer_node(self, state: AgentState) -> Dict[str, Any]:
        """Critique and score the generated answer"""
        print("🎯 Critiquing answer...")
        
        question = state["question"]
        answer = state["current_answer"]
        cv_context = state.get("cv_context", "")
        company_context = state.get("company_context", "")
        
        # Use validator tool
        validator = self.analysis_tools.create_answer_validator_tool()
        validation_result = validator.invoke({
            "question": question,
            "answer": answer,
            "cv_info": cv_context
        })
        
        # Parse JSON result
        try:
            critique = json.loads(validation_result)
        except:
            # Fallback if parsing fails
            critique = {
                "scores": {
                    "authenticity": 7.0,
                    "relevance": 7.0,
                    "structure": 7.0,
                    "specificity": 7.0,
                    "impact": 7.0,
                    "length": 7.0
                },
                "overall": 7.0,
                "strengths": ["Answer provided"],
                "improvements": ["Could be more specific"]
            }
        
        # Check company alignment if company context available
        if company_context:
            alignment_tool = self.analysis_tools.create_company_alignment_tool()
            alignment_result = alignment_tool.invoke({
                "answer": answer,
                "company_research": company_context
            })
            critique["company_alignment"] = alignment_result
        
        # Determine if we should iterate
        overall_score = critique.get("overall", 0)
        iteration_count = state.get("iteration_count", 0)
        
        should_iterate = (
            overall_score < settings.critique_threshold and 
            iteration_count < settings.max_iterations
        )
        
        print(f"   Score: {overall_score}/10 | Iterate: {should_iterate}")
        
        return {
            "critique_result": critique,
            "should_iterate": should_iterate,
            "messages": [AIMessage(content=f"Answer scored: {overall_score}/10")]
        }
    
    def refine_answer_node(self, state: AgentState) -> Dict[str, Any]:
        """Final refinement of the answer"""
        print("✨ Refining final answer...")
        
        answer = state["current_answer"]
        critique = state.get("critique_result", {})
        
        # Extract strengths to preserve
        strengths = critique.get("strengths", [])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are polishing a final interview answer. 

Make it:
- Clear and concise
- Well-structured
- Impactful
- Natural and conversational

Preserve these strengths: {strengths}

Only make minor improvements to clarity and flow. Don't change the core content."""),
            ("user", "Polish this answer:\n\n{answer}")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "answer": answer,
            "strengths": ", ".join(strengths)
        })
        
        refined_answer = result.content
        
        return {
            "final_answer": refined_answer,
            "messages": [AIMessage(content="Answer refined and finalized")]
        }
    
    def extract_key_points_node(self, state: AgentState) -> Dict[str, Any]:
        """Extract key points and delivery tips"""
        print("📝 Extracting key points...")
        
        final_answer = state.get("final_answer", state.get("current_answer", ""))
        question = state["question"]
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract from this interview answer:

1. **Key Points to Remember** (3-5 bullet points)
   - Main messages to emphasize
   - Important details not to forget

2. **Delivery Tips** (3-4 tips)
   - How to present this effectively
   - Body language or tone suggestions
   - Pacing recommendations

Return as JSON:
{{
  "key_points": ["...", "..."],
  "delivery_tips": ["...", "..."]
}}"""),
            ("user", "Question: {question}\n\nAnswer: {answer}\n\nExtract key points and tips:")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "question": question,
            "answer": final_answer
        })
        
        try:
            extracted = json.loads(result.content)
            key_points = extracted.get("key_points", [])
            delivery_tips = extracted.get("delivery_tips", [])
        except:
            key_points = ["Review the full answer"]
            delivery_tips = ["Practice delivery out loud"]
        
        return {
            "key_points": key_points,
            "delivery_tips": delivery_tips,
            "messages": [AIMessage(content="Key points extracted")]
        }
    
    def predict_follow_ups_node(self, state: AgentState) -> Dict[str, Any]:
        """Predict and prepare for follow-up questions"""
        print("🔮 Predicting follow-up questions...")
        
        question = state["question"]
        answer = state.get("final_answer", state.get("current_answer", ""))
        
        # Use follow-up predictor tool
        predictor = self.generation_tools.create_follow_up_predictor_tool()
        prediction_result = predictor.invoke({
            "question": question,
            "answer": answer
        })
        
        try:
            predictions = json.loads(prediction_result)
            follow_ups = predictions.get("follow_ups", [])
        except:
            follow_ups = []
        
        return {
            "follow_up_questions": follow_ups,
            "messages": [AIMessage(content=f"Predicted {len(follow_ups)} follow-up questions")]
        }
    
    def handle_follow_up_node(self, state: AgentState) -> Dict[str, Any]:
        """Handle a follow-up question"""
        print("🔄 Handling follow-up question...")
        
        # This node would be triggered when user asks a follow-up
        # For now, we'll prepare the structure
        
        follow_up_depth = state.get("follow_up_depth", 0)
        
        if follow_up_depth >= settings.follow_up_depth:
            return {
                "messages": [AIMessage(content="Maximum follow-up depth reached")],
                "error": "max_follow_up_depth"
            }
        
        # Reset iteration count for follow-up
        return {
            "iteration_count": 0,
            "follow_up_depth": follow_up_depth + 1,
            "messages": [AIMessage(content="Processing follow-up question")]
        }