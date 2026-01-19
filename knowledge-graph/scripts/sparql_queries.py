"""
Common SPARQL Query Templates for Dechivo Knowledge Graph

This module provides pre-built SPARQL queries for common operations
on the unified Dechivo knowledge graph.
"""

from typing import List, Dict, Optional


class KnowledgeGraphQueries:
    """Collection of SPARQL query templates"""
    
    @staticmethod
    def get_occupation_by_label(occupation_label: str) -> str:
        """
        Find occupation by label/name
        
        Args:
            occupation_label: The occupation name to search for
            
        Returns:
            SPARQL query string
        """
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX dv: <http://dechivo.com/ontology/>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX sg: <http://data.skillsframework.sg/>
        PREFIX ca-occ: <http://data.canada.ca/occupation/>
        
        SELECT DISTINCT ?occupation ?label ?description ?framework
        WHERE {{
            ?occupation rdfs:label ?label .
            OPTIONAL {{ ?occupation dcterms:description ?description }}
            OPTIONAL {{ ?occupation dv:fromFramework ?framework }}
            
            FILTER(CONTAINS(LCASE(STR(?label)), LCASE("{occupation_label}")))
        }}
        LIMIT 50
        """
    
    @staticmethod
    def get_skills_for_occupation(occupation_uri: str) -> str:
        """
        Get all skills required for an occupation
        
        Args:
            occupation_uri: URI of the occupation
            
        Returns:
            SPARQL query string
        """
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX sg: <http://data.skillsframework.sg/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT DISTINCT ?skill ?skillLabel ?skillType ?importance
        WHERE {{
            <{occupation_uri}> ?relation ?skill .
            ?skill rdfs:label ?skillLabel .
            
            # Determine skill type (essential/optional/required)
            OPTIONAL {{
                BIND(
                    IF(?relation = esco:hasEssentialSkill, "essential",
                    IF(?relation = esco:hasOptionalSkill, "optional",
                    IF(?relation = onet:requiresSkill, "required",
                    IF(?relation = sg:requiresSkill, "required",
                    "unknown")))) AS ?skillType
                )
            }}
            
            OPTIONAL {{ <{occupation_uri}> dv:hasImportance ?importance }}
            
            # Filter to only skill-related relationships
            FILTER(?relation IN (
                esco:hasEssentialSkill,
                esco:hasOptionalSkill,
                onet:requiresSkill,
                sg:requiresSkill,
                dv:requiresSkill
            ))
        }}
        ORDER BY DESC(?importance) ?skillLabel
        """
    
    @staticmethod
    def get_knowledge_for_occupation(occupation_uri: str) -> str:
        """Get knowledge areas required for an occupation"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT DISTINCT ?knowledge ?knowledgeLabel ?knowledgeGroup
        WHERE {{
            <{occupation_uri}> ?relation ?knowledge .
            ?knowledge rdfs:label ?knowledgeLabel .
            
            OPTIONAL {{ ?knowledge onet:knowledgeGroup ?knowledgeGroup }}
            
            FILTER(?relation IN (onet:requiresKnowledge, dv:requiresKnowledge))
        }}
        ORDER BY ?knowledgeGroup ?knowledgeLabel
        """
    
    @staticmethod
    def get_abilities_for_occupation(occupation_uri: str) -> str:
        """Get abilities required for an occupation"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT DISTINCT ?ability ?abilityLabel ?abilityGroup
        WHERE {{
            <{occupation_uri}> ?relation ?ability .
            ?ability rdfs:label ?abilityLabel .
            
            OPTIONAL {{ ?ability onet:abilityGroup ?abilityGroup }}
            
            FILTER(?relation IN (onet:requiresAbility, dv:requiresAbility))
        }}
        ORDER BY ?abilityGroup ?abilityLabel
        """
    
    @staticmethod
    def get_technologies_for_occupation(occupation_uri: str) -> str:
        """Get technologies used in an occupation (O*NET data)"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT DISTINCT ?technology ?techLabel ?techCategory ?isHot
        WHERE {{
            <{occupation_uri}> ?relation ?technology .
            ?technology rdfs:label ?techLabel .
            
            OPTIONAL {{ ?technology onet:technologyCategory ?techCategory }}
            OPTIONAL {{ ?technology onet:hotTechnology ?isHot }}
            
            FILTER(?relation IN (onet:usesTechnology, dv:usesTechnology))
        }}
        ORDER BY DESC(?isHot) ?techCategory ?techLabel
        """
    
    @staticmethod
    def find_similar_occupations(occupation_uri: str, min_common_skills: int = 5) -> str:
        """
        Find occupations similar to the given one based on shared skills
        
        Args:
            occupation_uri: URI of the occupation
            min_common_skills: Minimum number of shared skills
            
        Returns:
            SPARQL query string
        """
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX sg: <http://data.skillsframework.sg/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT ?similarOcc ?occLabel (COUNT(DISTINCT ?sharedSkill) as ?commonSkills)
        WHERE {{
            # Get skills of target occupation
            <{occupation_uri}> ?rel1 ?sharedSkill .
            
            # Find other occupations with the same skills
            ?similarOcc ?rel2 ?sharedSkill .
            ?similarOcc rdfs:label ?occLabel .
            
            # Filter to skill relationships only
            FILTER(?rel1 IN (
                esco:hasEssentialSkill, esco:hasOptionalSkill,
                onet:requiresSkill, sg:requiresSkill, dv:requiresSkill
            ))
            
            FILTER(?rel2 IN (
                esco:hasEssentialSkill, esco:hasOptionalSkill,
                onet:requiresSkill, sg:requiresSkill, dv:requiresSkill
            ))
            
            # Exclude the target occupation itself
            FILTER(?similarOcc != <{occupation_uri}>)
        }}
        GROUP BY ?similarOcc ?occLabel
        HAVING (COUNT(DISTINCT ?sharedSkill) >= {min_common_skills})
        ORDER BY DESC(?commonSkills)
        LIMIT 20
        """
    
    @staticmethod
    def search_skills_by_keyword(keyword: str) -> str:
        """Search for skills by keyword"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT DISTINCT ?skill ?skillLabel ?description ?framework
        WHERE {{
            ?skill a ?skillType .
            ?skill rdfs:label ?skillLabel .
            
            OPTIONAL {{ ?skill dcterms:description ?description }}
            OPTIONAL {{ ?skill dv:fromFramework ?framework }}
            
            FILTER(?skillType IN (esco:Skill, dv:Skill))
            
            FILTER(
                CONTAINS(LCASE(STR(?skillLabel)), LCASE("{keyword}")) ||
                CONTAINS(LCASE(STR(?description)), LCASE("{keyword}"))
            )
        }}
        LIMIT 50
        """
    
    @staticmethod
    def get_occupations_for_skill(skill_label: str) -> str:
        """Find all occupations that require a specific skill"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX sg: <http://data.skillsframework.sg/>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT DISTINCT ?occupation ?occLabel ?skillType
        WHERE {{
            ?skill rdfs:label ?skillLabel .
            ?occupation ?relation ?skill .
            ?occupation rdfs:label ?occLabel .
            
            BIND(
                IF(?relation = esco:hasEssentialSkill, "essential",
                IF(?relation = esco:hasOptionalSkill, "optional",
                "required")) AS ?skillType
            )
            
            FILTER(LCASE(STR(?skillLabel)) = LCASE("{skill_label}"))
            
            FILTER(?relation IN (
                esco:hasEssentialSkill, esco:hasOptionalSkill,
                onet:requiresSkill, sg:requiresSkill, dv:requiresSkill
            ))
        }}
        ORDER BY ?skillType ?occLabel
        LIMIT 100
        """
    
    @staticmethod
    def get_occupation_salary_data(occupation_uri: str) -> str:
        """Get salary information for an occupation (O*NET data)"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX schema: <http://schema.org/>
        PREFIX onet: <http://data.onetcenter.org/>
        
        SELECT ?occupation ?label ?medianSalary ?salary10th ?salary90th ?jobOutlook
        WHERE {{
            <{occupation_uri}> rdfs:label ?label .
            
            OPTIONAL {{ <{occupation_uri}> schema:baseSalary ?medianSalary }}
            OPTIONAL {{ <{occupation_uri}> onet:salary10thPercentile ?salary10th }}
            OPTIONAL {{ <{occupation_uri}> onet:salary90thPercentile ?salary90th }}
            OPTIONAL {{ <{occupation_uri}> onet:jobOutlook ?jobOutlook }}
            
            BIND(<{occupation_uri}> AS ?occupation)
        }}
        """
    
    @staticmethod
    def get_skill_proficiency_levels(occupation_uri: str) -> str:
        """Get skill proficiency levels (Singapore data)"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX sg: <http://data.skillsframework.sg/>
        
        SELECT DISTINCT ?skill ?skillLabel ?proficiencyLevel
        WHERE {{
            <{occupation_uri}> sg:requiresSkill ?skill .
            <{occupation_uri}> sg:proficiencyLevel ?proficiencyLevel .
            ?skill rdfs:label ?skillLabel .
        }}
        ORDER BY DESC(?proficiencyLevel) ?skillLabel
        """
    
    @staticmethod
    def get_framework_coverage(occupation_label: str) -> str:
        """Check which frameworks contain data for a specific occupation"""
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dv: <http://dechivo.com/ontology/>
        
        SELECT ?occupation ?label ?framework
        WHERE {{
            GRAPH ?g {{
                ?occupation rdfs:label ?label .
                FILTER(LCASE(STR(?label)) = LCASE("{occupation_label}"))
            }}
            
            BIND(
                IF(CONTAINS(STR(?g), "/ca"), "Canada",
                IF(CONTAINS(STR(?g), "/esco"), "ESCO",
                IF(CONTAINS(STR(?g), "/onet"), "O*NET",
                IF(CONTAINS(STR(?g), "/sg"), "Singapore",
                "Unknown")))) AS ?framework
            )
        }}
        """
    
    @staticmethod
    def aggregate_occupation_data(occupation_label: str) -> str:
        """
        Aggregate data for an occupation from all frameworks
        This returns a comprehensive view combining data from all sources
        """
        return f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX sg: <http://data.skillsframework.sg/>
        PREFIX schema: <http://schema.org/>
        
        SELECT DISTINCT ?occupation ?label ?description ?framework ?salary ?jobOutlook
        WHERE {{
            ?occupation rdfs:label ?label .
            
            OPTIONAL {{ ?occupation dcterms:description ?description }}
            OPTIONAL {{ ?occupation schema:baseSalary ?salary }}
            OPTIONAL {{ ?occupation onet:jobOutlook ?jobOutlook }}
            
            # Determine framework from namespace
            BIND(
                IF(CONTAINS(STR(?occupation), "europa.eu/esco"), "ESCO",
                IF(CONTAINS(STR(?occupation), "onetcenter.org"), "O*NET",
                IF(CONTAINS(STR(?occupation), "skillsframework.sg"), "Singapore",
                IF(CONTAINS(STR(?occupation), "canada.ca"), "Canada",
                "Unknown")))) AS ?framework
            )
            
            FILTER(LCASE(STR(?label)) = LCASE("{occupation_label}"))
        }}
        """
    
    @staticmethod
    def count_entities_by_framework() -> str:
        """Get statistics on entity counts per framework"""
        return """
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX esco: <http://data.europa.eu/esco/>
        PREFIX onet: <http://data.onetcenter.org/>
        PREFIX sg: <http://data.skillsframework.sg/>
        PREFIX ca-occ: <http://data.canada.ca/occupation/>
        
        SELECT ?framework (COUNT(DISTINCT ?occupation) AS ?occupationCount)
        WHERE {
            GRAPH ?g {
                ?occupation a ?type .
                FILTER(?type IN (esco:Occupation, onet:Occupation, sg:Occupation))
            }
            
            BIND(
                IF(CONTAINS(STR(?g), "/ca"), "Canada",
                IF(CONTAINS(STR(?g), "/esco"), "ESCO",
                IF(CONTAINS(STR(?g), "/onet"), "O*NET",
                IF(CONTAINS(STR(?g), "/sg"), "Singapore",
                "Unknown")))) AS ?framework
            )
        }
        GROUP BY ?framework
        ORDER BY DESC(?occupationCount)
        """


# Example usage and helper functions
def format_sparql_results(results: Dict) -> List[Dict]:
    """
    Format SPARQL JSON results into a more usable structure
    
    Args:
        results: Raw SPARQL query results in JSON format
        
    Returns:
        List of dictionaries with cleaned data
    """
    if not results or 'results' not in results or 'bindings' not in results['results']:
        return []
    
    formatted = []
    for binding in results['results']['bindings']:
        row = {}
        for key, value in binding.items():
            row[key] = value.get('value', '')
        formatted.append(row)
    
    return formatted


# Pre-defined query collections for common workflows
class WorkflowQueries:
    """Collection of query workflows for common tasks"""
    
    @staticmethod
    def enrich_job_description(job_title: str) -> Dict[str, str]:
        """
        Get all queries needed to enrich a job description
        
        Returns:
            Dictionary of query names to SPARQL queries
        """
        kg = KnowledgeGraphQueries()
        
        return {
            'find_occupation': kg.get_occupation_by_label(job_title),
            # Note: occupation_uri will be filled in after first query
            'search_similar': kg.find_similar_occupations('PLACEHOLDER', min_common_skills=3),
            'search_skills': kg.search_skills_by_keyword(job_title),
        }
    
    @staticmethod
    def career_pathway_analysis(current_occupation: str, target_occupation: str) -> Dict[str, str]:
        """
        Get queries to analyze career pathway between two occupations
        
        Returns:
            Dictionary of query names to SPARQL queries
        """
        kg = KnowledgeGraphQueries()
        
        return {
            'current_skills': f"# Skills for {current_occupation}",
            'target_skills': f"# Skills for {target_occupation}",
            'skill_gap': f"# Skill gap analysis (to be implemented)",
        }
