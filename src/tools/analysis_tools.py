# src/tools/analysis_tools.py
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from typing import Dict, Any, List
from src.config.settings import settings
import json

class AnalysisTools:
    """Tools for analyzing questions and answers"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai_deployment_name,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            temperature=0.3  # Lower temperature for analysis
        )
    
    def create_question_analyzer_tool(self):
        """Create question analysis tool"""
        llm = self.llm
        
        @tool
        def analyze_question(question: str, job_context: str = "") -> str:
            """
            Analyze an interview question to understand what the interviewer is looking for.
            
            Args:
                question: The interview question to analyze
                job_context: Optional job description or company context
            
            Returns:
                Analysis of the question including type, themes, and expected answer structure
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert interview coach. Analyze the interview question and provide:

1. **Question Type**: Behavioral, Technical, Situational, or Other
2. **Key Themes**: What topics/skills is this question targeting?
3. **What They're Really Asking**: The underlying intent
4. **Recommended Framework**: STAR, CAR, or Direct Answer
5. **Key Points to Address**: What must be included in a good answer
6. **Potential Pitfalls**: What to avoid

Be concise but thorough."""),
                ("user", "Interview Question: {question}\n\nJob Context: {context}\n\nProvide your analysis:")
            ])
            
            chain = prompt | llm
            result = chain.invoke({
                "question": question,
                "context": job_context or "Not provided"
            })
            
            return result.content
        
        return analyze_question
    
    def create_star_formatter_tool(self):
        """Create STAR framework formatting tool"""
        llm = self.llm
        
        @tool
        def format_with_star(experience: str, question: str) -> str:
            """
            Format an experience using the STAR framework (Situation, Task, Action, Result).
            
            Args:
                experience: The experience or story to format
                question: The interview question being answered
            
            Returns:
                Experience formatted in STAR structure
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Format the given experience using the STAR framework:

**Situation**: Set the context (1-2 sentences)
**Task**: Describe the challenge or goal (1-2 sentences)
**Action**: Explain what YOU did specifically (2-3 sentences)
**Result**: Share the outcome with metrics if possible (1-2 sentences)

Make it concise, specific, and impactful."""),
                ("user", "Question: {question}\n\nExperience: {experience}\n\nFormat this in STAR structure:")
            ])
            
            chain = prompt | llm
            result = chain.invoke({
                "question": question,
                "experience": experience
            })
            
            return result.content
        
        return format_with_star
    
    def create_answer_validator_tool(self):
        """Create answer validation tool"""
        llm = self.llm
        
        @tool
        def validate_answer(question: str, answer: str, cv_info: str = "") -> str:
            """
            Validate and score an interview answer.
            
            Args:
                question: The interview question
                answer: The proposed answer
                cv_info: Relevant CV information for fact-checking
            
            Returns:
                Validation results with scores and improvement suggestions (JSON format)
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are an expert interview coach. Evaluate this interview answer and provide scores (0-10) for:

1. **Authenticity**: Does it sound genuine and based on real experience?
2. **Relevance**: Does it directly answer the question?
3. **Structure**: Is it well-organized and easy to follow?
4. **Specificity**: Does it include concrete details and examples?
5. **Impact**: Does it demonstrate value and results?
6. **Length**: Is it appropriately concise (2-3 minutes when spoken)?

Also provide:
- **Overall Score** (average of above)
- **Strengths** (2-3 points)
- **Improvements** (2-3 specific suggestions)
- **Fact Check**: Does the answer align with the CV? (if CV provided)

Return as JSON with this structure:
{{
  "scores": {{"authenticity": X, "relevance": X, "structure": X, "specificity": X, "impact": X, "length": X}},
  "overall": X,
  "strengths": ["...", "..."],
  "improvements": ["...", "..."],
  "fact_check": "..."
}}"""),
                ("user", "Question: {question}\n\nAnswer: {answer}\n\nCV Info: {cv_info}\n\nProvide your evaluation:")
            ])
            
            chain = prompt | llm
            result = chain.invoke({
                "question": question,
                "answer": answer,
                "cv_info": cv_info or "Not provided"
            })
            
            return result.content
        
        return validate_answer
    
    def create_company_alignment_tool(self):
        """Create company-answer alignment tool"""
        llm = self.llm
        
        @tool
        def check_company_alignment(answer: str, company_research: str) -> str:
            """
            Check how well an answer aligns with company culture and values.
            
            Args:
                answer: The interview answer
                company_research: Company research data (culture, values, etc.)
            
            Returns:
                Alignment analysis with score and suggestions
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Analyze how well this interview answer aligns with the company's culture and values.

Provide:
1. **Alignment Score** (0-10)
2. **What Aligns Well**: Specific points that match company values
3. **What Could Be Better**: How to improve alignment
4. **Suggested Additions**: Company-specific points to mention

Be specific and actionable."""),
                ("user", "Answer: {answer}\n\nCompany Research:\n{research}\n\nAnalyze alignment:")
            ])
            
            chain = prompt | llm
            result = chain.invoke({
                "answer": answer,
                "research": company_research or "Not provided"
            })
            
            return result.content
        
        return check_company_alignment
    
    def get_all_tools(self) -> List:
        """Get all analysis tools"""
        return [
            self.create_question_analyzer_tool(),
            self.create_star_formatter_tool(),
            self.create_answer_validator_tool(),
            self.create_company_alignment_tool()
        ]