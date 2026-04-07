"""Service for interacting with Google Gemini API."""
import re
import google.generativeai as genai
from app.config import settings
from typing import Dict, List, Optional


class GeminiService:
    """Service for Gemini AI interactions."""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def _build_context(self, tree_structure: str, files: List[Dict]) -> str:
        """Build context string from repository structure and files."""
        context_parts = [
            "=== REPOSITORY STRUCTURE ===\n",
            tree_structure,
            "\n\n=== FILE CONTENTS ===\n\n"
        ]
        
        for file_data in files:
            context_parts.append(f"--- File: {file_data['path']} ---\n")
            context_parts.append(file_data['content'])
            context_parts.append("\n\n")
        
        return "".join(context_parts)
    
    def analyze_codebase(self, tree_structure: str, files: List[Dict]) -> Dict[str, str]:
        """Analyze codebase and return structured explanations."""
        context = self._build_context(tree_structure, files)
        
        prompt = f"""You are an expert software architect analyzing a codebase. Based on the repository structure and file contents below, provide a comprehensive analysis in the following sections:

1. **Architecture Overview**: Explain the overall architecture, design patterns, technology stack, and how the application is structured.

2. **Folder Structure**: Explain the purpose of major directories and how the codebase is organized.

3. **API Flow**: Identify and explain API endpoints, routes, request/response patterns, authentication mechanisms, and API architecture if present.

4. **Database/Models**: Identify and explain database schemas, data models, ORM usage, entity relationships, and data persistence patterns if present.

If any section is not applicable (e.g., no API or no database), state that clearly.

Repository Context:
{context}

Provide your analysis in a clear, structured format. Use markdown formatting for better readability."""

        try:
            response = self.model.generate_content(prompt)
            analysis_text = response.text
            
            # Parse the response into sections
            sections = self._parse_analysis_sections(analysis_text)
            
            return {
                'architecture': sections.get('architecture', 'No architecture information available.'),
                'folder_structure': sections.get('folder_structure', 'No folder structure explanation available.'),
                'api_flow': sections.get('api_flow', 'No API information available.'),
                'db_models': sections.get('db_models', 'No database/model information available.'),
                'raw_analysis': analysis_text
            }
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def _parse_analysis_sections(self, text: str) -> Dict[str, str]:
        """Parse analysis text into sections."""
        sections = {}
        
        # Try to extract sections by common headers
        section_patterns = {
            'architecture': r'(?i)(?:##?\s*)?(?:Architecture\s*Overview|Architecture)[\s\S]*?(?=##?\s*(?:Folder|API|Database|$))',
            'folder_structure': r'(?i)(?:##?\s*)?(?:Folder\s*Structure|Directory\s*Structure)[\s\S]*?(?=##?\s*(?:API|Database|Architecture|$))',
            'api_flow': r'(?i)(?:##?\s*)?(?:API\s*Flow|API\s*Endpoints|API\s*Architecture)[\s\S]*?(?=##?\s*(?:Database|Architecture|Folder|$))',
            'db_models': r'(?i)(?:##?\s*)?(?:Database|DB\s*Models|Data\s*Models|Models)[\s\S]*?(?=##?\s*(?:API|Architecture|Folder|$))'
        }
        
        for key, pattern in section_patterns.items():
            match = re.search(pattern, text)
            if match:
                sections[key] = match.group(0).strip()
        
        # If parsing failed, return raw text in architecture
        if not sections:
            sections['architecture'] = text
        
        return sections
    
    def generate_readme(self, analysis: Dict[str, str], tree_structure: str, files: List[Dict]) -> str:
        """Generate a comprehensive README.md from analysis."""
        context = self._build_context(tree_structure, files)
        
        analysis_summary = f"""
Architecture: {analysis.get('architecture', 'N/A')}
Folder Structure: {analysis.get('folder_structure', 'N/A')}
API Flow: {analysis.get('api_flow', 'N/A')}
Database/Models: {analysis.get('db_models', 'N/A')}
"""
        
        prompt = f"""You are an expert technical writer. Based on the codebase analysis and repository context below, generate a comprehensive, professional README.md file.

The README should include:
1. Project title and description
2. Features
3. Technology stack
4. Installation/setup instructions
5. Usage examples
6. Project structure overview
7. API documentation (if applicable)
8. Database schema (if applicable)
9. Contributing guidelines (optional)
10. License information (if available)

Use the analysis provided and the actual codebase context to write accurate, helpful documentation.

Analysis Summary:
{analysis_summary}

Repository Context:
{context}

Generate a well-formatted README.md in markdown format."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def answer_question(self, question: str, tree_structure: str, files: List[Dict], analysis: Optional[Dict[str, str]] = None) -> str:
        """Answer a question about the codebase."""
        context = self._build_context(tree_structure, files)
        
        analysis_context = ""
        if analysis:
            analysis_context = f"""
Previous Analysis Summary:
- Architecture: {analysis.get('architecture', 'N/A')[:500]}
- API Flow: {analysis.get('api_flow', 'N/A')[:500]}
- Database/Models: {analysis.get('db_models', 'N/A')[:500]}
"""
        
        prompt = f"""You are an expert codebase analyst. Answer the following question about this codebase based on the repository structure and file contents provided.

Question: {question}

{analysis_context}

Repository Context:
{context}

Provide a clear, detailed answer. If the question cannot be answered from the provided context, state that clearly. Use code examples from the files when relevant."""

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
