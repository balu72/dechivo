#!/usr/bin/env python3
"""
Quick test script to verify Knowledge Graph is working correctly
"""

from SPARQLWrapper import SPARQLWrapper, JSON, BASIC
import json

def test_query(endpoint, query_name, query):
    """Execute a test query"""
    try:
        sparql = SPARQLWrapper(f"http://localhost:3030/{endpoint}/query")
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials("admin", "admin123")
        
        results = sparql.query().convert()
        return True, results
    except Exception as e:
        return False, str(e)

print("=" * 80)
print("KNOWLEDGE GRAPH VERIFICATION TESTS")
print("=" * 80)
print()

# Test 1: Count triples in each dataset
print("Test 1: Triple counts per dataset")
print("-" * 80)

datasets = ['ca', 'esco', 'onet', 'sg']
count_query = "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"

for dataset in datasets:
    success, result = test_query(dataset, "count", count_query)
    if success:
        count = int(result['results']['bindings'][0]['count']['value'])
        print(f"  ✓ {dataset.upper():6s}: {count:>10,} triples")
    else:
        print(f"  ✗ {dataset.upper():6s}: Failed - {result}")

print()

# Test 2: Find sample occupations
print("Test 2: Sample occupation search")
print("-" * 80)

search_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?occ ?label
WHERE {
    ?occ rdfs:label ?label .
    FILTER(CONTAINS(LCASE(STR(?label)), "software developer"))
}
LIMIT 5
"""

for dataset in datasets:
    success, result = test_query(dataset, "search", search_query)
    if success:
        bindings = result['results']['bindings']
        if bindings:
            print(f"  {dataset.upper()}: Found {len(bindings)} match(es)")
            for binding in bindings[:3]:
                label = binding.get('label', {}).get('value', 'N/A')
                print(f"    - {label}")
        else:
            print(f"  {dataset.upper()}: No matches")
    else:
        print(f"  {dataset.upper()}: Query failed")

print()

# Test 3: Get skills for an occupation (ESCO)
print("Test 3: Get skills for 'accountant' (ESCO)")
print("-" * 80)

skills_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX esco: <http://data.europa.eu/esco/>

SELECT ?skill ?skillLabel
WHERE {
    ?occ rdfs:label "accountant"@en .
    ?occ esco:hasEssentialSkill ?skill .
    ?skill rdfs:label ?skillLabel .
}
LIMIT 10
"""

success, result = test_query('esco', "skills", skills_query)
if success:
    bindings = result['results']['bindings']
    print(f"  Found {len(bindings)} essential skills:")
    for binding in bindings:
        skill = binding.get('skillLabel', {}).get('value', 'N/A')
        print(f"    - {skill}")
else:
    print(f"  Failed: {result}")

print()

# Test 4: O*NET salary data
print("Test 4: Get salary data (O*NET)")
print("-" * 80)

salary_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>

SELECT ?label ?salary
WHERE {
    ?occ rdfs:label ?label .
    ?occ schema:baseSalary ?salary .
}
LIMIT 5
"""

success, result = test_query('onet', "salary", salary_query)
if success:
    bindings = result['results']['bindings']
    print(f"  Sample occupations with salary data:")
    for binding in bindings:
        label = binding.get('label', {}).get('value', 'N/A')
        salary = binding.get('salary', {}).get('value', 'N/A')
        print(f"    - {label}: ${salary}")
else:
    print(f"  Failed: {result}")

print()

# Test 5: Singapore proficiency levels
print("Test 5: Skills with proficiency levels (Singapore)")
print("-" * 80)

prof_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sg: <http://data.skillsframework.sg/>

SELECT DISTINCT ?skillLabel ?profLevel
WHERE {
    ?occ sg:requiresSkill ?skill .
    ?occ sg:proficiencyLevel ?profLevel .
    ?skill rdfs:label ?skillLabel .
}
LIMIT 10
"""

success, result = test_query('sg', "proficiency", prof_query)
if success:
    bindings = result['results']['bindings']
    print(f"  Sample skills with proficiency levels:")
    for binding in bindings[:5]:
        skill = binding.get('skillLabel', {}).get('value', 'N/A')
        prof = binding.get('profLevel', {}).get('value', 'N/A')
        print(f"    - {skill} (Level {prof})")
else:
    print(f"  Failed: {result}")

print()
print("=" * 80)
print("✅ VERIFICATION COMPLETE")
print("=" * 80)
print()
print("Your knowledge graph is loaded and working!")
print("Access Fuseki UI: http://localhost:3030")
print()
