"""
Job Description Enhancement Service using LangGraph
Workflow: Extract Skills → Map to SFIA → Set Skill Levels
Uses OpenAI (primary) or Ollama (fallback) LLM and SFIA Knowledge Graph
"""

import os
from typing import TypedDict, List, Dict, Any, Annotated
from operator import add

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage

# Import both LLM providers
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from .sfia_km_service import get_sfia_service
from prompts.enhance_jd_prompts import (
    get_skill_extraction_prompt,
    get_jd_regeneration_system_prompt,
    format_skill_extraction_user_prompt,
    format_jd_regeneration_user_prompt
)

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
    regenerated_jd: str  # LLM-rewritten JD incorporating SFIA skills
    messages: Annotated[List, add]
    error: str
    kg_connected: bool


class JobDescriptionEnhancer:
    """
    LangGraph-based service to enhance job descriptions with SFIA skills
    Uses OpenAI (primary) or Ollama (fallback) LLM and SFIA Knowledge Graph for skill mapping
    """
    
    def __init__(self, fuseki_url: str = None, ollama_model: str = None, openai_model: str = None):
        """
        Initialize the Job Description Enhancer
        
        Args:
            fuseki_url: Fuseki server URL (defaults to FUSEKI_URL env var)
            ollama_model: Ollama model to use (defaults to OLLAMA_MODEL env var or 'llama3:latest')
            openai_model: OpenAI model to use (defaults to OPENAI_MODEL env var or 'gpt-4o-mini')
        """
        self.llm = None
        self.llm_provider = None
        
        # Check for OpenAI API key first (primary)
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        openai_model = openai_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if openai_api_key and OPENAI_AVAILABLE:
            try:
                self.llm = ChatOpenAI(
                    model=openai_model,
                    api_key=openai_api_key,
                    temperature=0.3,
                    max_tokens=4000,
                )
                # Test connection with a simple request
                self.llm.invoke("test")
                self.llm_provider = "openai"
                logger.info(f"✅ OpenAI LLM initialized: {openai_model}")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI initialization failed: {e}")
                self.llm = None
        
        # Fallback to Ollama if OpenAI not available
        if self.llm is None and OLLAMA_AVAILABLE:
            ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
            ollama_model = ollama_model or os.getenv("OLLAMA_MODEL", "llama3:latest")
            
            try:
                self.llm = ChatOllama(
                    model=ollama_model,
                    base_url=ollama_url,
                    temperature=0.3,
                )
                # Test connection
                self.llm.invoke("test")
                self.llm_provider = "ollama"
                logger.info(f"✅ Ollama LLM initialized: {ollama_model}")
            except Exception as e:
                logger.error(f"❌ Ollama connection failed: {e}")
                self.llm = None
        
        # Check if any LLM is available
        if self.llm is None:
            raise RuntimeError(
                "No LLM available. Please configure either:\n"
                "  - OPENAI_API_KEY environment variable for OpenAI, or\n"
                "  - OLLAMA_URL and ensure Ollama is running"
            )
        
        # Initialize SFIA Knowledge Service
        self.sfia_service = get_sfia_service(fuseki_url=fuseki_url)
        self.kg_connected = self.sfia_service.is_connected()
        
        if self.kg_connected:
            logger.info("✅ Knowledge Graph integration enabled")
            stats = self.sfia_service.get_knowledge_graph_stats()
            logger.info(f"   📊 KG Stats: {stats.get('total_skills', 0)} skills, {stats.get('total_categories', 0)} categories")
        else:
            logger.error("❌ Knowledge Graph not available")
            raise RuntimeError("Knowledge Graph is required but not available")
        
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
        workflow.add_node("regenerate_jd", self.regenerate_jd_node)
        
        # Define edges
        workflow.set_entry_point("extract_skills")
        workflow.add_edge("extract_skills", "map_to_sfia")
        workflow.add_edge("map_to_sfia", "set_skill_level")
        workflow.add_edge("set_skill_level", "regenerate_jd")
        workflow.add_edge("regenerate_jd", END)
        
        return workflow.compile()
    
    def extract_skills_node(self, state: EnhancementState) -> EnhancementState:
        """
        Node 1: Extract skills and keywords from job description using Ollama LLM
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with extracted keywords
        """
        logger.info("=== Node 1: Extracting Skills ===")
        
        job_description = state["job_description"]
        
        try:
            # Use Ollama LLM to extract skills
            messages = [
                SystemMessage(content=get_skill_extraction_prompt()),
                HumanMessage(content=format_skill_extraction_user_prompt(job_description))
            ]
            
            response = self.llm.invoke(messages)
            keywords_text = response.content.strip()
            
            # Parse comma-separated keywords and clean them
            raw_keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            # Clean keywords - remove LLM artifacts and keep only valid skill names
            import re
            clean_keywords = []
            for kw in raw_keywords:
                # Remove any leading text like "Here are the skills:" etc.
                if ':' in kw and len(kw.split(':')[0]) > len(kw.split(':')[1]):
                    kw = kw.split(':')[-1].strip()
                # Remove quotes
                kw = kw.replace('"', '').replace("'", "").strip()
                # Keep only reasonable length keywords (2-50 chars)
                if 2 <= len(kw) <= 50:
                    clean_keywords.append(kw)
            
            keywords = clean_keywords[:20]  # Limit to 20 keywords
            
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
        seen_codes = set()
        
        try:
            for keyword in keywords:
                # Search Knowledge Graph directly by keyword
                results = self.sfia_service.search_skills(keyword, limit=3)
                
                for skill in results:
                    code = skill.get('code', '')
                    if code and code not in seen_codes:
                        seen_codes.add(code)
                        sfia_skills.append({
                            'code': code,
                            'label': skill.get('name', ''),
                            'category': skill.get('category', ''),
                            'description': skill.get('description', ''),
                            'keyword_matched': keyword
                        })
                        logger.info(f"   ✓ Matched '{keyword}' → {code}: {skill.get('name', '')}")
            
            logger.info(f"Mapped to {len(sfia_skills)} SFIA skills")
            
            state["sfia_skills"] = sfia_skills
            state["messages"].append(f"Mapped to {len(sfia_skills)} SFIA skills via Knowledge Graph")
            
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
            seniority_level = self._detect_seniority(job_description.lower())
            
            logger.info(f"Detected seniority level: {seniority_level}")
            
            for skill in sfia_skills:
                skill_code = skill['code']
                
                # Determine appropriate level based on seniority
                assigned_level = self._assign_level(
                    seniority_level,
                    skill_code,
                    job_description
                )
                
                # Get level-specific description from Knowledge Graph
                level_description = self._get_level_description(skill_code, assigned_level)
                
                enhanced_skill = {
                    'code': skill['code'],
                    'name': skill.get('label', skill.get('name', '')),
                    'category': skill.get('category', ''),
                    'level': assigned_level,
                    'level_name': self._get_level_name(assigned_level),
                    'level_description': level_description,
                    'keyword_matched': skill.get('keyword_matched', '')
                }
                
                enhanced_skills.append(enhanced_skill)
                logger.info(f"   Set {skill['code']} → Level {assigned_level} ({self._get_level_name(assigned_level)})")
            
            state["enhanced_skills"] = enhanced_skills
            state["messages"].append(f"Assigned levels to {len(enhanced_skills)} skills")
            state["kg_connected"] = self.kg_connected
            
        except Exception as e:
            logger.error(f"Error in set_skill_level_node: {str(e)}")
            state["error"] = f"Level assignment error: {str(e)}"
            state["enhanced_skills"] = []
        
        return state
    
    def regenerate_jd_node(self, state: EnhancementState) -> EnhancementState:
        """
        Node 4: Regenerate job description incorporating SFIA skills
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with regenerated job description
        """
        logger.info("=== Node 4: Regenerating Job Description ===")
        
        job_description = state["job_description"]
        enhanced_skills = state["enhanced_skills"]
        
        if not enhanced_skills:
            logger.info("No SFIA skills to incorporate, using original JD")
            state["regenerated_jd"] = job_description
            state["messages"].append("No SFIA skills found to incorporate")
            return state
        
        try:
            # Format SFIA skills for the prompt
            skills_text = "\n".join([
                f"- {skill['name']} ({skill['code']}) - Level {skill['level']} ({skill['level_name']})"
                for skill in enhanced_skills
            ])
            
            messages = [
                SystemMessage(content=get_jd_regeneration_system_prompt()),
                HumanMessage(content=format_jd_regeneration_user_prompt(job_description, skills_text))
            ]
            
            response = self.llm.invoke(messages)
            regenerated_jd = response.content.strip()
            
            logger.info(f"Regenerated JD: {len(regenerated_jd)} characters")
            
            state["regenerated_jd"] = regenerated_jd
            state["messages"].append(f"Regenerated JD with {len(enhanced_skills)} SFIA skills")
            
        except Exception as e:
            logger.error(f"Error in regenerate_jd_node: {str(e)}")
            state["error"] = f"JD regeneration error: {str(e)}"
            state["regenerated_jd"] = job_description  # Fallback to original
        
        return state
    
    def _get_level_name(self, level: int) -> str:
        """Get the SFIA level name"""
        level_names = {
            1: "Follow",
            2: "Assist",
            3: "Apply",
            4: "Enable",
            5: "Ensure/Advise",
            6: "Initiate/Influence",
            7: "Set Strategy/Inspire/Mobilise"
        }
        return level_names.get(level, f"Level {level}")
    
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
        lead_count = sum(1 for indicator in lead_indicators if indicator in text)
        senior_count = sum(1 for indicator in senior_indicators if indicator in text)
        mid_count = sum(1 for indicator in mid_indicators if indicator in text)
        junior_count = sum(1 for indicator in junior_indicators if indicator in text)
        
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
    
    def _get_level_description(self, skill_code: str, level: int) -> str:
        """
        Get level-specific description for a skill from Knowledge Graph
        """
        try:
            levels = self.sfia_service.get_skill_levels_detail(skill_code)
            if levels and level in levels:
                desc = levels[level].get('description', '')
                if desc:
                    # Truncate if too long
                    return desc[:300] + '...' if len(desc) > 300 else desc
        except Exception as e:
            logger.debug(f"Could not get level description: {e}")
        
        # Standard SFIA level descriptions
        level_descriptions = {
            1: "Follows instructions and guidance. Learns basic principles and techniques.",
            2: "Assists with tasks under supervision. Developing practical experience.",
            3: "Applies skills independently. Takes responsibility for own work outcomes.",
            4: "Enables others. Provides guidance to less experienced colleagues.",
            5: "Ensures quality and best practices. Advises on complex issues.",
            6: "Initiates strategic decisions. Influences organizational direction.",
            7: "Sets strategy. Inspires and mobilizes teams for enterprise-wide initiatives."
        }
        
        return level_descriptions.get(level, f"Level {level} proficiency")
    
    def enhance(self, job_description: str) -> Dict[str, Any]:
        """
        Main method to enhance a job description
        
        Args:
            job_description: Raw job description text
            
        Returns:
            Dictionary containing enhanced skills, regenerated JD, and metadata
        """
        logger.info("Starting job description enhancement")
        logger.info(f"Knowledge Graph status: Connected")
        
        # Initialize state
        initial_state = {
            "job_description": job_description,
            "extracted_keywords": [],
            "sfia_skills": [],
            "enhanced_skills": [],
            "regenerated_jd": "",
            "messages": [],
            "error": "",
            "kg_connected": self.kg_connected
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
            "regenerated_jd": final_state.get("regenerated_jd", ""),
            "workflow_messages": final_state.get("messages", []),
            "knowledge_graph_connected": final_state.get("kg_connected", True)
        }
        
        logger.info(f"Enhancement complete: {result['skills_count']} skills identified")
        
        return result


# Singleton enhancer instance
_enhancer_instance = None


def create_enhancer(fuseki_url: str = None, ollama_model: str = None) -> JobDescriptionEnhancer:
    """
    Factory function to create a JobDescriptionEnhancer instance
    
    Args:
        fuseki_url: Fuseki server URL
        ollama_model: Ollama model to use
        
    Returns:
        JobDescriptionEnhancer instance
    """
    return JobDescriptionEnhancer(fuseki_url=fuseki_url, ollama_model=ollama_model)


def get_enhancer(fuseki_url: str = None, ollama_model: str = None) -> JobDescriptionEnhancer:
    """
    Get or create a singleton JobDescriptionEnhancer instance
    
    Args:
        fuseki_url: Fuseki server URL
        ollama_model: Ollama model to use
        
    Returns:
        JobDescriptionEnhancer instance
    """
    global _enhancer_instance
    
    if _enhancer_instance is None:
        _enhancer_instance = JobDescriptionEnhancer(fuseki_url=fuseki_url, ollama_model=ollama_model)
    
    return _enhancer_instance


def reset_enhancer():
    """Reset the singleton enhancer instance (useful for testing)"""
    global _enhancer_instance
    _enhancer_instance = None
