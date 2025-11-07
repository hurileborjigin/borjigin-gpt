# src/tools/generation_tools.py
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI
from typing import List, Dict, Any
from src.config.settings import settings
import json
import random

class GenerationTools:
    """Tools for generating questions and predictions"""
    
    def __init__(self):
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai_deployment_name,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            temperature=0.8  # Higher temperature for creative generation
        )
    
    def generate_mock_questions(
        self,
        company_name: str,
        position: str,
        job_description: str,
        company_research: str,
        difficulty: str = "medium",
        count: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Generate mock interview questions based on company and role.
        
        Args:
            company_name: Name of the company
            position: Job position
            job_description: Full job description
            company_research: Company research data
            difficulty: easy, medium, or hard
            count: Number of questions to generate
        
        Returns:
            List of questions with metadata
        """
        # Distribution: 40% behavioral, 40% technical, 20% situational
        behavioral_count = int(count * 0.4)
        technical_count = int(count * 0.4)
        situational_count = count - behavioral_count - technical_count
        
        questions = []
        
        # Generate behavioral questions
        behavioral = self._generate_behavioral_questions(
            company_name, position, job_description, company_research,
            behavioral_count, difficulty
        )
        questions.extend(behavioral)
        
        # Generate technical questions
        technical = self._generate_technical_questions(
            position, job_description, technical_count, difficulty
        )
        questions.extend(technical)
        
        # Generate situational questions
        situational = self._generate_situational_questions(
            company_name, position, company_research, situational_count, difficulty
        )
        questions.extend(situational)
        
        # Shuffle to mix question types
        random.shuffle(questions)
        
        return questions
    
    def _generate_behavioral_questions(
        self, company_name: str, position: str, job_desc: str,
        research: str, count: int, difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate behavioral questions"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate {count} behavioral interview questions for {position} at {company}.

Requirements:
- Focus on past experiences and real situations
- Align with company culture: {research}
- Match job requirements: {job_desc}
- Difficulty level: {difficulty}
- Use "Tell me about a time..." or "Describe a situation..." format

Return ONLY a JSON array of objects with this structure:
[
  {{
    "question": "The question text",
    "type": "behavioral",
    "difficulty": "{difficulty}",
    "themes": ["theme1", "theme2"],
    "expected_framework": "STAR"
  }}
]"""),
            ("user", "Generate the questions:")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "count": count,
            "position": position,
            "company": company_name,
            "research": research[:500],  # Limit context
            "job_desc": job_desc[:500],
            "difficulty": difficulty
        })
        
        try:
            questions = json.loads(result.content)
            return questions if isinstance(questions, list) else []
        except:
            return []
    
    def _generate_technical_questions(
        self, position: str, job_desc: str, count: int, difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate technical questions"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate {count} technical interview questions for {position}.

Requirements:
- Focus on skills and technologies mentioned in: {job_desc}
- Difficulty level: {difficulty}
- Include both theoretical and practical questions
- Cover relevant tools, frameworks, and methodologies

Return ONLY a JSON array of objects with this structure:
[
  {{
    "question": "The question text",
    "type": "technical",
    "difficulty": "{difficulty}",
    "themes": ["skill1", "skill2"],
    "expected_framework": "Direct"
  }}
]"""),
            ("user", "Generate the questions:")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "count": count,
            "position": position,
            "job_desc": job_desc[:500],
            "difficulty": difficulty
        })
        
        try:
            questions = json.loads(result.content)
            return questions if isinstance(questions, list) else []
        except:
            return []
    
    def _generate_situational_questions(
        self, company_name: str, position: str, research: str,
        count: int, difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate situational questions"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate {count} situational interview questions for {position} at {company}.

Requirements:
- Present hypothetical scenarios
- Align with company culture: {research}
- Difficulty level: {difficulty}
- Use "What would you do if..." or "How would you handle..." format

Return ONLY a JSON array of objects with this structure:
[
  {{
    "question": "The question text",
    "type": "situational",
    "difficulty": "{difficulty}",
    "themes": ["theme1", "theme2"],
    "expected_framework": "CAR"
  }}
]"""),
            ("user", "Generate the questions:")
        ])
        
        chain = prompt | self.llm
        result = chain.invoke({
            "count": count,
            "position": position,
            "company": company_name,
            "research": research[:500],
            "difficulty": difficulty
        })
        
        try:
            questions = json.loads(result.content)
            return questions if isinstance(questions, list) else []
        except:
            return []
    
    def create_follow_up_predictor_tool(self):
        """Create follow-up question prediction tool"""
        llm = self.llm
        
        @tool
        def predict_follow_ups(question: str, answer: str) -> str:
            """
            Predict likely follow-up questions based on the answer given.
            
            Args:
                question: The original interview question
                answer: The answer provided
            
            Returns:
                List of 2-3 predicted follow-up questions with brief response guidance
            """
            prompt = ChatPromptTemplate.from_messages([
                ("system", """Based on the interview answer, predict 2-3 likely follow-up questions an interviewer might ask.

For each follow-up:
1. The question itself
2. Why they might ask it
3. Brief guidance on how to respond

Return as JSON:
{{
  "follow_ups": [
    {{
      "question": "...",
      "reason": "...",
      "guidance": "..."
    }}
  ]
}}"""),
                ("user", "Original Question: {question}\n\nAnswer Given: {answer}\n\nPredict follow-ups:")
            ])
            
            chain = prompt | llm
            result = chain.invoke({
                "question": question,
                "answer": answer
            })
            
            return result.content
        
        return predict_follow_ups
    
    def adjust_difficulty(self, current_difficulty: str, performance_score: float) -> str:
        """
        Adjust difficulty based on performance (for adaptive mock interviews).
        
        Args:
            current_difficulty: Current difficulty level
            performance_score: Average performance score (0-10)
        
        Returns:
            New difficulty level
        """
        if performance_score >= 8.5:
            # Performing very well, increase difficulty
            if current_difficulty == "easy":
                return "medium"
            elif current_difficulty == "medium":
                return "hard"
        elif performance_score <= 5.5:
            # Struggling, decrease difficulty
            if current_difficulty == "hard":
                return "medium"
            elif current_difficulty == "medium":
                return "easy"
        
        return current_difficulty  # Keep same difficulty
    
    def get_all_tools(self) -> List:
        """Get all generation tools"""
        return [
            self.create_follow_up_predictor_tool()
        ]