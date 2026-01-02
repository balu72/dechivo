"""
Prompts for Job Description Enhancement Service
All LLM prompts used in the enhancement workflow
"""

# Prompt for extracting skills from job description
SKILL_EXTRACTION_PROMPT = """You are an expert at analyzing job descriptions and extracting technical skills, 
competencies, and required capabilities. Extract all relevant skills mentioned in the job description.

Focus on:
- Technical skills (programming languages, tools, technologies)
- Professional competencies (project management, communication, leadership)
- Domain expertise (data analysis, software development, cybersecurity, etc.)
- Soft skills when explicitly mentioned

Return ONLY a comma-separated list of skill keywords, no explanations."""


# Prompt for regenerating job description with SFIA skills and organizational context
JD_REGENERATION_SYSTEM_PROMPT = """You are an expert HR consultant and technical writer specializing in SFIA-aligned job descriptions.

Your task is to rewrite the provided job description to incorporate the identified SFIA skills, competencies, and organizational context professionally.

Guidelines:
1. Keep the original role and responsibilities but enhance them with SFIA terminology
2. Incorporate the provided organizational context (company info, culture, values) naturally
3. Add a dedicated "SFIA Skills & Competencies" section
4. For each SFIA skill, include the skill name, code, and level with appropriate context
5. Maintain a professional, engaging tone suitable for job postings
6. Structure the JD with clear sections:
   - About the Company (if company context provided)
   - Role Overview
   - Key Responsibilities
   - SFIA Skills & Competencies
   - Requirements & Qualifications
   - Role Details (location, reporting, work environment if provided)
7. Make the SFIA requirements specific and actionable
8. Keep the total length reasonable (not too verbose)

Output format: Write the complete enhanced job description in markdown format."""


# Organizational context template
ORG_CONTEXT_TEMPLATE = """
--- Organizational Context ---
{context_items}
"""


def get_skill_extraction_prompt():
    """Get the system prompt for skill extraction"""
    return SKILL_EXTRACTION_PROMPT


def get_jd_regeneration_system_prompt():
    """Get the system prompt for JD regeneration"""
    return JD_REGENERATION_SYSTEM_PROMPT


def format_skill_extraction_user_prompt(job_description: str) -> str:
    """Format the user prompt for skill extraction"""
    return f"Extract skills from this job description:\n\n{job_description}"


def format_org_context(org_context: dict) -> str:
    """
    Format organizational context for inclusion in the prompt.
    
    Args:
        org_context: Dictionary containing organizational information:
            - org_industry: Industry sector
            - company_name: Name of the company
            - company_description: Brief description of the company
            - company_culture: Company culture description
            - company_values: Core company values
            - business_context: Business context for the role
            - role_context: Company-specific role context
            - role_type: Type of role (permanent, contract, etc.)
            - role_grade: Grade/band of the role
            - location: Work location
            - work_environment: Work environment (remote, hybrid, onsite)
            - reporting_to: Reporting manager/title
    
    Returns:
        Formatted context string
    """
    if not org_context:
        return ""
    
    context_items = []
    
    field_labels = {
        'org_industry': 'Industry',
        'company_name': 'Company Name',
        'company_description': 'Company Description',
        'company_culture': 'Company Culture',
        'company_values': 'Company Values',
        'business_context': 'Business Context',
        'role_context': 'Role Context',
        'role_type': 'Role Type',
        'role_grade': 'Role Grade/Band',
        'location': 'Location',
        'work_environment': 'Work Environment',
        'reporting_to': 'Reports To'
    }
    
    for key, label in field_labels.items():
        value = org_context.get(key, '').strip() if org_context.get(key) else ''
        if value:
            context_items.append(f"- {label}: {value}")
    
    if not context_items:
        return ""
    
    return ORG_CONTEXT_TEMPLATE.format(context_items='\n'.join(context_items))


def format_jd_regeneration_user_prompt(
    job_description: str, 
    skills_text: str, 
    org_context: dict = None
) -> str:
    """
    Format the user prompt for JD regeneration with optional organizational context.
    
    Args:
        job_description: The original job description text
        skills_text: Formatted SFIA skills to incorporate
        org_context: Optional dictionary containing organizational context
    
    Returns:
        Formatted user prompt for JD regeneration
    """
    org_context_str = format_org_context(org_context) if org_context else ""
    
    prompt = f"""Original Job Description:
{job_description}

SFIA Skills to incorporate:
{skills_text}
{org_context_str}
Please rewrite this job description incorporating these SFIA skills and competencies{' and the organizational context provided' if org_context_str else ''}."""
    
    return prompt
