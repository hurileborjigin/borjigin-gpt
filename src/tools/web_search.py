# src/tools/web_search.py (COMPLETE WORKING VERSION)
from tavily import TavilyClient
from typing import Dict, List, Any
from src.config.settings import settings
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class WebSearchTool:
    """Enhanced web search tool using Tavily with better result processing"""
    
    def __init__(self):
        self.client = TavilyClient(api_key=settings.tavily_api_key)
        
        # Initialize LLM for summarization
        self.llm = AzureChatOpenAI(
            azure_deployment=settings.azure_openai_deployment_name,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            temperature=0.3
        )
    
    def search_company_overview(self, company_name: str) -> Dict[str, Any]:
        """Search for comprehensive company overview"""
        
        print(f"🔍 Searching company overview for {company_name}...")
        
        query = f"{company_name} company overview products services mission business model"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            results = response.get('results', [])
            
            if not results:
                return {
                    "summary": f"No information found for {company_name}.",
                    "sources": [],
                    "raw_results_count": 0
                }
            
            print(f"   ✓ Found {len(results)} sources")
            
            # Extract full content from results
            combined_content = ""
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                content = result.get('content', '')
                url = result.get('url', '')
                
                combined_content += f"\n{'='*80}\n"
                combined_content += f"SOURCE {i}: {title}\n"
                combined_content += f"URL: {url}\n"
                combined_content += f"{'='*80}\n"
                combined_content += f"{content}\n\n"
            
            print(f"   ✓ Combined content: {len(combined_content)} characters")
            
            # Synthesize with LLM
            synthesis = self._synthesize_overview(company_name, combined_content, results)
            
            return synthesis
            
        except Exception as e:
            print(f"❌ Error searching overview: {e}")
            import traceback
            traceback.print_exc()
            return {
                "summary": f"Error researching {company_name}: {str(e)}",
                "sources": [],
                "raw_results_count": 0
            }
    
    def search_company_culture(self, company_name: str) -> Dict[str, Any]:
        """Search for company culture and work environment"""
        
        print(f"🔍 Searching company culture for {company_name}...")
        
        query = f"{company_name} company culture work environment employee experience benefits"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            results = response.get('results', [])
            
            if not results:
                return {
                    "summary": f"Limited culture information available for {company_name}.",
                    "sources": [],
                    "raw_results_count": 0
                }
            
            print(f"   ✓ Found {len(results)} sources")
            
            combined_content = ""
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                content = result.get('content', '')
                url = result.get('url', '')
                
                combined_content += f"\n{'='*80}\n"
                combined_content += f"SOURCE {i}: {title}\n"
                combined_content += f"URL: {url}\n"
                combined_content += f"{'='*80}\n"
                combined_content += f"{content}\n\n"
            
            synthesis = self._synthesize_culture(company_name, combined_content, results)
            
            return synthesis
            
        except Exception as e:
            print(f"❌ Error searching culture: {e}")
            return {
                "summary": f"Limited culture information available for {company_name}.",
                "sources": [],
                "raw_results_count": 0
            }
    
    def search_recent_news(self, company_name: str, days: int = 180) -> Dict[str, Any]:
        """Search for recent company news"""
        
        print(f"🔍 Searching recent news for {company_name}...")
        
        query = f"{company_name} latest news announcements developments 2024 2025"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            results = response.get('results', [])
            
            if not results:
                return {
                    "summary": f"No recent news found for {company_name}.",
                    "sources": [],
                    "raw_results_count": 0
                }
            
            print(f"   ✓ Found {len(results)} news items")
            
            combined_content = ""
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                content = result.get('content', '')
                url = result.get('url', '')
                
                combined_content += f"\n{'='*80}\n"
                combined_content += f"ARTICLE {i}: {title}\n"
                combined_content += f"URL: {url}\n"
                combined_content += f"{'='*80}\n"
                combined_content += f"{content}\n\n"
            
            synthesis = self._synthesize_news(company_name, combined_content, results)
            
            return synthesis
            
        except Exception as e:
            print(f"❌ Error searching news: {e}")
            return {
                "summary": f"No recent news found for {company_name}.",
                "sources": [],
                "raw_results_count": 0
            }
    
    def search_position_insights(self, company_name: str, position: str) -> Dict[str, Any]:
        """Search for position-specific insights"""
        
        print(f"🔍 Searching insights for {position} at {company_name}...")
        
        query = f"{position} role at {company_name} responsibilities requirements skills"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            results = response.get('results', [])
            
            if not results:
                return {
                    "summary": f"Limited information available for {position} at {company_name}.",
                    "sources": [],
                    "raw_results_count": 0
                }
            
            print(f"   ✓ Found {len(results)} sources")
            
            combined_content = ""
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Unknown')
                content = result.get('content', '')
                url = result.get('url', '')
                
                combined_content += f"\n{'='*80}\n"
                combined_content += f"SOURCE {i}: {title}\n"
                combined_content += f"URL: {url}\n"
                combined_content += f"{'='*80}\n"
                combined_content += f"{content}\n\n"
            
            synthesis = self._synthesize_position(company_name, position, combined_content, results)
            
            return synthesis
            
        except Exception as e:
            print(f"❌ Error searching position: {e}")
            return {
                "summary": f"Limited information available for {position} at {company_name}.",
                "sources": [],
                "raw_results_count": 0
            }
    
    def _synthesize_overview(self, company_name: str, content: str, sources: List[Dict]) -> Dict[str, Any]:
        """Synthesize company overview from raw content"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional research analyst creating company overviews for interview preparation.

Create a comprehensive, well-structured overview with these sections:

## 📊 Company Overview
- What the company does (core business, products, services)
- Industry and market position
- Company size, locations, year founded
- Key customers or clients

## 🎯 Mission & Values
- Company mission and vision
- Core values and principles
- What makes them unique

## 💼 Products & Services
- Main offerings
- Target markets
- Technology stack or approach
- Competitive advantages

## 🏆 Notable Achievements
- Market recognition (awards, rankings)
- Growth metrics
- Key partnerships or clients

**Important Guidelines:**
- Use bullet points for clarity
- Be specific and factual - cite numbers when available
- If information is limited, say so clearly
- Don't make up details
- Focus on what's relevant for interview candidates
- Keep it professional but engaging"""),
            ("user", """Company: {company_name}

Research Content:
{content}

Create a clear, well-organized company overview for interview preparation.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "company_name": company_name,
                "content": content[:15000]  # Limit to avoid token limits
            })
            
            return {
                "summary": response.content,
                "sources": [
                    {
                        "title": r.get('title', 'Unknown'),
                        "url": r.get('url', ''),
                        "score": r.get('score', 0)
                    }
                    for r in sources[:5]
                ],
                "raw_results_count": len(sources)
            }
        except Exception as e:
            print(f"❌ Error synthesizing overview: {e}")
            return {
                "summary": f"Error creating summary: {str(e)}",
                "sources": [],
                "raw_results_count": 0
            }
    
    def _synthesize_culture(self, company_name: str, content: str, sources: List[Dict]) -> Dict[str, Any]:
        """Synthesize company culture from raw content"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research analyst synthesizing company culture information for interview candidates.

Create a comprehensive culture overview with these sections:

## 🌟 Core Values & Culture
- Company values and principles
- Cultural philosophy
- What they prioritize

## 💡 Work Environment
- Office culture and atmosphere
- Remote/hybrid policies
- Team collaboration style

## 🎁 Benefits & Perks
- Employee benefits
- Wellness programs
- Work-life balance initiatives

## 📈 Growth & Development
- Learning opportunities
- Career advancement
- Training programs

## 👥 Employee Perspectives
- What employees say (if available)
- Glassdoor/review insights
- Team dynamics

**Guidelines:**
- Be honest about what you find
- Include both positives and areas of focus
- Use specific examples when available
- If limited info, say so clearly"""),
            ("user", """Company: {company_name}

Research Content:
{content}

Synthesize this into a clear culture overview.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "company_name": company_name,
                "content": content[:15000]
            })
            
            return {
                "summary": response.content,
                "sources": [
                    {
                        "title": r.get('title', 'Unknown'),
                        "url": r.get('url', ''),
                        "score": r.get('score', 0)
                    }
                    for r in sources[:5]
                ],
                "raw_results_count": len(sources)
            }
        except Exception as e:
            print(f"❌ Error synthesizing culture: {e}")
            return {
                "summary": f"Error creating summary: {str(e)}",
                "sources": [],
                "raw_results_count": 0
            }
    
    def _synthesize_news(self, company_name: str, content: str, sources: List[Dict]) -> Dict[str, Any]:
        """Synthesize recent news from raw content"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research analyst synthesizing recent company news for interview preparation.

Create a news summary with these sections:

## 📰 Recent Developments (Last 6 Months)
- Major announcements
- Product launches
- Business expansions

## 🤝 Partnerships & Collaborations
- Strategic partnerships
- Acquisitions or mergers
- New market entries

## 🚀 Innovation & Growth
- New technologies or products
- R&D initiatives
- Market expansion

## 🏅 Recognition & Awards
- Industry recognition
- Rankings or certifications
- Customer wins

**Guidelines:**
- Organize chronologically (most recent first)
- Be factual and specific
- Include dates when available
- Focus on what's relevant for candidates
- If news is limited or outdated, say so clearly"""),
            ("user", """Company: {company_name}

Recent News Content:
{content}

Create a clear, organized news summary.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "company_name": company_name,
                "content": content[:15000]
            })
            
            return {
                "summary": response.content,
                "sources": [
                    {
                        "title": r.get('title', 'Unknown'),
                        "url": r.get('url', ''),
                        "score": r.get('score', 0)
                    }
                    for r in sources[:5]
                ],
                "raw_results_count": len(sources)
            }
        except Exception as e:
            print(f"❌ Error synthesizing news: {e}")
            return {
                "summary": f"Error creating summary: {str(e)}",
                "sources": [],
                "raw_results_count": 0
            }
    
    def _synthesize_position(self, company_name: str, position: str, content: str, sources: List[Dict]) -> Dict[str, Any]:
        """Synthesize position-specific insights from raw content"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a research analyst creating role-specific insights for interview candidates.

Create a position analysis with these sections:

## 📋 Role Overview
- Key responsibilities
- Day-to-day activities
- Team structure

## 🎯 Required Skills & Qualifications
- Technical skills
- Soft skills
- Experience requirements
- Nice-to-have qualifications

## 💬 Interview Focus Areas
- Common interview topics
- Technical assessments
- Behavioral questions likely to come up

## 🌱 Growth Opportunities
- Career progression
- Learning opportunities
- Impact potential

## 💡 Preparation Tips
- What to emphasize in your application
- How to stand out
- Company-specific considerations

**Guidelines:**
- Be specific to both the role AND the company
- Provide actionable insights
- If info is limited, provide general role insights
- Focus on interview preparation"""),
            ("user", """Company: {company_name}
Position: {position}

Research Content:
{content}

Create a comprehensive position analysis.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({
                "company_name": company_name,
                "position": position,
                "content": content[:15000]
            })
            
            return {
                "summary": response.content,
                "sources": [
                    {
                        "title": r.get('title', 'Unknown'),
                        "url": r.get('url', ''),
                        "score": r.get('score', 0)
                    }
                    for r in sources[:5]
                ],
                "raw_results_count": len(sources)
            }
        except Exception as e:
            print(f"❌ Error synthesizing position: {e}")
            return {
                "summary": f"Error creating summary: {str(e)}",
                "sources": [],
                "raw_results_count": 0
            }