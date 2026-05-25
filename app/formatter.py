from models import AIAnalysis, JobListing, KeyWordAnalysisResult


def format_keyword_analysis(keyword_analysis: KeyWordAnalysisResult) -> str:
    core_matches = keyword_analysis.matched_core_keywords
    supporting_matches = keyword_analysis.matched_supporting_keywords
    core_matches_text = ", ".join(core_matches) if core_matches else "None"
    supporting_matches_text = ", ".join(supporting_matches) if supporting_matches else "None"
    return f"""
    Keyword Analysis:
    - Score: {keyword_analysis.keyword_score}
    - Matched Core Keywords: {core_matches_text}
    - Matched Supporting Keywords: {supporting_matches_text}
    - Passed Gate: {keyword_analysis.passed_gate}
    """

def format_ai_analysis(ai_analysis: AIAnalysis) -> str:
    strengths = ", ".join(f"{s}" for s in ai_analysis.strengths) 
    gaps = ", ".join(f"{g}" for g in ai_analysis.gaps)
    return f"""
    AI Analysis:
    - Fit Score: {ai_analysis.fit_score}/100
    - Interview Chance Score: {ai_analysis.interview_chance_score}/100
    - Recommendation: {ai_analysis.recommendation.upper()}
    - Summary: {ai_analysis.summary}
    - Strengths: {strengths}
    - Gaps: {gaps}
    - Role Description: {ai_analysis.role_description}
    - Company Description: {ai_analysis.company_description}
    - Application Advice: {ai_analysis.application_advice}
    """

def format_match_result(job: JobListing, keyword_analysis: KeyWordAnalysisResult, ai_analysis: AIAnalysis | None = None, ai_error=None) -> str:
    lines = [
        "=" * 70,
        f"Job Title: {job.title} at {job.company}",
        f"Location: {job.location or 'Not provided'}",
        f"URL: {job.url}",
        format_keyword_analysis(keyword_analysis)
    ]

    if ai_error:
        lines.extend([
            f"AI Analysis Error: {ai_error}"
        ])
    
    elif ai_analysis is None:
        lines.extend([  
            "Did not pass keyword gate, skipping AI analysis."
        ])

    else:
        lines.extend([format_ai_analysis(ai_analysis)])

    return "\n".join(lines)