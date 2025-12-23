"""
Job Description Enhancement Service using LangGraph
Workflow: Extract Skills → Map to SFIA → Set Skill Levels
"""

import os
import re
from typing import TypedDict, List, Dict, Any, Annotated
from operator import add

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from .sfia_km_service import get_sfia_service

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Define the state structure for the graph
class EnhancementState(TypedDict):
    """State object for the job description enhancement workflow"""
    job_description: str
    extracted_keywords: List[str]
    sfia_skills: List[Dict[str, Any]]
    enhanced_skills: List[Dict[str, Any]]
    messages: Annotated[List, add]
    error: str


class JobDescriptionEnhancer:
    """
    LangGraph-based service to enhance job descriptions with SFIA skills
    """
    
    def __init__(self, openai_api_key: str = None, fuseki_url: str = "http://localhost:3030"):
        """
        Initialize the Job Description Enhancer
        
        Args:
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            fuseki_url: Fuseki server URL
        """
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not provided. Service may not function properly.")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            api_key=self.api_key
        ) if self.api_key else None
        
        # Initialize SFIA Knowledge Service
        self.sfia_service = get_sfia_service(fuseki_url=fuseki_url)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        
        Returns:
            Compiled StateGraph
        """
        workflow = StateGraph(EnhancementState)
        
        # Add nodes
        workflow.add_node("extract_skills", self.extract_skills_node)
        workflow.add_node("map_to_sfia", self.map_to_sfia_node)
        workflow.add_node("set_skill_level", self.set_skill_level_node)
        
        # Define edges
        workflow.set_entry_point("extract_skills")
        workflow.add_edge("extract_skills", "map_to_sfia")
        workflow.add_edge("map_to_sfia", "set_skill_level")
        workflow.add_edge("set_skill_level", END)
        
        return workflow.compile()
    
    def extract_skills_node(self, state: EnhancementState) -> EnhancementState:
        """
        Node 1: Extract skills and keywords from job description using LLM
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with extracted keywords
        """
        logger.info("=== Node 1: Extracting Skills ===")
        
        job_description = state["job_description"]
        
        try:
            if not self.llm:
                # Fallback: Simple keyword extraction without LLM
                logger.warning("LLM not available, using fallback keyword extraction")
                keywords = self._fallback_keyword_extraction(job_description)
            else:
                # Use LLM to extract skills
                system_prompt = """You are an expert at analyzing job descriptions and extracting technical skills, 
                competencies, and required capabilities. Extract all relevant skills mentioned in the job description.
                
                Focus on:
                - Technical skills (programming languages, tools, technologies)
                - Professional competencies (project management, communication, leadership)
                - Domain expertise (data analysis, software development, cybersecurity, etc.)
                - Soft skills when explicitly mentioned
                
                Return ONLY a comma-separated list of skill keywords, no explanations."""
                
                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=f"Extract skills from this job description:\n\n{job_description}")
                ]
                
                response = self.llm.invoke(messages)
                keywords_text = response.content.strip()
                
                # Parse comma-separated keywords
                keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            logger.info(f"Extracted {len(keywords)} keywords: {keywords}")
            
            state["extracted_keywords"] = keywords
            state["messages"].append(f"Extracted {len(keywords)} skill keywords")
            
        except Exception as e:
            logger.error(f"Error in extract_skills_node: {str(e)}")
            state["error"] = f"Skill extraction error: {str(e)}"
            state["extracted_keywords"] = []
        
        return state
    
    def map_to_sfia_node(self, state: EnhancementState) -> EnhancementState:
        """
        Node 2: Map extracted keywords to SFIA skills using knowledge graph
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with mapped SFIA skills
        """
        logger.info("=== Node 2: Mapping to SFIA Skills ===")
        
        keywords = state["extracted_keywords"]
        sfia_skills = []
        
        try:
            for keyword in keywords:
                # Search SFIA knowledge graph for matching skills
                results = self.sfia_service.search_skills(keyword, limit=3)
                
                if results and results['results']['bindings']:
                    for binding in results['results']['bindings']:
                        skill = {
                            'code': binding.get('code', {}).get('value', ''),
                            'label': binding.get('label', {}).get('value', ''),
                            'category': binding.get('category', {}).get('value', ''),
                            'keyword_matched': keyword,
                            'uri': binding.get('skill', {}).get('value', '')
                        }
                        
                        # Avoid duplicates
                        if not any(s['code'] == skill['code'] for s in sfia_skills):
                            sfia_skills.append(skill)
                            logger.info(f"Matched '{keyword}' → {skill['code']}: {skill['label']}")
            
            logger.info(f"Mapped to {len(sfia_skills)} SFIA skills")
            
            state["sfia_skills"] = sfia_skills
            state["messages"].append(f"Mapped to {len(sfia_skills)} SFIA skills")
            
        except Exception as e:
            logger.error(f"Error in map_to_sfia_node: {str(e)}")
            state["error"] = f"SFIA mapping error: {str(e)}"
            state["sfia_skills"] = []
        
        return state
    
    def set_skill_level_node(self, state: EnhancementState) -> EnhancementState:
        """
        Node 3: Determine appropriate skill levels based on job description context
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with skill levels assigned
        """
        logger.info("=== Node 3: Setting Skill Levels ===")
        
        job_description = state["job_description"]
        sfia_skills = state["sfia_skills"]
        enhanced_skills = []
        
        try:
            # Detect seniority indicators in job description
            jd_lower = job_description.lower()
            seniority_level = self._detect_seniority(jd_lower)
            
            logger.info(f"Detected seniority level: {seniority_level}")
            
            for skill in sfia_skills:
                skill_code = skill['code']
                
                # Get detailed skill information including level descriptions
                skill_details = self.sfia_service.get_skill_by_code(skill_code)
                
                # Determine appropriate level based on seniority
                assigned_level = self._assign_level(
                    seniority_level,
                    skill_code,
                    job_description
                )
                
                # Get level-specific description
                level_description = self._get_level_description(
                    skill_details,
                    assigned_level
                )
                
                enhanced_skill = {
                    'code': skill['code'],
                    'label': skill['label'],
                    'category': skill['category'],
                    'level': assigned_level,
                    'level_description': level_description,
                    'keyword_matched': skill['keyword_matched']
                }
                
                enhanced_skills.append(enhanced_skill)
                logger.info(f"Set {skill['code']} → Level {assigned_level}")
            
            state["enhanced_skills"] = enhanced_skills
            state["messages"].append(f"Assigned levels to {len(enhanced_skills)} skills")
            
        except Exception as e:
            logger.error(f"Error in set_skill_level_node: {str(e)}")
            state["error"] = f"Level assignment error: {str(e)}"
            state["enhanced_skills"] = sfia_skills  # Fallback to skills without levels
        
        return state
    
    def _fallback_keyword_extraction(self, text: str) -> List[str]:
        """
        Fallback method for keyword extraction without LLM
        Uses simple pattern matching and common skill keywords
        """
        # Common technical and professional skill keywords
        skill_patterns = [
            r'\b(python|java|javascript|typescript|c\+\+|ruby|go|rust|php|swift)\b',
            r'\b(data\s*analysis|machine\s*learning|ai|analytics)\b',
            r'\b(project\s*management|agile|scrum|devops)\b',
            r'\b(cloud|aws|azure|gcp|docker|kubernetes)\b',
            r'\b(database|sql|nosql|mongodb|postgresql)\b',
            r'\b(web\s*development|frontend|backend|fullstack)\b',
            r'\b(testing|qa|quality\s*assurance|automation)\b',
            r'\b(security|cybersecurity|infosec)\b',
            r'\b(leadership|management|communication)\b',
            r'\b(api|rest|graphql|microservices)\b'
        ]
        
        keywords = []
        text_lower = text.lower()
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.extend(matches)
        
        # Remove duplicates and clean up
        keywords = list(set(k.strip() for k in keywords if k.strip()))
        
        return keywords[:20]  # Limit to top 20
    
    def _detect_seniority(self, text: str) -> str:
        """
        Detect seniority level from job description text
        
        Returns:
            'junior', 'mid', 'senior', or 'lead'
        """
        # Seniority indicators
        junior_indicators = ['junior', 'entry', 'graduate', '0-2 years', 'beginner']
        mid_indicators = ['mid-level', 'intermediate', '3-5 years', 'experienced']
        senior_indicators = ['senior', 'principal', '5+ years', 'expert', '7+ years']
        lead_indicators = ['lead', 'architect', 'manager', 'head', 'director', 'principal']
        
        # Count matches
        text_lower = text.lower()
        
        lead_count = sum(1 for indicator in lead_indicators if indicator in text_lower)
        senior_count = sum(1 for indicator in senior_indicators if indicator in text_lower)
        mid_count = sum(1 for indicator in mid_indicators if indicator in text_lower)
        junior_count = sum(1 for indicator in junior_indicators if indicator in text_lower)
        
        # Determine seniority based on counts
        if lead_count > 0:
            return 'lead'
        elif senior_count > 0:
            return 'senior'
        elif mid_count > 0:
            return 'mid'
        elif junior_count > 0:
            return 'junior'
        else:
            return 'mid'  # Default to mid-level
    
    def _assign_level(self, seniority: str, skill_code: str, job_description: str) -> int:
        """
        Assign SFIA level (1-7) based on seniority
        
        SFIA Levels:
        1: Follow - Basic understanding
        2: Assist - Limited experience
        3: Apply - Experienced practitioner
        4: Enable - Specialist, guides others
        5: Ensure - Expert, ensures quality
        6: Initiate - Senior expert, strategic
        7: Set strategy - Leader, enterprise-wide
        """
        # Base level mapping
        level_mapping = {
            'junior': 2,
            'mid': 4,
            'senior': 5,
            'lead': 6
        }
        
        base_level = level_mapping.get(seniority, 4)
        
        # Adjust based on context in job description
        jd_lower = job_description.lower()
        
        # Leadership indicators increase level
        if any(word in jd_lower for word in ['lead', 'manage', 'strategic', 'architect']):
            base_level = min(base_level + 1, 7)
        
        # Mentoring/teaching increases level
        if any(word in jd_lower for word in ['mentor', 'train', 'guide', 'coach']):
            base_level = min(base_level + 1, 7)
        
        return base_level
    
    def _get_level_description(self, skill_details: Dict, level: int) -> str:
        """
        Extract level-specific description from skill details
        """
        if not skill_details or 'results' not in skill_details:
            return f"Level {level} proficiency"
        
        bindings = skill_details['results']['bindings']
        
        for binding in bindings:
            level_number = binding.get('levelNumber', {}).get('value')
            if level_number and int(level_number) == level:
                description = binding.get('levelDescription', {}).get('value', '')
                if description:
                    # Truncate if too long
                    return description[:200] + '...' if len(description) > 200 else description
        
        return f"Level {level} proficiency"
    
    def enhance(self, job_description: str) -> Dict[str, Any]:
        """
        Main method to enhance a job description
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Dictionary containing enhanced skills and metadata
        """
        logger.info("Starting job description enhancement")
        
        # Initialize state
        initial_state = {
            "job_description": job_description,
            "extracted_keywords": [],
            "sfia_skills": [],
            "enhanced_skills": [],
            "messages": [],
            "error": ""
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Format output
        result = {
            "success": not final_state.get("error"),
            "error": final_state.get("error", ""),
            "extracted_keywords": final_state.get("extracted_keywords", []),
            "skills_count": len(final_state.get("enhanced_skills", [])),
            "skills": final_state.get("enhanced_skills", []),
            "workflow_messages": final_state.get("messages", [])
        }
        
        logger.info(f"Enhancement complete: {result['skills_count']} skills identified")
        
        return result


# Convenience function
def create_enhancer(openai_api_key: str = None, fuseki_url: str = "http://localhost:3030") -> JobDescriptionEnhancer:
    """
    Factory function to create a JobDescriptionEnhancer instance
    
    Args:
        openai_api_key: OpenAI API key
        fuseki_url: Fuseki server URL
        
    Returns:
        JobDescriptionEnhancer instance
    """
    return JobDescriptionEnhancer(openai_api_key=openai_api_key, fuseki_url=fuseki_url)
