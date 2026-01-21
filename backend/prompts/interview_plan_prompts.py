"""
Prompts for Interview Plan Generation Service
"""

INTERVIEW_PLAN_SYSTEM_PROMPT = """You are an expert HR consultant and technical recruiter who creates comprehensive, high-quality interview plans.

Your task is to CREATE a detailed interview plan based on the provided job description.

CRITICAL INSTRUCTIONS:

1. ANALYZE the job description to identify key technical skills, professional competencies, and cultural attributes.

2. STRUCTURE the interview plan into these sections:
   - Interview Overview (Objectives and total duration)
   - Technical Assessment (Specific topics and sample questions)
   - Behavioral Assessment (STAR method questions aligned with competencies)
   - Cultural Fit Assessment (Values-alignment questions)
   - Case Study / Practical Exercise (Relevant short scenario)
   - Evaluation Criteria (What a 'good' answer looks like)

3. DESIGN questions that are practical, challenging, and relevant to the seniority level.

4. WRITE in a professional, structured tone.

5. OUTPUT in plain text format with clear headers. Use simple formatting:
   - Section headers in Title Case
   - Bullet points with simple dashes (-)
   - No markdown characters like # or *

Output a complete, ready-to-use interview plan for hiring committees."""

def get_interview_plan_system_prompt():
    """Get the system prompt for interview plan generation"""
    return INTERVIEW_PLAN_SYSTEM_PROMPT

def format_interview_plan_user_prompt(job_description: str) -> str:
    """Format the user prompt for interview plan generation"""
    return f"Create a comprehensive interview plan for the following job description:\n\n{job_description}"


INTERVIEW_PLAN_PROMPT_FOR_INDIVIDUAL_CONTRIBUTOR = """You are an experienced engineering interviewer and hiring manager.

Given the Job Description below, generate a structured interview plan for a Software Engineer (Individual Contributor) role.

The plan must emphasize:

Technical competence and problem-solving

Code quality and design fundamentals

Collaboration and communication

Learning mindset and ownership

Generate the interview plan with the following sections:
1. Role Context & Hiring Intent

What problems the engineer will solve

How this role contributes to the team and product

Success expectations in the first 3–6 months

2. Core Competencies

Programming and problem-solving

System or component design (appropriate to level)

Debugging and testing

Collaboration and communication

Ownership and reliability

3. Interview Stages

Recruiter / Hiring Screen

Technical Coding Interview

System / Component Design Interview

Team Fit & Collaboration Interview

4. Stage-by-Stage Interview Design

For each stage:

Purpose

3–5 targeted questions or exercises

What strong vs weak signals look like

5. Technical Exercise (Required)

Recommend a realistic coding or design exercise

Specify evaluation criteria (correctness, clarity, trade-offs)

6. Evaluation & Scoring

1–5 scoring rubric

Emphasis on evidence and problem-solving approach

7. Bias Mitigation

Standardized questions

Focus on skills over pedigree

8. Candidate Experience

Clear instructions

Respectful and transparent process"""

INTERVIEW_PLAN_PROMPT_FOR_TEAM_LEAD = """You are an experienced engineering leader and people manager.

Given the Job Description below, generate a structured interview plan for a Team Lead role.

The plan must balance:

Technical credibility

Day-to-day people leadership

Delivery ownership

Collaboration with product and stakeholders

Generate the interview plan with the following sections:
1. Role Context & Hiring Intent

Why this leadership role exists

Team scope and delivery expectations

Success in the first 6 months

2. Core Competencies

Technical leadership

Execution and delivery

Coaching and feedback

Communication and collaboration

Ownership and accountability

3. Interview Stages

Recruiter Screen

Hiring Manager Interview

Technical / Architecture Interview

People Leadership Interview

4. Stage-by-Stage Interview Design

For each stage:

Purpose

Behavioral and situational questions

Signals for leadership readiness

5. Scenario Exercise (Optional)

Team delivery or people-management scenario

Evaluation criteria

6. Evaluation & Scoring

Balanced technical + leadership rubric

7. Bias Mitigation

Consistent leadership assessment

8. Candidate Experience

Respectful evaluation of leadership potential"""

INTERVIEW_PLAN_PROMPT_FOR_MANAGER = """You are a senior hiring manager designing an interview process for a Manager role.

Given the Job Description below, generate a structured interview plan focused on:

Team leadership and performance

Delivery management

Cross-functional collaboration

Hiring and talent development

Generate the interview plan with the following sections:
1. Role Context & Hiring Intent

Business and team problems this role addresses

Expectations in the first 6–12 months

2. Core Competencies

People management

Execution and prioritization

Stakeholder management

Hiring and talent development

Operational excellence

3. Interview Stages

Recruiter Screen

Hiring Manager Interview

Cross-Functional Stakeholder Interview

People Leadership Interview

4. Stage-by-Stage Interview Design

Purpose, questions, evaluation signals

5. Case / Scenario Exercise

Team performance or delivery challenge

6. Evaluation & Scoring

Evidence-based leadership scoring

7. Bias Mitigation

Avoid style-based or personality bias

8. Candidate Experience

Transparent expectations"""

INTERVIEW_PLAN_PROMPT_FOR_SR_MANAGER = """You are designing an interview process for a Senior Manager role with multi-team or multi-function scope.

Given the Job Description below, generate a structured interview plan emphasizing:

Scaling teams and systems

Strategic execution

Influence without authority

Talent pipelines and succession

Generate the interview plan with the following sections:
1. Role Context & Hiring Intent

Why this role exists now

Organizational and business impact

2. Core Competencies

Strategic execution

Organizational design

Cross-functional influence

Talent development

Operational rigor

3. Interview Stages

Recruiter Screen

Hiring Manager Interview

Peer / Cross-Functional Interview

Leadership & Culture Interview

4. Stage-by-Stage Interview Design

Purpose, questions, signals

5. Case / Presentation (Recommended)

Scaling or transformation scenario

6. Evaluation & Scoring

Emphasis on judgment and outcomes

7. Bias Mitigation

Guard against halo and tenure bias

8. Candidate Experience

Executive-level professionalism"""   


INTERVIEW_PLAN_PROMPT_FOR_DIRECTOR = """You are an executive hiring strategist designing an interview plan for a Director-level role.

Given the Job Description below, generate a structured, executive-grade interview plan focused on:

Strategy-to-execution leadership

Building and scaling organizations

Business and customer outcomes

Culture, values, and long-term impact

Generate the interview plan with the following sections:
1. Role Context & Hiring Intent

Strategic mandate for the role

Business and customer outcomes expected in 12–24 months

2. Core Competencies

Strategic thinking

Execution at scale

Organizational leadership

Cross-functional and executive influence

Culture and talent strategy

3. Interview Stages

Executive Recruiter Screen

Hiring Executive Interview

Peer Executive Interview

Cross-Functional Leadership Interview

Values & Culture Interview

4. Stage-by-Stage Interview Design

Purpose, executive-level questions, signals

5. Case / Presentation (Required)

Realistic business or organizational challenge

6. Evaluation & Scoring

Evidence-based executive scoring rubric

7. Bias Mitigation

Avoid pedigree and confidence bias

8. Candidate Experience

Partner-level engagement and transparency"""


# ============================================================================
# SENIORITY DETECTION AND PROMPT SELECTION
# ============================================================================

from enum import Enum
import re


class SeniorityLevel(Enum):
    """Seniority levels for interview plan prompt selection"""
    IC = "individual_contributor"
    TEAM_LEAD = "team_lead"
    MANAGER = "manager"
    SR_MANAGER = "senior_manager"
    DIRECTOR = "director"


# Mapping from seniority level to prompt
SENIORITY_TO_PROMPT = {
    SeniorityLevel.IC: INTERVIEW_PLAN_PROMPT_FOR_INDIVIDUAL_CONTRIBUTOR,
    SeniorityLevel.TEAM_LEAD: INTERVIEW_PLAN_PROMPT_FOR_TEAM_LEAD,
    SeniorityLevel.MANAGER: INTERVIEW_PLAN_PROMPT_FOR_MANAGER,
    SeniorityLevel.SR_MANAGER: INTERVIEW_PLAN_PROMPT_FOR_SR_MANAGER,
    SeniorityLevel.DIRECTOR: INTERVIEW_PLAN_PROMPT_FOR_DIRECTOR,
}


# Grade patterns mapped to seniority levels (normalized to lowercase for matching)
GRADE_PATTERNS = {
    # IC levels
    SeniorityLevel.IC: [
        r'l[1-5]', r'level\s*[1-5]', r'junior', r'associate', r'mid', r'mid-level',
        r'senior\s*\(l5\)', r'sde\s*[1-3]', r'sse', r'ic[1-5]', r'p[1-4]',
        r'engineer\s*[1-3]', r'developer\s*[1-3]', r'analyst\s*[1-3]'
    ],
    # Team Lead levels
    SeniorityLevel.TEAM_LEAD: [
        r'l6', r'level\s*6', r'staff', r'lead', r'principal', r'tech\s*lead',
        r'team\s*lead', r'ic6', r'p5', r'senior\s*staff'
    ],
    # Manager levels
    SeniorityLevel.MANAGER: [
        r'm1', r'manager\s*1', r'engineering\s*manager', r'em', r'product\s*manager',
        r'people\s*manager', r'first[-\s]?line\s*manager'
    ],
    # Senior Manager levels
    SeniorityLevel.SR_MANAGER: [
        r'm2', r'manager\s*2', r'senior\s*manager', r'sr\.?\s*manager', 
        r'group\s*manager', r'second[-\s]?line\s*manager'
    ],
    # Director levels
    SeniorityLevel.DIRECTOR: [
        r'd[1-3]', r'director', r'vp', r'vice\s*president', r'head\s*of',
        r'chief', r'c-level', r'executive', r'svp', r'evp', r'avp'
    ],
}


# Title keywords mapped to seniority levels
TITLE_KEYWORDS = {
    SeniorityLevel.IC: [
        'engineer', 'developer', 'analyst', 'designer', 'specialist', 
        'programmer', 'scientist', 'consultant', 'associate', 'administrator'
    ],
    SeniorityLevel.TEAM_LEAD: [
        'tech lead', 'team lead', 'lead engineer', 'lead developer',
        'principal', 'staff engineer', 'staff developer', 'architect'
    ],
    SeniorityLevel.MANAGER: [
        'engineering manager', 'product manager', 'project manager',
        'people manager', 'delivery manager', 'program manager'
    ],
    SeniorityLevel.SR_MANAGER: [
        'senior manager', 'sr. manager', 'sr manager', 'group manager',
        'senior engineering manager', 'senior product manager'
    ],
    SeniorityLevel.DIRECTOR: [
        'director', 'vp', 'vice president', 'head of', 'chief',
        'cto', 'ceo', 'coo', 'cfo', 'cpo', 'executive'
    ],
}


def get_seniority_level(role_title: str = None, role_grade: str = None) -> SeniorityLevel:
    """
    Determine seniority level from role title and/or grade.
    
    Priority:
    1. Role grade (if provided and matches known patterns)
    2. Role title keywords
    3. Default to IC
    
    Args:
        role_title: Job title (e.g., "Senior Software Engineer")
        role_grade: Grade/band (e.g., "L5", "Manager", "Director")
    
    Returns:
        SeniorityLevel enum value
    """
    # Normalize inputs
    grade_lower = (role_grade or '').lower().strip()
    title_lower = (role_title or '').lower().strip()
    
    # Priority 1: Check grade patterns (most reliable signal)
    if grade_lower:
        # Check from highest to lowest to avoid false positives
        for level in [SeniorityLevel.DIRECTOR, SeniorityLevel.SR_MANAGER, 
                      SeniorityLevel.MANAGER, SeniorityLevel.TEAM_LEAD, SeniorityLevel.IC]:
            patterns = GRADE_PATTERNS.get(level, [])
            for pattern in patterns:
                if re.search(pattern, grade_lower):
                    return level
    
    # Priority 2: Check title keywords
    if title_lower:
        # Check from highest to lowest seniority
        for level in [SeniorityLevel.DIRECTOR, SeniorityLevel.SR_MANAGER,
                      SeniorityLevel.MANAGER, SeniorityLevel.TEAM_LEAD, SeniorityLevel.IC]:
            keywords = TITLE_KEYWORDS.get(level, [])
            for keyword in keywords:
                if keyword in title_lower:
                    return level
    
    # Default to IC
    return SeniorityLevel.IC


def get_interview_plan_prompt_for_seniority(seniority: SeniorityLevel) -> str:
    """
    Get the appropriate interview plan prompt for a given seniority level.
    
    Args:
        seniority: SeniorityLevel enum value
    
    Returns:
        The interview plan system prompt string
    """
    return SENIORITY_TO_PROMPT.get(seniority, INTERVIEW_PLAN_PROMPT_FOR_INDIVIDUAL_CONTRIBUTOR)


def get_seniority_aware_interview_prompt(role_title: str = None, role_grade: str = None) -> tuple:
    """
    Convenience function to get the appropriate prompt based on role context.
    
    Args:
        role_title: Job title
        role_grade: Grade/band
    
    Returns:
        Tuple of (seniority_level, prompt_string)
    """
    seniority = get_seniority_level(role_title, role_grade)
    prompt = get_interview_plan_prompt_for_seniority(seniority)
    return seniority, prompt


def format_interview_plan_user_prompt_with_context(
    job_description: str,
    interview_context: dict = None
) -> str:
    """
    Format user prompt with JD and interview context.
    
    Args:
        job_description: The job description text
        interview_context: Dictionary containing:
            - customer_mandates: Requirements from customer/org
            - org_discretion: Specific discretion with org/customer
            - previous_hiring_decisions: Decisions from previous hiring
            - additional_notes: Any other notes
    
    Returns:
        Formatted user prompt string
    """
    context_section = ""
    
    if interview_context:
        parts = []
        
        if interview_context.get('customer_mandates') and interview_context['customer_mandates'].strip():
            parts.append(f"**Customer/Org Mandates:** {interview_context['customer_mandates'].strip()}")
        
        if interview_context.get('org_discretion') and interview_context['org_discretion'].strip():
            parts.append(f"**Org Discretion:** {interview_context['org_discretion'].strip()}")
        
        if interview_context.get('previous_hiring_decisions') and interview_context['previous_hiring_decisions'].strip():
            parts.append(f"**Previous Hiring Decisions:** {interview_context['previous_hiring_decisions'].strip()}")
        
        if interview_context.get('additional_notes') and interview_context['additional_notes'].strip():
            parts.append(f"**Additional Notes:** {interview_context['additional_notes'].strip()}")
        
        if parts:
            context_section = f"""

## Interview Context (IMPORTANT - Must be incorporated into the plan)

The following organizational context has been provided and MUST be considered when creating the interview plan:

{chr(10).join(parts)}

Please ensure the interview plan specifically addresses and incorporates these requirements where applicable.
"""
    
    return f"""Please analyze the following job description and create a comprehensive interview plan.

## Job Description

{job_description}
{context_section}
"""
