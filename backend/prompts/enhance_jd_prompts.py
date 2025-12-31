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


# Prompt for regenerating job description with SFIA skills
JD_REGENERATION_SYSTEM_PROMPT = """You are an expert HR consultant and technical writer specializing in SFIA-aligned job descriptions.

Your task is to rewrite the provided job description to incorporate the identified SFIA skills and competencies professionally.

Guidelines:
1. Keep the original role and responsibilities but enhance them with SFIA terminology
2. Add a dedicated "SFIA Skills & Competencies" section
3. For each SFIA skill, include the skill name, code, and level with appropriate context
4. Maintain a professional, engaging tone suitable for job postings
5. Structure the JD with clear sections (Overview, Responsibilities, SFIA Skills, Requirements)
6. Make the SFIA requirements specific and actionable
7. Keep the total length reasonable (not too verbose)

Output format: Write the complete enhanced job description in markdown format."""


def get_skill_extraction_prompt():
    """Get the system prompt for skill extraction"""
    return SKILL_EXTRACTION_PROMPT


def get_jd_regeneration_system_prompt():
    """Get the system prompt for JD regeneration"""
    return JD_REGENERATION_SYSTEM_PROMPT


def format_skill_extraction_user_prompt(job_description: str) -> str:
    """Format the user prompt for skill extraction"""
    return f"Extract skills from this job description:\n\n{job_description}"


def format_jd_regeneration_user_prompt(job_description: str, skills_text: str) -> str:
    """Format the user prompt for JD regeneration"""
    return f"""Original Job Description:
{job_description}

SFIA Skills to incorporate:
{skills_text}

Please rewrite this job description incorporating these SFIA skills and competencies."""
