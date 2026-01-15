"""
Prompts for Job Description Creation Service
Prompts used when creating JD from organizational context only
"""


# Prompt for creating job description from context only (no existing JD)
JD_CREATION_SYSTEM_PROMPT = """You are an expert HR consultant who creates compelling, professional job descriptions that attract top talent.

Your task is to CREATE a complete job description from scratch based on the organizational context provided.

CRITICAL INSTRUCTIONS:

1. CREATE a detailed, engaging job description that reflects the role, company, and requirements.

2. INCLUDE all standard job description sections:
   - Role title and overview
   - About the company
   - Key responsibilities
   - Required qualifications and experience
   - Location and work model details

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


def format_org_context(org_context: dict) -> str:
    """
    Format organizational context for inclusion in the prompt.
    
    Args:
        org_context: Dictionary containing organizational information
    
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
        'business_context': 'Experience Level',
        'role_context': 'Key Skills',
        'role_title': 'Role Title',
        'role_type': 'Role Type',
        'role_grade': 'Role Grade/Band',
        'location': 'Location',
        'work_environment': 'Work Environment',
        'reporting_to': 'Reports To',
        'additional_context': 'Additional Context'
    }
    
    for key, label in field_labels.items():
        value = org_context.get(key, '').strip() if org_context.get(key) else ''
        if value:
            context_items.append(f"- {label}: {value}")
    
    if not context_items:
        return ""
    
    return ORG_CONTEXT_TEMPLATE.format(context_items='\n'.join(context_items))


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
    experience = org_context.get('business_context', '')
    additional_context = org_context.get('additional_context', '').strip()
    
    skills_section = ""
    if key_skills:
        skills_section = f"\nKey Skills to Include: {key_skills}"
    if experience:
        skills_section += f"\nExperience Level: {experience}"
    
    # Add additional context if provided
    additional_info = ""
    if additional_context:
        additional_info = f"\n--- Additional Context from Hiring Manager ---\n{additional_context}\n"
    
    prompt = f"""Create a complete, professional job description for the following role:

Role: {role_title}
Company: {company_name}
{org_context_str}
{skills_section}
{additional_info}

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

Foundations for Success
- Essential qualifications and experience required (4-6 bullet points)

What Sets You Apart
- Differentiating skills and attributes (3-4 bullet points)

How We Work
- Work culture and collaboration style

Our Operating Principles
- Core values and ways of working

Create a complete, polished job description ready for posting on job boards.
"""
    
    return prompt
