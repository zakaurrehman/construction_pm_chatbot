import matplotlib.pyplot as plt
import numpy as np
import os
from datetime import datetime
import io
import base64

def generate_budget_chart(project):
    """Generate a budget chart for a project"""
    
    # Create charts directory if it doesn't exist
    if not os.path.exists('app/static/charts'):
        os.makedirs('app/static/charts')
    
    # Prepare data
    budget = project['budget']
    labels = ['Spent', 'Remaining']
    sizes = [budget['spent'], budget['remaining']]
    colors = ['#ff9999','#66b3ff']
    
    # Create figure and axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pie chart
    ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    ax1.set_title(f'Budget Allocation for {project["name"]}')
    
    # Bar chart
    categories = ['Allocated', 'Spent', 'Remaining']
    values = [budget['allocated'], budget['spent'], budget['remaining']]
    
    x = np.arange(len(categories))
    ax2.bar(x, values, color=['#9999ff', '#ff9999', '#66b3ff'])
    ax2.set_xticks(x)
    ax2.set_xticklabels(categories)
    ax2.set_title(f'Budget Breakdown (in $)')
    ax2.set_ylabel('Amount ($)')
    
    # Add values on top of bars
    for i, v in enumerate(values):
        ax2.text(i, v + 0.05 * max(values), f'${v:,}', ha='center')
    
    plt.tight_layout()
    
    # Save to memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Create a filename and save to disk as well
    filename = f'charts/{project["name"].replace(" ", "_")}_budget_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    # Save to disk
    plt.savefig(f'app/static/{filename}')
    plt.close()
    
    return {
        'image_base64': image_base64,
        'filename': filename
    }

def generate_progress_chart(project):
    """Generate a progress chart for a project"""
    
    # Create charts directory if it doesn't exist
    if not os.path.exists('app/static/charts'):
        os.makedirs('app/static/charts')
    
    # Prepare milestone data
    milestones = project['milestones']
    names = [m['name'] for m in milestones]
    
    # Calculate progress for each milestone
    progress = []
    colors = []
    for m in milestones:
        if m['status'] == 'Completed':
            progress.append(100)
            colors.append('#66cc66')  # Green
        elif m['status'] == 'In Progress':
            progress.append(50)  # Assuming 50% for in-progress
            colors.append('#ffcc66')  # Orange
        else:
            progress.append(0)
            colors.append('#ff9999')  # Red
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create progress bars
    y_pos = np.arange(len(names))
    ax.barh(y_pos, progress, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlabel('Completion Percentage')
    ax.set_title(f'Milestone Progress for {project["name"]}')
    
    # Add percentage labels
    for i, v in enumerate(progress):
        ax.text(v + 5, i, f'{v}%', va='center')
    
    plt.tight_layout()
    
    # Save to memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Create a filename and save to disk as well
    filename = f'charts/{project["name"].replace(" ", "_")}_progress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    # Save to disk
    plt.savefig(f'app/static/{filename}')
    plt.close()
    
    return {
        'image_base64': image_base64,
        'filename': filename
    }

def generate_timeline_chart(project):
    """Generate a timeline chart for a project"""
    
    # Create charts directory if it doesn't exist
    if not os.path.exists('app/static/charts'):
        os.makedirs('app/static/charts')
    
    # Get milestone data
    milestones = project['milestones']
    
    # Convert dates to datetime objects for plotting
    import datetime as dt
    
    milestone_names = []
    milestone_starts = []
    milestone_durations = []
    milestone_colors = []
    
    # Mock start dates based on the target completion date
    # In a real app, you would have actual start and end dates
    for i, milestone in enumerate(milestones):
        milestone_names.append(milestone['name'])
        
        # Parse the target date
        target_date = dt.datetime.strptime(milestone['date'], '%Y-%m-%d')
        
        # Mock a start date 30 days before the target
        start_date = target_date - dt.timedelta(days=30)
        milestone_starts.append(start_date)
        
        # Duration is 30 days
        milestone_durations.append(30)
        
        # Color based on status
        if milestone['status'] == 'Completed':
            milestone_colors.append('#66cc66')  # Green
        elif milestone['status'] == 'In Progress':
            milestone_colors.append('#ffcc66')  # Orange
        else:
            milestone_colors.append('#ff9999')  # Red
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot each milestone as a horizontal bar
    for i, (name, start, duration, color) in enumerate(zip(milestone_names, milestone_starts, milestone_durations, milestone_colors)):
        ax.barh(i, duration, left=start, color=color, alpha=0.8)
        ax.text(start, i, name, va='center', ha='right', color='black')
    
    # Set y-ticks
    ax.set_yticks(range(len(milestone_names)))
    ax.set_yticklabels([])  # Hide labels since we added them manually
    
    # Format the x-axis to show dates
    from matplotlib.dates import DateFormatter
    date_formatter = DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(date_formatter)
    fig.autofmt_xdate()  # Rotate date labels
    
    # Add title and labels
    ax.set_title(f'Project Timeline for {project["name"]}')
    ax.set_xlabel('Date')
    
    # Add a legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#66cc66', label='Completed'),
        Patch(facecolor='#ffcc66', label='In Progress'),
        Patch(facecolor='#ff9999', label='Not Started')
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    
    # Save to memory
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Create a filename and save to disk as well
    filename = f'charts/{project["name"].replace(" ", "_")}_timeline_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    # Save to disk
    plt.savefig(f'app/static/{filename}')
    plt.close()
    
    return {
        'image_base64': image_base64,
        'filename': filename
    }
    