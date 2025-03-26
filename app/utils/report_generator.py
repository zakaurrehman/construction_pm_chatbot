from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

def generate_project_report(project, filename=None):
    """Generate a PDF report for a project"""
    
    if filename is None:
        # Create reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')
        filename = f"reports/Project_Report_{project['name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = styles['Heading1']
    title = Paragraph(f"Project Report: {project['name']}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.25*inch))
    
    # Project overview
    subtitle_style = styles['Heading2']
    elements.append(Paragraph("Project Overview", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    overview_data = [
        ["Status", project['status']],
        ["Completion", f"{project['completion']}%"],
        ["Timeline", project['timeline']]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Budget information
    elements.append(Paragraph("Budget Information", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    budget = project['budget']
    budget_data = [
        ["Category", "Amount"],
        ["Allocated", f"${budget['allocated']:,}"],
        ["Spent", f"${budget['spent']:,}"],
        ["Remaining", f"${budget['remaining']:,}"]
    ]
    
    budget_table = Table(budget_data, colWidths=[2*inch, 4*inch])
    budget_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(budget_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Issues
    elements.append(Paragraph("Current Issues", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    if project['issues']:
        issue_data = [["ID", "Description", "Status", "Date"]]
        for issue in project['issues']:
            issue_data.append([
                issue['id'],
                issue['description'],
                issue['status'],
                issue['date']
            ])
        
        issue_table = Table(issue_data, colWidths=[0.7*inch, 3*inch, 1*inch, 1.3*inch])
        issue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(issue_table)
    else:
        elements.append(Paragraph("No current issues for this project.", styles['Normal']))
    
    elements.append(Spacer(1, 0.25*inch))
    
    # Milestones
    elements.append(Paragraph("Milestones", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    milestone_data = [["Name", "Status", "Target Date"]]
    for milestone in project['milestones']:
        milestone_data.append([
            milestone['name'],
            milestone['status'],
            milestone['date']
        ])
    
    milestone_table = Table(milestone_data, colWidths=[2.5*inch, 1.5*inch, 2*inch])
    milestone_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(milestone_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Resources
    elements.append(Paragraph("Resources", subtitle_style))
    elements.append(Spacer(1, 0.1*inch))
    
    resources = project['resources']
    resources_data = [
        ["Workers", str(resources['workers'])],
        ["Equipment", ", ".join(resources['equipment'] if resources['equipment'] else ["None"])]
    ]
    
    resources_table = Table(resources_data, colWidths=[2*inch, 4*inch])
    resources_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(resources_table)
    
    # Footer
    elements.append(Spacer(1, 0.5*inch))
    footer_text = f"Report generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}"
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    return filename