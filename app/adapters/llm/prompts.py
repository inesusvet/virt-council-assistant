"""Module for storing LLM prompt templates."""

CLASSIFY_MESSAGE_PROMPT = """Analyze the following message and classify it based on the available projects.

Message: {content}

Available Projects:
{project_context}

Provide:
1. A category (e.g., "feature_request", "bug_report", "question", "research", "general")
2. Confidence score (0.0 to 1.0)
3. Suggested project ID if applicable
4. Relevant tags (list of keywords)
5. Brief summary

Respond in JSON format with keys: category, confidence, suggested_project_id, tags, summary"""

EXTRACT_KNOWLEDGE_PROMPT = """Extract key information, insights, and actionable items from this message:

Message: {content}

Provide a structured summary highlighting:
- Main topics discussed
- Key decisions or insights
- Action items or next steps
- Important context or references

Keep it concise and well-organized."""

SUGGEST_NEXT_STEPS_PROMPT = """Based on the project information and knowledge base, suggest 3-5 next research steps or actions.

Project: {project.name}
Description: {project.description}

Recent Knowledge Base Entries:
{knowledge_context}

Provide suggestions in JSON array format with each item having:
- title: Brief title
- description: Detailed description
- priority: Integer (1-5, higher is more important)
- resources: List of suggested resources/tools

Example format:
[
  {{"title": "...", "description": "...", "priority": 4, "resources": ["...", "..."]}},
  ...
]"""
