# src/agents/mock_interview.py
from typing import List, Dict, Any
from src.tools.web_search import WebSearchTool
from src.tools.generation_tools import GenerationTools
from src.memory.company_research_cache import CompanyResearchCache
from src.memory.short_term_memory import ShortTermMemory

class MockInterviewGenerator:
    """Generate and manage mock interviews"""
    
    def __init__(
        self,
        web_search: WebSearchTool,
        generation_tools: GenerationTools,
        research_cache: CompanyResearchCache
    ):
        self.web_search = web_search
        self.generation_tools = generation_tools
        self.research_cache = research_cache
    
    def prepare_mock_interview(
        self,
        company_name: str,
        position: str,
        job_description: str,
        force_refresh: bool = False,
        question_count: int = 15
    ) -> Dict[str, Any]:
        """
        Prepare a complete mock interview with research and questions.
        
        Args:
            company_name: Name of the company
            position: Job position
            job_description: Full job description
            force_refresh: Force new research even if cached
            question_count: Number of questions to generate
        
        Returns:
            Complete mock interview package
        """
        print(f"\n{'='*60}")
        print(f"🎭 Preparing Mock Interview")
        print(f"   Company: {company_name}")
        print(f"   Position: {position}")
        print(f"{'='*60}\n")
        
        # Step 1: Get or perform company research
        research_data = self._get_company_research(
            company_name, 
            position,
            force_refresh
        )
        
        # Step 2: Generate mock questions
        questions = self._generate_questions(
            company_name,
            position,
            job_description,
            research_data,
            question_count
        )
        
        # Step 3: Prepare interview package
        interview_package = {
            "company_name": company_name,
            "position": position,
            "job_description": job_description,
            "research_data": research_data,
            "questions": questions,
            "total_questions": len(questions),
            "difficulty_distribution": self._get_difficulty_distribution(questions),
            "type_distribution": self._get_type_distribution(questions)
        }
        
        print(f"\n{'='*60}")
        print(f"✅ Mock Interview Ready!")
        print(f"   Total Questions: {len(questions)}")
        print(f"   Behavioral: {interview_package['type_distribution'].get('behavioral', 0)}")
        print(f"   Technical: {interview_package['type_distribution'].get('technical', 0)}")
        print(f"   Situational: {interview_package['type_distribution'].get('situational', 0)}")
        print(f"{'='*60}\n")
        
        return interview_package
    
    def _get_company_research(
        self,
        company_name: str,
        position: str,
        force_refresh: bool
    ) -> Dict[str, Any]:
        """Get company research (cached or fresh)"""
        
        # Check cache first
        if not force_refresh:
            cached = self.research_cache.get_research(company_name)
            if cached:
                print(f"📦 Using cached research for {company_name}")
                return cached
        
        print(f"🔍 Researching {company_name}...")
        
        # Perform comprehensive web search with new method names
        try:
            overview = self.web_search.search_company_overview(company_name)
            culture = self.web_search.search_company_culture(company_name)
            news = self.web_search.search_recent_news(company_name, days=180)
            position_insights = self.web_search.search_position_insights(company_name, position)
            
            research_data = {
                "company_name": company_name,
                "position": position,
                "overview": overview.get("summary", ""),
                "overview_sources": overview.get("sources", []),
                "culture": culture.get("summary", ""),
                "culture_sources": culture.get("sources", []),
                "news": news.get("summary", ""),
                "news_sources": news.get("sources", []),
                "position_analysis": position_insights.get("summary", ""),
                "position_sources": position_insights.get("sources", []),
                "research_timestamp": datetime.now().isoformat()
            }
            
            # Cache the research
            self.research_cache.save_research(company_name, research_data)
            
            print(f"✅ Research completed and cached")
            
            return research_data
            
        except Exception as e:
            print(f"❌ Research error: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "company_name": company_name,
                "position": position,
                "overview": f"Error researching {company_name}: {str(e)}",
                "culture": "",
                "news": "",
                "position_analysis": "",
                "overview_sources": [],
                "culture_sources": [],
                "news_sources": [],
                "position_sources": []
            }
    def _generate_questions(
        self,
        company_name: str,
        position: str,
        job_description: str,
        research_data: Dict[str, Any],
        count: int
    ) -> List[Dict[str, Any]]:
        """Generate mock interview questions"""
        
        print(f"💭 Generating {count} interview questions...")
        
        # Combine research data for context
        company_research = f"""
        Overview: {research_data.get('overview', '')}
        Culture: {research_data.get('culture', '')}
        Recent News: {research_data.get('news', '')}
        """
        
        questions = self.generation_tools.generate_mock_questions(
            company_name=company_name,
            position=position,
            job_description=job_description,
            company_research=company_research,
            difficulty="medium",  # Start with medium
            count=count
        )
        
        print(f"✅ Generated {len(questions)} questions")
        
        return questions
    
    def _get_difficulty_distribution(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of question difficulties"""
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        
        for q in questions:
            difficulty = q.get("difficulty", "medium")
            distribution[difficulty] = distribution.get(difficulty, 0) + 1
        
        return distribution
    
    def _get_type_distribution(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of question types"""
        distribution = {"behavioral": 0, "technical": 0, "situational": 0}
        
        for q in questions:
            q_type = q.get("type", "behavioral")
            distribution[q_type] = distribution.get(q_type, 0) + 1
        
        return distribution
    
    def adjust_difficulty_adaptive(
        self,
        current_questions: List[Dict[str, Any]],
        performance_scores: List[float],
        remaining_count: int
    ) -> str:
        """
        Adjust difficulty for remaining questions based on performance.
        
        Args:
            current_questions: Questions asked so far
            performance_scores: Scores received
            remaining_count: How many questions remain
        
        Returns:
            New difficulty level
        """
        if not performance_scores:
            return "medium"
        
        avg_score = sum(performance_scores) / len(performance_scores)
        current_difficulty = current_questions[-1].get("difficulty", "medium") if current_questions else "medium"
        
        new_difficulty = self.generation_tools.adjust_difficulty(
            current_difficulty,
            avg_score
        )
        
        print(f"📊 Adaptive Difficulty: {current_difficulty} → {new_difficulty} (avg score: {avg_score:.1f})")
        
        return new_difficulty