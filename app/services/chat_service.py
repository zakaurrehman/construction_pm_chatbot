from app.services.project_service import get_project_by_id
from data.projects import project_data
import re

def process_message(message, active_project_id):
    """Process incoming messages and determine appropriate response"""
    lower_msg = message.lower()
    
    # Debug output
    print(f"Processing message: '{message}', active project: {active_project_id}")
    
    # Check for project selection
    if ('select' in lower_msg or 'choose' in lower_msg) and 'project' in lower_msg:
        print("Project selection detected")
        return 'SHOW_PROJECT_SELECTOR'
    
    # Check for report generation
    report_pattern = re.compile(r'(generate|create|make|produce).*report', re.IGNORECASE)
    if report_pattern.search(lower_msg):
        if not active_project_id:
            return "Please select a project first before generating a report."
        return 'GENERATE_REPORT'
    
    # Check for chart/visualization request
    chart_pattern = re.compile(r'(show|display|create|generate|visualize).*?(chart|graph|budget.*?chart|visualization)', re.IGNORECASE)
    if chart_pattern.search(lower_msg):
        if not active_project_id:
            return "Please select a project first before generating charts."
        return 'SHOW_BUDGET_CHART'
    
    # Check for weather request
    weather_pattern = re.compile(r'(check|show|get|what.*?is|how.*?is).*?(weather|forecast|temperature|rain|precipitation)', re.IGNORECASE)
    if weather_pattern.search(lower_msg):
        if not active_project_id:
            return "Please select a project first before checking weather."
        return 'CHECK_WEATHER'
    
    # Check for add note request
    add_note_pattern = re.compile(r'(add|create|make|write).*?note', re.IGNORECASE)
    if add_note_pattern.search(lower_msg):
        if not active_project_id:
            return "Please select a project first before adding notes."
        
        # Try to extract the note content
        note_content_pattern = re.compile(r'(saying|that says|with content|with text|:)\s*[""]?(.*?)[""]?$', re.IGNORECASE)
        note_match = note_content_pattern.search(lower_msg)
        
        if note_match:
            note_text = note_match.group(2).strip()
            return f"ADD_NOTE:{note_text}"
        else:
            return "What would you like the note to say?"
    
    # Check for view notes request
    view_notes_pattern = re.compile(r'(view|show|get|read|list).*?notes', re.IGNORECASE)
    if view_notes_pattern.search(lower_msg):
        if not active_project_id:
            return "Please select a project first before viewing notes."
        return 'VIEW_NOTES'
    
    # Check for specific project mention when no project is selected
    if not active_project_id:
        for proj_id, project in project_data.items():
            if project['name'].lower() in lower_msg:
                return f"I found the {project['name']}. Please select it first by typing 'select project'."
        
        return "Please select a project first by typing 'select project'."
    
    project = get_project_by_id(active_project_id)
    
    # Check for project status
    if 'status' in lower_msg:
        return f"Project \"{project['name']}\" is currently {project['status']} with {project['completion']}% completion. The timeline is {project['timeline']}."
    
    # Check for budget inquiries
    if any(word in lower_msg for word in ['budget', 'cost', 'money', 'financial', 'spend', 'spending']):
        budget = project['budget']
        return f"Budget for {project['name']}: Allocated: ${budget['allocated']:,}, Spent: ${budget['spent']:,}, Remaining: ${budget['remaining']:,}"
    
    # Check for issue reports
    if any(word in lower_msg for word in ['issue', 'problem', 'trouble', 'challenge', 'difficulty']):
        issues = project['issues']
        if not issues:
            return f"No issues reported for project {project['name']}."
        else:
            return f"Issues for {project['name']}:\n" + "\n".join([
                f"- {issue['description']} ({issue['status']}) - Reported on {issue['date']}"
                for issue in issues
            ])
    
    # Check for milestone inquiries
    if any(word in lower_msg for word in ['milestone', 'progress', 'phase', 'stage', 'timeline', 'schedule']):
        milestones = project['milestones']
        return f"Milestones for {project['name']}:\n" + "\n".join([
            f"- {milestone['name']}: {milestone['status']} (Target: {milestone['date']})"
            for milestone in milestones
        ])
    
    # Check for resource inquiries
    if any(word in lower_msg for word in ['resource', 'worker', 'staff', 'people', 'team', 'equipment', 'tool', 'machine']):
        resources = project['resources']
        equipment_str = ', '.join(resources['equipment']) if resources['equipment'] else 'None'
        return f"Resources for {project['name']}:\n- Workers: {resources['workers']}\n- Equipment: {equipment_str}"
    
    # Help message
    if any(word in lower_msg for word in ['help', 'guide', 'assist', 'instruction', 'command']):
        return """You can ask about:
- Project Status: "What's the status of this project?"
- Budget Information: "Show me the budget details"
- Current Issues: "Are there any issues?"
- Milestones: "What are the milestones?"
- Resources: "What resources are assigned?"

Additional features:
- Generate a PDF report: "Generate a project report"
- View budget charts: "Show me the budget chart"
- Check weather: "What's the weather forecast for the site?"
- Add notes: "Add a note saying [your note text]"
- View notes: "Show me all notes"

First, select a project by typing 'select project'.
"""
    
    # Default response
    return "I'm not sure how to answer that. Try asking about project status, budget, issues, milestones, or resources."