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
JD_REGENERATION_SYSTEM_PROMPT = """You are an expert HR consultant who creates compelling, professional job descriptions that attract top talent.

Your task is to REWRITE the provided job description, enriching it with the competency expectations from the provided skill definitions.

CRITICAL INSTRUCTIONS:

1. DO NOT include SFIA codes, skill names in parentheses, or level numbers.
   - WRONG: "Software Development (PROG) Level 4 required"
   - RIGHT: "You will independently design and implement software solutions..."

2. INTEGRATE competency expectations into responsibilities naturally.
   Use the level descriptions to show WHAT the person will do at this role level.

3. TRANSLATE technical skill definitions into real-world job expectations.
   The skill and level descriptions tell you the depth of expertise required - weave this into the JD.

4. WRITE in an engaging, professional tone that attracts candidates.

5. FOLLOW a standard job description structure:
   - Role Mandate and Capability
   - Why [Company Name]
   - The Impact You'll Create
   - Your Mandate & Ownership (Responsibilities)
   - Mandatory Skills (Essential Skills)
   - Desired Skills (What Sets You Apart)
   - How We Work & Operating Principles

6. OUTPUT in plain text format (not markdown). Use simple formatting:
   - Section headers in Title Case followed by a blank line
   - Bullet points with simple dashes (-)
   - No special characters like #, *, **, or ```

Output a complete, polished job description ready for posting on job boards."""


# Prompt for creating job description from context only (no existing JD)
JD_CREATION_SYSTEM_PROMPT = """You are an expert HR consultant who creates compelling, professional job descriptions that attract top talent.

Your task is to CREATE a complete job description from scratch based on the organizational context provided.

CRITICAL INSTRUCTIONS:

1. CREATE a detailed, engaging job description that reflects the role, company, and requirements.

2. INCLUDE all standard job description sections:
   - Role Mandate and Capability
   - Why [Company Name]
   - The Impact You'll Create
   - Your Mandate & Ownership (Responsibilities)
   - Mandatory Skills
   - Desired Skills
   - How We Work & Operating Principles

3. WRITE in an engaging, professional tone that attracts top candidates.

4. USE the organizational context to make the JD specific and compelling.

5. OUTPUT in plain text format (not markdown). Use simple formatting:
   - Section headers in Title Case followed by a blank line
   - Bullet points with simple dashes (-)
   - No special characters like #, *, **, or ```

Output a complete, polished job description ready for posting on job boards."""


# Organizational context template
ORG_CONTEXT_TEMPLATE = """
--- Organizational Context ---
{context_items}
"""


def get_jd_creation_system_prompt():
    """Get the system prompt for JD creation from context only"""
    return JD_CREATION_SYSTEM_PROMPT


def get_skill_extraction_prompt():
    """Get the system prompt for skill extraction"""
    return SKILL_EXTRACTION_PROMPT


def get_jd_regeneration_system_prompt():
    """Get the system prompt for JD regeneration"""
    return JD_REGENERATION_SYSTEM_PROMPT


def format_skills_detailed(enhanced_skills: list) -> str:
    """
    Format skills with full descriptions and level descriptions for LLM context.
    
    This provides the LLM with rich context about each skill so it can
    integrate competency expectations naturally into the job description.
    
    Args:
        enhanced_skills: List of skill dictionaries with name, description, 
                        level, level_name, and level_description
    
    Returns:
        Formatted string with detailed skill information
    """
    if not enhanced_skills:
        return "No specific competencies identified."
    
    skills_text = []
    for skill in enhanced_skills:
        name = skill.get('name', skill.get('label', 'Unknown'))
        description = skill.get('description', 'N/A')
        level = skill.get('level', 'N/A')
        level_name = skill.get('level_name', 'N/A')
        level_description = skill.get('level_description', 'N/A')
        
        entry = f"""Competency: {name}
Definition: {description}
Required Level: {level} - {level_name}
What This Level Means: {level_description}"""
        
        skills_text.append(entry)
    
    return "\n\n".join(skills_text)


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
        'role_context': 'Mandatory Skills (Primary)',
        'secondary_skills': 'Desired Skills (Secondary)',
        'role_title': 'Role Title',
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
        skills_text: Formatted skills with detailed descriptions
        org_context: Optional dictionary containing organizational context
    
    Returns:
        Formatted user prompt for JD regeneration
    """
    org_context_str = format_org_context(org_context) if org_context else ""
    
    prompt = f"""Original Job Description:
{job_description}

Competency Requirements (use these to enrich the JD, but do not mention codes or levels explicitly):
{skills_text}
{org_context_str}

Rewrite this job description as a polished, professional posting. Integrate the competency expectations naturally into responsibilities and requirements. Do not include any skill codes or level numbers in your output.

Use the following structure for the enhanced job description:

Role Mandate: <Job Title>
Practice / Capability: <Function>
Location & Work Model: <Location from context or "Flexible">

Why <Organization Name>
- Brief compelling paragraph about the organization

The Impact You'll Create
- Key outcomes and value this role delivers

Your Mandate & Ownership
- Core responsibilities and accountabilities

Mandatory Skills
- Essential qualifications, technical skills, and experience required
- Incorporate the Primary Skills/SFIA competencies provided

Desired Skills
- Differentiating skills, preferred technologies, and attributes
- Incorporate the Secondary Skills provided

How We Work
- Work culture and collaboration style

Our Operating Principles
- Core values and ways of working
"""
    
    return prompt


def format_jd_creation_user_prompt(org_context: dict) -> str:
    """
    Format the user prompt for JD creation from organizational context only.
    
    Args:
        org_context: Dictionary containing organizational context
    
    Returns:
        Formatted user prompt for JD creation
    """
    org_context_str = format_org_context(org_context) if org_context else ""
    
    role_title = org_context.get('role_title', 'the role')
    company_name = org_context.get('company_name', 'the organization')
    key_skills = org_context.get('role_context', '')
    secondary_skills = org_context.get('secondary_skills', '')
    experience = org_context.get('business_context', '')
    
    skills_section = ""
    if key_skills:
        skills_section = f"\nMandatory Skills (Primary): {key_skills}"
    if secondary_skills:
        skills_section += f"\nDesired Skills (Secondary): {secondary_skills}"
    if experience:
        skills_section += f"\nExperience Level: {experience}"
    
    prompt = f"""Create a complete, professional job description for the following role:

Role: {role_title}
Company: {company_name}
{org_context_str}
{skills_section}

Generate a detailed job description using this structure:

Role Mandate: {role_title}
Practice / Capability: <Appropriate function/department>
Location & Work Model: <From context>

Why {company_name}
- Brief compelling paragraph about the organization

The Impact You'll Create
- Key outcomes and value this role delivers

Your Mandate & Ownership
- Core responsibilities and accountabilities (5-7 bullet points)

Mandatory Skills
- Essential qualifications, technical skills, and experience required (4-6 bullet points)
- Incorporate the Primary Skills provided: {key_skills}

Desired Skills
- Differentiating skills, preferred technologies, and attributes (3-4 bullet points)
- Incorporate the Secondary Skills provided: {secondary_skills}

How We Work
- Work culture and collaboration style

Our Operating Principles
- Core values and ways of working

Create a complete, polished job description ready for posting on job boards.
"""
    
    return prompt

