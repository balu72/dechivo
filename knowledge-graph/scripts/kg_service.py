"""
Knowledge Graph API Integration Service

This service provides a Python interface to query the Dechivo Knowledge Graph
and can be integrated into the Flask backend.
"""

from typing import List, Dict, Optional, Any
from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
import logging
from functools import lru_cache
from sparql_queries import KnowledgeGraphQueries, format_sparql_results

logger = logging.getLogger(__name__)


class KnowledgeGraphService:
    """Service for interacting with the Dechivo Knowledge Graph"""
    
    def __init__(self, endpoint_url: str = "http://localhost:3030/unified/query",
                 username: str = "admin", password: str = "admin123"):
        """
        Initialize the Knowledge Graph service
        
        Args:
            endpoint_url: SPARQL endpoint URL (default: unified dataset)
            username: Fuseki username
            password: Fuseki password
        """
        self.endpoint_url = endpoint_url
        self.username = username
        self.password = password
        self.queries = KnowledgeGraphQueries()
    
    def _execute_query(self, query: str, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Execute a SPARQL query and return formatted results
        
        Args:
            query: SPARQL query string
            use_cache: Whether to use caching for this query
            
        Returns:
            List of result dictionaries
        """
        try:
            sparql = SPARQLWrapper(self.endpoint_url)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            sparql.setHTTPAuth(BASIC)
            sparql.setCredentials(self.username, self.password)
            
            results = sparql.query().convert()
            return format_sparql_results(results)
            
        except Exception as e:
            logger.error(f"Error executing SPARQL query: {e}")
            logger.debug(f"Query that failed: {query}")
            return []
    
    def search_occupations(self, keyword: str) -> List[Dict[str, str]]:
        """
        Search for occupations by keyword
        
        Args:
            keyword: Search term
            
        Returns:
            List of matching occupations with labels and descriptions
        """
        query = self.queries.get_occupation_by_label(keyword)
        results = self._execute_query(query)
        
        # Deduplicate by label (in case same occupation appears in multiple frameworks)
        seen = set()
        unique_results = []
        for result in results:
            label = result.get('label', '').lower()
            if label not in seen:
                seen.add(label)
                unique_results.append(result)
        
        return unique_results
    
    def get_occupation_skills(self, occupation_uri: str) -> Dict[str, List[Dict]]:
        """
        Get all skills for an occupation, categorized by type
        
        Args:
            occupation_uri: URI of the occupation
            
        Returns:
            Dictionary with 'essential', 'optional', and 'required' skill lists
        """
        query = self.queries.get_skills_for_occupation(occupation_uri)
        results = self._execute_query(query)
        
        categorized = {
            'essential': [],
            'optional': [],
            'required': [],
            'all': results
        }
        
        for skill in results:
            skill_type = skill.get('skillType', 'required')
            if skill_type in categorized:
                categorized[skill_type].append(skill)
        
        return categorized
    
    def get_occupation_complete_profile(self, occupation_label: str) -> Dict[str, Any]:
        """
        Get complete profile for an occupation including skills, knowledge, abilities, etc.
        
        Args:
            occupation_label: Name of the occupation
            
        Returns:
            Complete occupation profile
        """
        # First, find the occupation URI
        occupations = self.search_occupations(occupation_label)
        
        if not occupations:
            return {
                'found': False,
                'message': f"No occupation found matching '{occupation_label}'"
            }
        
        # Use the first match (most relevant)
        occupation = occupations[0]
        occupation_uri = occupation.get('occupation', '')
        
        if not occupation_uri:
            return {
                'found': False,
                'message': 'Occupation URI not found'
            }
        
        # Get all related data
        profile = {
            'found': True,
            'occupation': occupation,
            'skills': self.get_occupation_skills(occupation_uri),
            'knowledge': self._execute_query(self.queries.get_knowledge_for_occupation(occupation_uri)),
            'abilities': self._execute_query(self.queries.get_abilities_for_occupation(occupation_uri)),
            'technologies': self._execute_query(self.queries.get_technologies_for_occupation(occupation_uri)),
            'salary_data': self._execute_query(self.queries.get_occupation_salary_data(occupation_uri)),
            'similar_occupations': self._execute_query(self.queries.find_similar_occupations(occupation_uri, min_common_skills=3))
        }
        
        return profile
    
    def find_skills_by_keyword(self, keyword: str) -> List[Dict[str, str]]:
        """
        Search for skills by keyword
        
        Args:
            keyword: Search term
            
        Returns:
            List of matching skills
        """
        query = self.queries.search_skills_by_keyword(keyword)
        return self._execute_query(query)
    
    def get_occupations_requiring_skill(self, skill_name: str) -> List[Dict[str, str]]:
        """
        Find all occupations that require a specific skill
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            List of occupations
        """
        query = self.queries.get_occupations_for_skill(skill_name)
        return self._execute_query(query)
    
    def find_similar_occupations(self, occupation_label: str, min_common_skills: int = 5) -> List[Dict[str, Any]]:
        """
        Find occupations similar to the given one
        
        Args:
            occupation_label: Name of the occupation
            min_common_skills: Minimum number of shared skills
            
        Returns:
            List of similar occupations with similarity scores
        """
        # First find the occupation URI
        occupations = self.search_occupations(occupation_label)
        
        if not occupations:
            return []
        
        occupation_uri = occupations[0].get('occupation', '')
        if not occupation_uri:
            return []
        
        query = self.queries.find_similar_occupations(occupation_uri, min_common_skills)
        similar = self._execute_query(query)
        
        # Add similarity percentage
        for occ in similar:
            common_skills = int(occ.get('commonSkills', 0))
            # Get total skills for target occupation
            target_skills = self.get_occupation_skills(occupation_uri)
            total_skills = len(target_skills.get('all', []))
            
            if total_skills > 0:
                occ['similarity_percentage'] = round((common_skills / total_skills) * 100, 1)
            else:
                occ['similarity_percentage'] = 0
        
        return similar
    
    def enrich_jd_with_skills(self, job_title: str, existing_skills: List[str] = None) -> Dict[str, Any]:
        """
        Enrich a job description with recommended skills from the knowledge graph
        
        Args:
            job_title: Job title from the JD
            existing_skills: List of skills already in the JD
            
        Returns:
            Dictionary with recommended skills and justifications
        """
        if existing_skills is None:
            existing_skills = []
        
        # Normalize existing skills for comparison
        existing_skills_lower = [s.lower().strip() for s in existing_skills]
        
        # Get occupation profile
        profile = self.get_occupation_complete_profile(job_title)
        
        if not profile.get('found'):
            return {
                'success': False,
                'message': f"No matching occupation found for '{job_title}'",
                'suggestions': []
            }
        
        # Extract skills
        skills_data = profile.get('skills', {})
        essential_skills = skills_data.get('essential', [])
        optional_skills = skills_data.get('optional', [])
        required_skills = skills_data.get('required', [])
        
        # Find missing essential skills
        missing_essential = []
        for skill in essential_skills:
            skill_label = skill.get('skillLabel', '').lower().strip()
            if skill_label and skill_label not in existing_skills_lower:
                missing_essential.append({
                    'skill': skill.get('skillLabel'),
                    'type': 'essential',
                    'reason': 'This is marked as an essential skill for this occupation'
                })
        
        # Find relevant optional skills
        suggested_optional = []
        for skill in optional_skills[:10]:  # Limit to top 10
            skill_label = skill.get('skillLabel', '').lower().strip()
            if skill_label and skill_label not in existing_skills_lower:
                suggested_optional.append({
                    'skill': skill.get('skillLabel'),
                    'type': 'optional',
                    'reason': 'Commonly associated with this occupation'
                })
        
        # Get technologies
        technologies = profile.get('technologies', [])
        tech_suggestions = []
        for tech in technologies[:5]:  # Top 5 technologies
            tech_label = tech.get('techLabel', '').lower().strip()
            if tech_label and tech_label not in existing_skills_lower:
                is_hot = tech.get('isHot', 'false') == 'true'
                reason = 'Trending technology' if is_hot else 'Commonly used technology'
                tech_suggestions.append({
                    'skill': tech.get('techLabel'),
                    'type': 'technology',
                    'reason': reason,
                    'category': tech.get('techCategory', 'General')
                })
        
        return {
            'success': True,
            'occupation': profile.get('occupation', {}),
            'missing_essential_skills': missing_essential,
            'suggested_optional_skills': suggested_optional,
            'technology_suggestions': tech_suggestions,
            'total_suggestions': len(missing_essential) + len(suggested_optional) + len(tech_suggestions),
            'framework_sources': list(set([
                s.get('framework', 'Unknown') 
                for s in essential_skills + optional_skills + required_skills 
                if 'framework' in s
            ]))
        }
    
    def calculate_skill_gap(self, current_occupation: str, target_occupation: str) -> Dict[str, Any]:
        """
        Calculate skill gap between current and target occupation
        
        Args:
            current_occupation: Current occupation name
            target_occupation: Target occupation name
            
        Returns:
            Skill gap analysis
        """
        current_profile = self.get_occupation_complete_profile(current_occupation)
        target_profile = self.get_occupation_complete_profile(target_occupation)
        
        if not current_profile.get('found') or not target_profile.get('found'):
            return {
                'success': False,
                'message': 'One or both occupations not found'
            }
        
        # Get skill sets
        current_skills = set(
            s.get('skillLabel', '').lower() 
            for s in current_profile.get('skills', {}).get('all', [])
        )
        target_skills = set(
            s.get('skillLabel', '').lower() 
            for s in target_profile.get('skills', {}).get('all', [])
        )
        
        # Calculate gaps
        skills_to_acquire = target_skills - current_skills
        transferable_skills = current_skills & target_skills
        obsolete_skills = current_skills - target_skills
        
        return {
            'success': True,
            'current_occupation': current_profile.get('occupation'),
            'target_occupation': target_profile.get('occupation'),
            'transferable_skills': list(transferable_skills),
            'skills_to_acquire': list(skills_to_acquire),
            'obsolete_skills': list(obsolete_skills),
            'skill_overlap_percentage': round(
                (len(transferable_skills) / len(target_skills) * 100) if target_skills else 0,
                1
            ),
            'total_current_skills': len(current_skills),
            'total_target_skills': len(target_skills),
            'total_to_acquire': len(skills_to_acquire)
        }


# Singleton instance for easy import
kg_service = KnowledgeGraphService()
