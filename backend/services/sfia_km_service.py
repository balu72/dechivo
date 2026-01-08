"""
SFIA Knowledge Management Service
Provides functions to query the SFIA knowledge graph using SPARQLWrapper
Enhanced with environment configuration, connection validation, and correct SFIA ontology schema
"""

import os
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SFIAKnowledgeService:
    """Service class for querying SFIA knowledge graph via SPARQL"""
    
    # Class-level cache for singleton pattern
    _instance = None
    _connection_validated = False
    
    def __init__(self, fuseki_url=None, dataset=None):
        """
        Initialize the SFIA Knowledge Service
        
        Args:
            fuseki_url: Base URL of Fuseki server (defaults to env var)
            dataset: Name of the dataset in Fuseki (defaults to env var)
        """
        # Read from environment variables with fallbacks
        self.fuseki_url = fuseki_url or os.getenv('FUSEKI_URL', 'http://localhost:3030')
        self.dataset = dataset or os.getenv('FUSEKI_DATASET', 'sfia')
        self.timeout = int(os.getenv('KG_TIMEOUT', '10'))
        self.enabled = os.getenv('KG_ENABLED', 'true').lower() == 'true'
        
        self.endpoint = f"{self.fuseki_url}/{self.dataset}/query"
        self.update_endpoint = f"{self.fuseki_url}/{self.dataset}/update"
        
        # Common prefixes used in SFIA 9 ontology
        # Note: SFIA 9 uses skos:notation for skill codes, not sfia:code
        self.prefixes = """
        PREFIX sfia: <https://rdf.sfia-online.org/9/ontology/>
        PREFIX skills: <https://rdf.sfia-online.org/9/skills/>
        PREFIX skilllevels: <https://rdf.sfia-online.org/9/skilllevels/>
        PREFIX categories: <https://rdf.sfia-online.org/9/categories/>
        PREFIX levels: <https://rdf.sfia-online.org/9/lor/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        """
        
        # Validate connection on first instantiation
        if self.enabled and not SFIAKnowledgeService._connection_validated:
            self._validate_connection()
    
    def _validate_connection(self):
        """Test connection to Fuseki and log status"""
        try:
            test_query = "SELECT (1 as ?test) WHERE {}"
            sparql = SPARQLWrapper(self.endpoint)
            sparql.setTimeout(self.timeout)
            sparql.setQuery(test_query)
            sparql.setReturnFormat(JSON)
            sparql.query().convert()
            
            SFIAKnowledgeService._connection_validated = True
            logger.info(f"✅ Knowledge Graph connected: {self.endpoint}")
            return True
        except Exception as e:
            logger.warning(f"⚠️ Knowledge Graph connection failed: {str(e)}")
            logger.warning("Falling back to mock data mode")
            self.enabled = False
            return False
    
    def is_connected(self):
        """Check if Knowledge Graph is connected and available"""
        if not self.enabled:
            return False
        return SFIAKnowledgeService._connection_validated
    
    def _execute_query(self, query):
        """
        Execute a SPARQL query with error handling
        
        Args:
            query: SPARQL query string
            
        Returns:
            Query results as dictionary
        """
        if not self.enabled:
            logger.debug("KG disabled, returning empty results")
            return {'results': {'bindings': []}}
        
        try:
            sparql = SPARQLWrapper(self.endpoint)
            sparql.setTimeout(self.timeout)
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            return results
        except Exception as e:
            logger.error(f"SPARQL query error: {str(e)}")
            # Return empty results instead of raising to allow fallback
            return {'results': {'bindings': []}}
    
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
        
        SELECT ?skill ?code ?label ?description ?category
        WHERE {{
            ?skill a sfia:Skill ;
                   skos:notation ?code ;
                   rdfs:label ?label .
            
            OPTIONAL {{ ?skill sfia:description ?description }}
            OPTIONAL {{ 
                ?skill sfia:inCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
        }}
        ORDER BY ?label
        """
        
        if limit:
            query += f"\nLIMIT {limit}"
        if offset:
            query += f"\nOFFSET {offset}"
        
        result = self._execute_query(query)
        return self._format_skills_list(result)
    
    def _format_skills_list(self, result):
        """Format SPARQL result into a clean list of skills"""
        skills = []
        seen_codes = set()
        
        for binding in result.get('results', {}).get('bindings', []):
            code = binding.get('code', {}).get('value', '')
            if code and code not in seen_codes:
                seen_codes.add(code)
                skills.append({
                    'code': code,
                    'name': binding.get('label', {}).get('value', ''),
                    'category': binding.get('category', {}).get('value', ''),
                    'description': binding.get('description', {}).get('value', '')[:200] if binding.get('description', {}).get('value') else '',
                    'uri': binding.get('skill', {}).get('value', '')
                })
        
        return skills
    
    def get_skill_by_code(self, skill_code):
        """
        Get detailed information about a skill by its code
        
        Args:
            skill_code: SFIA skill code (e.g., 'PROG', 'DTAN')
            
        Returns:
            Detailed skill information including all levels
        """
        query = f"""
        {self.prefixes}
        
        SELECT ?skill ?code ?label ?description ?category ?url
               ?levelNumber ?levelDescription
        WHERE {{
            ?skill a sfia:Skill ;
                   skos:notation "{skill_code}" ;
                   rdfs:label ?label .
            
            BIND("{skill_code}" as ?code)
            
            OPTIONAL {{ ?skill sfia:description ?description }}
            OPTIONAL {{ ?skill sfia:url ?url }}
            OPTIONAL {{ 
                ?skill sfia:inCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
            
            OPTIONAL {{
                ?skill sfia:definedAtLevel ?skillLevel .
                ?skillLevel sfia:atLevel ?levelUri .
                ?levelUri sfia:levelNumber ?levelNumber .
                ?skillLevel sfia:description ?levelDescription .
            }}
        }}
        ORDER BY ?levelNumber
        """
        
        result = self._execute_query(query)
        return self._format_skill_detail(result, skill_code)
    
    def _format_skill_detail(self, result, skill_code):
        """Format SPARQL result into a detailed skill object"""
        bindings = result.get('results', {}).get('bindings', [])
        
        if not bindings:
            return None
        
        first = bindings[0]
        skill = {
            'code': skill_code,
            'name': first.get('label', {}).get('value', ''),
            'description': first.get('description', {}).get('value', ''),
            'category': first.get('category', {}).get('value', ''),
            'url': first.get('url', {}).get('value', ''),
            'levels': {}
        }
        
        # Collect levels
        for binding in bindings:
            level_num = binding.get('levelNumber', {}).get('value')
            level_desc = binding.get('levelDescription', {}).get('value')
            if level_num and level_desc:
                skill['levels'][int(level_num)] = level_desc
        
        return skill
    
    def search_skills(self, keyword, limit=50):
        """
        Search skills by keyword in name or description
        
        Args:
            keyword: Search keyword
            limit: Maximum number of results
            
        Returns:
            List of matching skills
        """
        # First try smart search with relevance scoring
        results = self.smart_search_skills(keyword, limit)
        if results:
            return results
        
        # Fallback to basic regex search
        return self._basic_search_skills(keyword, limit)
    
    def _basic_search_skills(self, keyword, limit=50):
        """Basic regex-based skill search (fallback)"""
        import re as regex_module
        safe_keyword = regex_module.sub(r'[^a-zA-Z0-9\s\-]', '', keyword)
        safe_keyword = safe_keyword.strip()
        
        if not safe_keyword:
            return []
        
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?skill ?code ?label ?category ?description
        WHERE {{
            ?skill a sfia:Skill ;
                   skos:notation ?code ;
                   rdfs:label ?label .
            
            OPTIONAL {{ 
                ?skill sfia:skillCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
            OPTIONAL {{ ?skill sfia:skillDescription ?description }}
            OPTIONAL {{ ?skill sfia:skillNotes ?notes }}
            
            FILTER (
                regex(?label, "{safe_keyword}", "i") ||
                regex(?description, "{safe_keyword}", "i") ||
                regex(?notes, "{safe_keyword}", "i") ||
                regex(?code, "{safe_keyword}", "i")
            )
        }}
        ORDER BY ?label
        LIMIT {limit}
        """
        
        result = self._execute_query(query)
        return self._format_search_results(result)
    
    def smart_search_skills(self, keyword, limit=10):
        """
        Smart skill search with relevance scoring and keyword mapping
        
        Uses:
        1. Direct keyword-to-SFIA mapping for common terms
        2. Relevance scoring based on match location
        3. Prioritizes exact matches over partial matches
        
        Args:
            keyword: Search keyword
            limit: Maximum number of results
            
        Returns:
            List of matching skills sorted by relevance
        """
        import re as regex_module
        
        # Clean keyword
        clean_keyword = regex_module.sub(r'[^a-zA-Z0-9\s\-]', '', keyword.strip().lower())
        if not clean_keyword:
            return []
        
        # Check keyword mapping first for direct matches
        mapped_codes = self._get_mapped_skill_codes(clean_keyword)
        
        # Get all potential matches from KG
        all_matches = []
        
        # If we have mapped codes, get those skills first
        for code in mapped_codes:
            skill = self.get_skill_by_code(code)
            if skill:
                all_matches.append({
                    'code': skill['code'],
                    'name': skill['name'],
                    'category': skill.get('category', ''),
                    'description': skill.get('description', '')[:200] if skill.get('description') else '',
                    'score': 100,  # Highest priority for mapped skills
                    'match_type': 'keyword_map'
                })
        
        # Search by keyword in label and description
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?skill ?code ?label ?category ?description ?notes
        WHERE {{
            ?skill a sfia:Skill ;
                   skos:notation ?code ;
                   rdfs:label ?label .
            
            OPTIONAL {{ 
                ?skill sfia:skillCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
            OPTIONAL {{ ?skill sfia:skillDescription ?description }}
            OPTIONAL {{ ?skill sfia:skillNotes ?notes }}
        }}
        """
        
        result = self._execute_query(query)
        
        # Score each skill based on relevance
        for binding in result.get('results', {}).get('bindings', []):
            code = binding.get('code', {}).get('value', '')
            label = binding.get('label', {}).get('value', '').lower()
            desc = binding.get('description', {}).get('value', '').lower() if binding.get('description') else ''
            notes = binding.get('notes', {}).get('value', '').lower() if binding.get('notes') else ''
            
            # Skip if already in results
            if any(m['code'] == code for m in all_matches):
                continue
            
            # Calculate relevance score
            score = 0
            match_type = None
            
            # Exact label match (highest)
            if clean_keyword == label:
                score = 95
                match_type = 'exact_label'
            # Label starts with keyword
            elif label.startswith(clean_keyword):
                score = 85
                match_type = 'label_prefix'
            # Label contains keyword as whole word
            elif regex_module.search(r'\b' + regex_module.escape(clean_keyword) + r'\b', label):
                score = 75
                match_type = 'label_word'
            # Label contains keyword
            elif clean_keyword in label:
                score = 65
                match_type = 'label_partial'
            # Code matches
            elif clean_keyword.upper() == code:
                score = 90
                match_type = 'exact_code'
            # Description contains keyword as whole word
            elif desc and regex_module.search(r'\b' + regex_module.escape(clean_keyword) + r'\b', desc):
                score = 50
                match_type = 'description'
            # Notes contains keyword
            elif notes and regex_module.search(r'\b' + regex_module.escape(clean_keyword) + r'\b', notes):
                score = 40
                match_type = 'notes'
            # Partial match in description
            elif desc and clean_keyword in desc:
                score = 30
                match_type = 'description_partial'
            
            if score > 0:
                all_matches.append({
                    'code': code,
                    'name': binding.get('label', {}).get('value', ''),
                    'category': binding.get('category', {}).get('value', ''),
                    'description': desc[:200] + '...' if len(desc) > 200 else desc,
                    'score': score,
                    'match_type': match_type
                })
        
        # Sort by score descending and return top results
        all_matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top matches (remove score from output)
        return [{k: v for k, v in m.items() if k != 'score' and k != 'match_type'} 
                for m in all_matches[:limit]]
    
    def _get_mapped_skill_codes(self, keyword):
        """
        Get SFIA skill codes for common keyword mappings
        
        This provides direct mapping for commonly used terms that may not
        match SFIA skill names exactly.
        """
        # Common keyword to SFIA skill code mappings
        keyword_map = {
            # Programming & Development
            'programming': ['PROG'],
            'coding': ['PROG'],
            'software development': ['PROG', 'SWDN'],
            'software engineering': ['PROG', 'SWDN', 'SLEN'],
            'development': ['PROG'],
            'software design': ['SWDN'],
            'system design': ['DESN'],
            'systems design': ['DESN'],
            'architecture': ['ARCH', 'STPL'],
            'solution architecture': ['ARCH'],
            'enterprise architecture': ['STPL'],
            
            # Data
            'data analysis': ['DAAN'],
            'data analytics': ['DAAN'],
            'data science': ['DATS'],
            'data engineering': ['DENG'],
            'machine learning': ['MLNG', 'DATS'],
            'artificial intelligence': ['MLNG', 'DATS'],
            'ai': ['MLNG', 'DATS'],
            'ml': ['MLNG'],
            'database': ['DBDS', 'DBAD'],
            'database design': ['DBDS'],
            'database administration': ['DBAD'],
            'big data': ['DENG', 'DATS'],
            'etl': ['DENG'],
            'data warehouse': ['DENG', 'DBDS'],
            
            # Security
            'cybersecurity': ['SCTY'],
            'cyber security': ['SCTY'],
            'information security': ['SCTY'],
            'security': ['SCTY'],
            'security architecture': ['SCAD'],
            'penetration testing': ['PENT'],
            'vulnerability assessment': ['VUAS'],
            'security operations': ['SCAD', 'SCTY'],
            'threat detection': ['THIN'],
            'incident response': ['USUP'],
            'incident management': ['USUP'],
            
            # Infrastructure & Operations
            'devops': ['RELM', 'CFMG', 'DEPL'],
            'cloud': ['IFDN', 'ITOP', 'DEPL'],
            'cloud computing': ['IFDN', 'ITOP', 'DEPL'],
            'aws': ['IFDN', 'ITOP'],
            'azure': ['IFDN', 'ITOP'],
            'gcp': ['IFDN', 'ITOP'],
            'infrastructure': ['IFDN', 'ITOP'],
            'infrastructure design': ['IFDN'],
            'deployment': ['DEPL'],
            'networking': ['NTAS', 'NTDS'],
            'network': ['NTAS', 'NTDS'],
            'server': ['ITOP'],
            'system administration': ['ITOP'],
            'sysadmin': ['ITOP'],
            'kubernetes': ['IFDN', 'DEPL'],
            'docker': ['IFDN', 'DEPL'],
            'containers': ['IFDN', 'DEPL'],
            'terraform': ['IFDN', 'CFMG'],
            
            # Project & Management
            'project management': ['PRMG'],
            'program management': ['PGMG'],
            'portfolio management': ['POMG'],
            'agile': ['DLMG', 'PRMG'],
            'scrum': ['DLMG'],
            'leadership': ['PRMG', 'ITMG'],
            'team lead': ['PRMG'],
            'management': ['ITMG', 'PRMG'],
            'stakeholder management': ['RLMT'],
            'requirements': ['BCRE', 'REQM'],
            'requirements analysis': ['REQM'],
            'business analysis': ['BUAN'],
            
            # Testing & Quality
            'testing': ['TEST'],
            'qa': ['TEST'],
            'quality assurance': ['TEST'],
            'test automation': ['TEST'],
            'performance testing': ['PERF'],
            
            # Other
            'release management': ['RELM'],
            'configuration management': ['CFMG'],
            'change management': ['CHMG'],
            'service management': ['SLMO'],
            'itil': ['SLMO'],
            'documentation': ['INCA'],
            'technical writing': ['INCA'],
            'user experience': ['HCEV'],
            'ux': ['HCEV'],
            'ui': ['HCEV'],
            'automation': ['AUTY'],
        }
        
        # Check for exact match
        if keyword in keyword_map:
            return keyword_map[keyword]
        
        # Check for partial matches
        for key, codes in keyword_map.items():
            if key in keyword or keyword in key:
                return codes
        
        return []

    def _format_search_results(self, result):
        """Format SPARQL result into search results"""
        skills = []
        seen_codes = set()
        
        for binding in result.get('results', {}).get('bindings', []):
            code = binding.get('code', {}).get('value', '')
            if code and code not in seen_codes:
                seen_codes.add(code)
                desc = binding.get('description', {}).get('value', '')
                skills.append({
                    'code': code,
                    'name': binding.get('label', {}).get('value', ''),
                    'category': binding.get('category', {}).get('value', ''),
                    'description': desc[:200] + '...' if len(desc) > 200 else desc
                })
        
        return skills
    
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
        
        SELECT ?skill ?code ?label ?description
        WHERE {{
            ?skill a sfia:Skill ;
                   skos:notation ?code ;
                   rdfs:label ?label ;
                   sfia:inCategory ?categoryUri .
            
            ?categoryUri rdfs:label ?categoryLabel .
            FILTER (regex(?categoryLabel, "{category_name}", "i"))
            
            OPTIONAL {{ ?skill sfia:description ?description }}
        }}
        ORDER BY ?label
        """
        
        result = self._execute_query(query)
        return self._format_skills_list(result)
    
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
                   skos:notation ?code ;
                   rdfs:label ?label ;
                   sfia:definedAtLevel ?skillLevel .
            
            ?skillLevel sfia:atLevel ?levelUri .
            ?levelUri sfia:levelNumber {level_number} .
            
            OPTIONAL {{ 
                ?skill sfia:inCategory ?categoryUri .
                ?categoryUri rdfs:label ?category 
            }}
        }}
        ORDER BY ?category ?label
        """
        
        result = self._execute_query(query)
        return self._format_skills_list(result)
    
    def get_all_categories(self):
        """
        Get all SFIA categories
        
        Returns:
            List of categories
        """
        query = f"""
        {self.prefixes}
        
        SELECT DISTINCT ?category ?label (COUNT(DISTINCT ?skill) as ?skillCount)
        WHERE {{
            ?category a sfia:Category ;
                     rdfs:label ?label .
            
            OPTIONAL {{
                ?skill sfia:inCategory ?category .
            }}
        }}
        GROUP BY ?category ?label
        ORDER BY ?label
        """
        
        result = self._execute_query(query)
        categories = []
        
        for binding in result.get('results', {}).get('bindings', []):
            categories.append({
                'name': binding.get('label', {}).get('value', ''),
                'uri': binding.get('category', {}).get('value', ''),
                'skill_count': int(binding.get('skillCount', {}).get('value', 0))
            })
        
        return categories
    
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
        
        result = self._execute_query(query)
        levels = []
        
        for binding in result.get('results', {}).get('bindings', []):
            levels.append({
                'number': int(binding.get('levelNumber', {}).get('value', 0)),
                'name': binding.get('label', {}).get('value', ''),
                'description': binding.get('description', {}).get('value', '')
            })
        
        return levels
    
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
        
        SELECT ?levelNumber ?description
        WHERE {{
            ?skill a sfia:Skill ;
                   skos:notation "{skill_code}" ;
                   sfia:definedAtLevel ?skillLevel .
            
            ?skillLevel sfia:atLevel ?levelUri ;
                       sfia:description ?description .
            ?levelUri sfia:levelNumber ?levelNumber .
        }}
        ORDER BY ?levelNumber
        """
        
        result = self._execute_query(query)
        levels = {}
        
        for binding in result.get('results', {}).get('bindings', []):
            level_num = int(binding.get('levelNumber', {}).get('value', 0))
            levels[level_num] = {
                'description': binding.get('description', {}).get('value', ''),
            }
        
        return levels
    
    def get_related_skills(self, skill_code, limit=10):
        """
        Get skills related to a given skill (same category)
        
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
                   skos:notation "{skill_code}" ;
                   sfia:inCategory ?category .
            
            ?relatedSkill a sfia:Skill ;
                          sfia:inCategory ?category ;
                          skos:notation ?code ;
                          rdfs:label ?label .
            
            FILTER (?relatedSkill != ?skill)
        }}
        ORDER BY ?label
        LIMIT {limit}
        """
        
        result = self._execute_query(query)
        related = []
        seen_codes = set()
        
        for binding in result.get('results', {}).get('bindings', []):
            code = binding.get('code', {}).get('value', '')
            if code and code not in seen_codes:
                seen_codes.add(code)
                related.append({
                    'code': code,
                    'name': binding.get('label', {}).get('value', '')
                })
        
        return related
    
    def get_knowledge_graph_stats(self):
        """
        Get statistics about the knowledge graph
        
        Returns:
            Statistics including counts of skills, levels, categories, etc.
        """
        if not self.enabled:
            return {
                'connected': False,
                'total_triples': 0,
                'total_skills': 0,
                'total_categories': 0,
                'total_levels': 0,
                'total_skill_levels': 0
            }
        
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
        
        stats = {'connected': True}
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


# Singleton instance holder
_service_instance = None


def get_sfia_service(fuseki_url=None, dataset=None):
    """
    Factory function to create or return SFIA Knowledge Service instance
    Uses singleton pattern to reuse validated connections
    
    Args:
        fuseki_url: Base URL of Fuseki server
        dataset: Name of the dataset
        
    Returns:
        SFIAKnowledgeService instance
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = SFIAKnowledgeService(fuseki_url, dataset)
    
    return _service_instance


def reset_service():
    """Reset the singleton instance (useful for testing)"""
    global _service_instance
    _service_instance = None
    SFIAKnowledgeService._connection_validated = False
