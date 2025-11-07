# Create a script to verify structure
# verify_structure.py

import os
from pathlib import Path

def verify_structure():
    """Verify all files are in place"""
    
    required_files = [
        "app.py",
        ".env",
        ".gitignore",
        "pyproject.toml",
        ".streamlit/config.toml",
        
        # Config
        "src/config/__init__.py",
        "src/config/settings.py",
        
        # Utils
        "src/utils/__init__.py",
        "src/utils/document_parser.py",
        "src/utils/text_processing.py",
        
        # Memory
        "src/memory/__init__.py",
        "src/memory/long_term_memory.py",
        "src/memory/short_term_memory.py",
        "src/memory/company_research_cache.py",
        
        # Tools
        "src/tools/__init__.py",
        "src/tools/web_search.py",
        "src/tools/retrieval_tools.py",
        "src/tools/analysis_tools.py",
        "src/tools/generation_tools.py",
        
        # Agents
        "src/agents/__init__.py",
        "src/agents/state.py",
        "src/agents/nodes.py",
        "src/agents/graph.py",
        "src/agents/mock_interview.py",
        "src/agents/orchestrator.py",
        
        # UI
        "src/ui/__init__.py",
        "src/ui/sidebar.py",
        "src/ui/utils.py",
        "src/ui/pages/home.py",
        "src/ui/pages/profile_setup.py",
        "src/ui/pages/preparation_mode.py",
        "src/ui/pages/practice_mode.py",
        "src/ui/pages/mock_interview.py",
        "src/ui/pages/analytics.py",
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for f in missing_files:
            print(f"   - {f}")
        return False
    else:
        print("✅ All files in place!")
        return True

if __name__ == "__main__":
    verify_structure()