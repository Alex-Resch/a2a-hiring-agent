import instructor
from litellm import completion

from agents.agent_2_screener.state import AgentState, ProfileScore


client = instructor.from_litellm(completion)


SYSTEM_PROMPT = """
You are an expert technical recruiter and senior software engineer. Your job is to evaluate GitHub profiles of potential candidates and score them based on their technical skills, code quality, and activity.

You will receive a GitHub profile containing:
- Basic info (name, bio, location)
- Repositories (name, description, language, stars)
- Commits (messages, code changes, additions, deletions, diffs)

Evaluate the candidate on the following criteria:

1. CODE QUALITY (0-25 points)
   - Are commit messages clear and descriptive?
   - Is the code well-structured based on the diffs?
   - Are changes meaningful or just minor edits?

2. ACTIVITY & CONSISTENCY (0-25 points)
   - How frequently does the candidate commit?
   - Is there consistent activity over time?
   - Are there recent contributions?

3. TECHNICAL BREADTH (0-25 points)
   - How many languages does the candidate work with?
   - Do the repositories show diverse technical skills?
   - Are there complex or impressive projects?

4. COMMUNITY IMPACT (0-25 points)
   - Do repositories have stars from other developers?
   - Does the candidate work on open-source projects?
   - Is there evidence of collaboration?

Count the four scores together to produce an overall_score out of 100.
Provide a detailed reasoning for the scores, highlighting the candidate's strengths and weaknesses based on the GitHub data.
Be objective, fair, and base your evaluation only on the data provided. Do not make assumptions beyond what the GitHub data shows.
"""


def build_user_prompt(profile_str: str, state: AgentState):
    return f"""
    Here are the details about the candidate:
    **{profile_str}**

    The recruiter is looking for the following criteria:
    **{state.user_input}**

    Adjust your scoring based on how well the candidate matches these criteria.
    A strong match should significantly increase the overall score.
    A poor match should decrease it, even if the candidate is technically strong overall.
    """


def score_profiles(state: AgentState):
    scored_profiles: list[ProfileScore] = []

    for profile in state.profiles_details:
        result = client.chat.completions.create(
            model="gemini/gemini-2.5-flash",
            response_model=ProfileScore,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(str(profile), state)},
            ],
        )
        result.email = profile.email
        scored_profiles.append(result)

    return {"scored_profiles": scored_profiles}
