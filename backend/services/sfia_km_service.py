"""
SFIA Knowledge Management Service
Provides functions to query the SFIA knowledge graph using SPARQLWrapper
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SFIAKnowledgeService:
    """Service class for querying SFIA knowledge graph via SPARQL"""
    
    def __init__(self, fuseki_url="http://localhost:3030", dataset="sfia"):
        """
        Initialize the SFIA Knowledge Service
        
        Args:
            fuseki_url: Base URL of Fuseki server
            dataset: Name of the dataset in Fuseki
        """
        self.endpoint = f"{fuseki_url}/{dataset}/query"
        self.update_endpoint = f"{fuseki_url}/{dataset}/update"
        
        # Common prefixes used in SFIA ontology
        self.prefixes = """
        PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        """
    
    def _execute_query(self, query):
        """
        Execute a SPARQL query
        
        Args:
            query: SPARQL query string
            
        Returns:
            Query results as dictionary
        """
        try:
            sparql = SPARQLWrapper(self.endpoint)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            return results
        except Exception as e:
            logger.error(f"SPARQL query error: {str(e)}")
            raise
    
    def get_all_skills(self, limit=None, offset=None):
        """
        Get all SFIA skills
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of skills with basic information
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?skill ?code ?label ?category
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code ?code ;
                   rdfs:label ?label .
            
            OPTIONAL {{ ?skill sfia:hasCategory ?categoryUri .
                       ?categoryUri rdfs:label ?category }}
        }}
        ORDER BY ?label
        """
        
        if limit:
            query += f"\nLIMIT {limit}"
        if offset:
            query += f"\nOFFSET {offset}"
        
        return self._execute_query(query)
    
    def get_skill_by_code(self, skill_code):
        """
        Get detailed information about a skill by its code
        
        Args:
            skill_code: SFIA skill code (e.g., 'PROG', 'DAAN')
            
        Returns:
            Detailed skill information including all levels
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?skill ?code ?label ?description ?category ?subcategory ?url
               ?level ?levelNumber ?levelDescription
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code "{skill_code}" ;
                   rdfs:label ?label .
            
            OPTIONAL {{ ?skill sfia:description ?description }}
            OPTIONAL {{ ?skill sfia:url ?url }}
            OPTIONAL {{ 
                ?skill sfia:hasCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
            OPTIONAL {{ 
                ?skill sfia:hasSubcategory ?subcategoryUri .
                ?subcategoryUri rdfs:label ?subcategory 
            }}
            
            OPTIONAL {{
                ?skill sfia:hasSkillLevel ?level .
                ?level sfia:levelNumber ?levelNumber ;
                       sfia:description ?levelDescription .
            }}
        }}
        ORDER BY ?levelNumber
        """
        
        return self._execute_query(query)
    
    def search_skills(self, keyword, limit=50):
        """
        Search skills by keyword in name or description
        
        Args:
            keyword: Search keyword
            limit: Maximum number of results
            
        Returns:
            List of matching skills
        """
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?skill ?code ?label ?category
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code ?code ;
                   rdfs:label ?label .
            
            OPTIONAL {{ 
                ?skill sfia:hasCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
            OPTIONAL {{ ?skill sfia:description ?description }}
            
            FILTER (
                regex(?label, "{keyword}", "i") ||
                regex(?description, "{keyword}", "i") ||
                regex(?category, "{keyword}", "i")
            )
        }}
        ORDER BY ?label
        LIMIT {limit}
        """
        
        return self._execute_query(query)
    
    def get_skills_by_category(self, category_name):
        """
        Get all skills in a specific category
        
        Args:
            category_name: Name of the category
            
        Returns:
            List of skills in the category
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?skill ?code ?label ?subcategory
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code ?code ;
                   rdfs:label ?label ;
                   sfia:hasCategory ?categoryUri .
            
            ?categoryUri rdfs:label "{category_name}" .
            
            OPTIONAL {{ 
                ?skill sfia:hasSubcategory ?subcategoryUri .
                ?subcategoryUri rdfs:label ?subcategory 
            }}
        }}
        ORDER BY ?subcategory, ?label
        """
        
        return self._execute_query(query)
    
    def get_skills_by_level(self, level_number):
        """
        Get all skills available at a specific level
        
        Args:
            level_number: Level number (1-7)
            
        Returns:
            List of skills available at that level
        """
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?skill ?code ?label ?category
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code ?code ;
                   rdfs:label ?label ;
                   sfia:hasSkillLevel ?skillLevel .
            
            ?skillLevel sfia:levelNumber {level_number} .
            
            OPTIONAL {{ 
                ?skill sfia:hasCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
        }}
        ORDER BY ?category, ?label
        """
        
        return self._execute_query(query)
    
    def get_all_categories(self):
        """
        Get all SFIA categories
        
        Returns:
            List of categories
        """
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?category ?label (COUNT(?skill) as ?skillCount)
        WHERE {{
            ?category a sfia:Category ;
                     rdfs:label ?label .
            
            OPTIONAL {{
                ?skill sfia:hasCategory ?category .
            }}
        }}
        GROUP BY ?category ?label
        ORDER BY ?label
        """
        
        return self._execute_query(query)
    
    def get_all_levels(self):
        """
        Get all SFIA responsibility levels
        
        Returns:
            List of levels with descriptions
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?level ?levelNumber ?label ?description
        WHERE {{
            ?level a sfia:Level ;
                   sfia:levelNumber ?levelNumber ;
                   rdfs:label ?label .
            
            OPTIONAL {{ ?level sfia:description ?description }}
        }}
        ORDER BY ?levelNumber
        """
        
        return self._execute_query(query)
    
    def get_skill_levels_detail(self, skill_code):
        """
        Get detailed level descriptions for a specific skill
        
        Args:
            skill_code: SFIA skill code
            
        Returns:
            Detailed level information for the skill
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?levelNumber ?description ?guidanceNotes
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code "{skill_code}" ;
                   sfia:hasSkillLevel ?skillLevel .
            
            ?skillLevel sfia:levelNumber ?levelNumber ;
                       sfia:description ?description .
            
            OPTIONAL {{ ?skillLevel sfia:guidanceNotes ?guidanceNotes }}
        }}
        ORDER BY ?levelNumber
        """
        
        return self._execute_query(query)
    
    def get_related_skills(self, skill_code, limit=10):
        """
        Get skills related to a given skill (same category or subcategory)
        
        Args:
            skill_code: SFIA skill code
            limit: Maximum number of results
            
        Returns:
            List of related skills
        """
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?relatedSkill ?code ?label
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code "{skill_code}" .
            
            {{
                ?skill sfia:hasCategory ?category .
                ?relatedSkill sfia:hasCategory ?category .
            }} UNION {{
                ?skill sfia:hasSubcategory ?subcategory .
                ?relatedSkill sfia:hasSubcategory ?subcategory .
            }}
            
            ?relatedSkill sfia:code ?code ;
                         rdfs:label ?label .
            
            FILTER (?relatedSkill != ?skill)
        }}
        ORDER BY ?label
        LIMIT {limit}
        """
        
        return self._execute_query(query)
    
    def get_skills_by_subcategory(self, subcategory_name):
        """
        Get all skills in a specific subcategory
        
        Args:
            subcategory_name: Name of the subcategory
            
        Returns:
            List of skills in the subcategory
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?skill ?code ?label ?category
        WHERE {{
            ?skill a sfia:Skill ;
                   sfia:code ?code ;
                   rdfs:label ?label ;
                   sfia:hasSubcategory ?subcategoryUri .
            
            ?subcategoryUri rdfs:label "{subcategory_name}" .
            
            OPTIONAL {{ 
                ?skill sfia:hasCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
        }}
        ORDER BY ?label
        """
        
        return self._execute_query(query)
    
    def get_knowledge_graph_stats(self):
        """
        Get statistics about the knowledge graph
        
        Returns:
            Statistics including counts of skills, levels, categories, etc.
        """
        queries = {
            'total_triples': """
                SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }
            """,
            'total_skills': f"""
                {self.prefixes}
                SELECT (COUNT(?skill) as ?count) WHERE {{ ?skill a sfia:Skill }}
            """,
            'total_categories': f"""
                {self.prefixes}
                SELECT (COUNT(?category) as ?count) WHERE {{ ?category a sfia:Category }}
            """,
            'total_levels': f"""
                {self.prefixes}
                SELECT (COUNT(?level) as ?count) WHERE {{ ?level a sfia:Level }}
            """,
            'total_skill_levels': f"""
                {self.prefixes}
                SELECT (COUNT(?skillLevel) as ?count) WHERE {{ ?skillLevel a sfia:SkillLevel }}
            """
        }
        
        stats = {}
        for key, query in queries.items():
            try:
                result = self._execute_query(query)
                count = result['results']['bindings'][0]['count']['value']
                stats[key] = int(count)
            except Exception as e:
                logger.error(f"Error getting {key}: {str(e)}")
                stats[key] = 0
        
        return stats
    
    def custom_query(self, sparql_query):
        """
        Execute a custom SPARQL query
        
        Args:
            sparql_query: Custom SPARQL query string
            
        Returns:
            Query results
        """
        # Add prefixes if not already in query
        if 'PREFIX' not in sparql_query.upper():
            sparql_query = self.prefixes + "\n" + sparql_query
        
        return self._execute_query(sparql_query)


# Convenience function to create service instance
def get_sfia_service(fuseki_url="http://localhost:3030", dataset="sfia"):
    """
    Factory function to create SFIA Knowledge Service instance
    
    Args:
        fuseki_url: Base URL of Fuseki server
        dataset: Name of the dataset
        
    Returns:
        SFIAKnowledgeService instance
    """
    return SFIAKnowledgeService(fuseki_url, dataset)
