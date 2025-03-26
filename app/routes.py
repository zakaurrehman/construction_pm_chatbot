from flask import Blueprint, render_template, request, jsonify, session, url_for, send_from_directory, send_file
from app.services.chat_service import process_message
from app.services.auth_service import get_user_by_id, get_all_users
from app.services.project_service import get_all_projects, get_project_by_id
from data.projects import project_data
from data.users import user_data
import os
from datetime import datetime
import json
import requests

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/chat')
def chat():
    users = get_all_users()
    # Default to first user if none selected
    user_ids = list(users.keys())
    current_user_id = session.get('user_id')
    
    # If no user in session, set the first user as default
    if not current_user_id or current_user_id not in user_ids:
        current_user_id = user_ids[0]
        session['user_id'] = current_user_id
    
    current_user = get_user_by_id(current_user_id)
    
    print(f"Setting up chat with user: {current_user_id}, access: {current_user['project_access']}")
    
    return render_template(
        'chat.html', 
        users=users, 
        current_user=current_user,
        current_user_id=current_user_id
    )

@main.route('/api/switch_user', methods=['POST'])
def switch_user():
    data = request.get_json()
    user_id = data.get('user_id')
    
    if user_id in user_data:
        session['user_id'] = user_id
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid user ID'})

@main.route('/api/projects')
def get_projects():
    user_id = session.get('user_id')
    print(f"Fetching projects for user: {user_id}")
    
    if not user_id:
        print("No user_id in session")
        return jsonify([])
    
    user = get_user_by_id(user_id)
    print(f"User data: {user}")
    
    accessible_projects = {}
    
    for project_id in user['project_access']:
        if project_id in project_data:
            accessible_projects[project_id] = project_data[project_id]
    
    print(f"Returning projects: {list(accessible_projects.keys())}")
    return jsonify(accessible_projects)

@main.route('/api/select_project', methods=['POST'])
def select_project():
    data = request.get_json()
    project_id = data.get('project_id')
    
    user_id = session.get('user_id')
    user = get_user_by_id(user_id)
    
    if not user or project_id not in user['project_access']:
        return jsonify({'status': 'error', 'message': 'Access denied'})
    
    session['project_id'] = project_id
    return jsonify({'status': 'success', 'project': get_project_by_id(project_id)})

@main.route('/api/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    message_text = data.get('message')
    
    project_id = session.get('project_id')
    
    response = process_message(message_text, project_id)
    
    if response == 'SHOW_PROJECT_SELECTOR':
        return jsonify({
            'status': 'success',
            'message': 'Please select a project from the list below.',
            'action': 'show_project_selector'
        })
    elif response == 'GENERATE_REPORT':
        return jsonify({
            'status': 'success',
            'message': 'GENERATE_REPORT'
        })
    elif response == 'SHOW_BUDGET_CHART':
        return jsonify({
            'status': 'success',
            'message': 'SHOW_BUDGET_CHART'
        })
    elif response == 'CHECK_WEATHER':
        return jsonify({
            'status': 'success',
            'message': 'CHECK_WEATHER'
        })
    elif response.startswith('ADD_NOTE:'):
        note_text = response.replace('ADD_NOTE:', '').strip()
        return jsonify({
            'status': 'success',
            'message': 'ADD_NOTE',
            'note': note_text
        })
    elif response == 'VIEW_NOTES':
        return jsonify({
            'status': 'success',
            'message': 'VIEW_NOTES'
        })
    
    return jsonify({
        'status': 'success',
        'message': response
    })

@main.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    project_id = data.get('project_id') or session.get('project_id')
    
    if not project_id:
        return jsonify({'status': 'error', 'message': 'No project selected'})
    
    try:
        from app.utils.report_generator import generate_project_report
        project = get_project_by_id(project_id)
        
        if not project:
            return jsonify({'status': 'error', 'message': 'Project not found'})
        
        print(f"Generating report for project: {project['name']}")
        
        try:
            report_path = generate_project_report(project)
            report_filename = os.path.basename(report_path)
            
            print(f"Report generated successfully at: {report_path}")
            
            # Create a download URL
            download_url = url_for('main.download_report', filename=report_filename)
            
            return jsonify({
                'status': 'success', 
                'message': f'Report for {project["name"]} generated successfully',
                'download_url': download_url
            })
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'status': 'error', 'message': f'Error generating report: {str(e)}'})
    except ImportError as e:
        return jsonify({'status': 'error', 'message': f'Required library not installed: {str(e)}'})

@main.route('/download_report/<filename>')
def download_report(filename):
    # Using absolute path to the reports directory
    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
    # Make sure the directory exists
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)
    return send_from_directory(reports_dir, filename, as_attachment=True)

@main.route('/api/generate_budget_chart', methods=['POST'])
def generate_budget_chart():
    data = request.get_json()
    project_id = data.get('project_id') or session.get('project_id')
    
    if not project_id:
        return jsonify({'status': 'error', 'message': 'No project selected'})
    
    from app.utils.chart_generator import generate_budget_chart
    project = get_project_by_id(project_id)
    
    if not project:
        return jsonify({'status': 'error', 'message': 'Project not found'})
    
    try:
        chart_data = generate_budget_chart(project)
        
        return jsonify({
            'status': 'success',
            'message': f'Budget chart for {project["name"]} generated successfully',
            'image_data': chart_data['image_base64'],
            'chart_url': url_for('static', filename=f'charts/{chart_data["filename"]}')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error generating chart: {str(e)}'})

@main.route('/api/get_weather', methods=['POST'])
def get_weather():
    data = request.get_json()
    project_id = data.get('project_id') or session.get('project_id')
    
    if not project_id:
        return jsonify({'status': 'error', 'message': 'No project selected'})
    
    project = get_project_by_id(project_id)
    
    # For demo purposes, we'll use a fixed location based on project id
    # In a real app, you would store location data with each project
    locations = {
        'P001': {'city': 'New York', 'lat': 40.7128, 'lon': -74.0060},
        'P002': {'city': 'Chicago', 'lat': 41.8781, 'lon': -87.6298},
        'P003': {'city': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437},
        'P004': {'city': 'Seattle', 'lat': 47.6062, 'lon': -122.3321},
        'P005': {'city': 'Miami', 'lat': 25.7617, 'lon': -80.1918}
    }
    
    location = locations.get(project_id, {'city': 'New York', 'lat': 40.7128, 'lon': -74.0060})
    
    try:
        # Use a mock response for demo purposes
        # In production, you would use an actual API like:
        # api_key = os.environ.get('WEATHER_API_KEY')
        # url = f"https://api.openweathermap.org/data/2.5/forecast?lat={location['lat']}&lon={location['lon']}&appid={api_key}&units=imperial"
        # response = requests.get(url)
        # weather_data = response.json()
        
        # Mock data
        weather_data = {
            'city': {'name': location['city']},
            'list': [
                {
                    'dt_txt': (datetime.now()).strftime('%Y-%m-%d'),
                    'main': {'temp': 72, 'humidity': 65},
                    'weather': [{'description': 'Partly cloudy', 'icon': '02d'}],
                    'wind': {'speed': 8}
                },
                {
                    'dt_txt': (datetime.now()).strftime('%Y-%m-%d'),
                    'main': {'temp': 75, 'humidity': 60},
                    'weather': [{'description': 'Sunny', 'icon': '01d'}],
                    'wind': {'speed': 5}
                },
                {
                    'dt_txt': (datetime.now()).strftime('%Y-%m-%d'),
                    'main': {'temp': 68, 'humidity': 70},
                    'weather': [{'description': 'Light rain', 'icon': '10d'}],
                    'wind': {'speed': 10}
                }
            ]
        }
        
        forecast_html = f"""
        <div class="weather-forecast">
            <h3>Weather Forecast for {location['city']}</h3>
            <div class="forecast-days">
        """
        
        for day in weather_data['list'][:3]:  # Show 3 days
            forecast_html += f"""
            <div class="forecast-day">
                <div class="date">{day['dt_txt']}</div>
                <div class="temp">{day['main']['temp']}°F</div>
                <div class="description">{day['weather'][0]['description']}</div>
                <div class="details">Humidity: {day['main']['humidity']}% | Wind: {day['wind']['speed']} mph</div>
            </div>
            """
        
        forecast_html += """
            </div>
        </div>
        """
        
        return jsonify({
            'status': 'success',
            'message': f'Weather forecast for {project["name"]} ({location["city"]})',
            'html': forecast_html
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error retrieving weather: {str(e)}'})

@main.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    project_id = session.get('project_id')
    
    if not project_id:
        return jsonify({'status': 'error', 'message': 'No project selected'})
    
    notes_dir = 'data/notes'
    if not os.path.exists(notes_dir):
        os.makedirs(notes_dir)
    
    notes_file = f'{notes_dir}/{project_id}_notes.json'
    
    if request.method == 'GET':
        # Retrieve notes
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                notes = json.load(f)
        else:
            notes = []
            
        return jsonify({
            'status': 'success',
            'notes': notes
        })
    
    elif request.method == 'POST':
        # Add a new note
        data = request.get_json()
        note_text = data.get('note')
        
        if not note_text:
            return jsonify({'status': 'error', 'message': 'Note text is required'})
        
        # Load existing notes
        if os.path.exists(notes_file):
            with open(notes_file, 'r') as f:
                notes = json.load(f)
        else:
            notes = []
        
        # Add new note
        new_note = {
            'id': len(notes) + 1,
            'text': note_text,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'user': session.get('user_id', 'unknown')
        }
        
        notes.append(new_note)
        
        # Save notes
        with open(notes_file, 'w') as f:
            json.dump(notes, f)
        
        return jsonify({
            'status': 'success',
            'message': 'Note added successfully',
            'note': new_note
        })