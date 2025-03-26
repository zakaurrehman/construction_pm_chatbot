// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messagesContainer = document.getElementById('messages-container');
    const userSelector = document.getElementById('user-selector');
    const projectSummary = document.getElementById('project-summary');
    
    let currentProjectId = null;

    // Initialize project buttons if available
    initializeProjectButtons();
    
    // Add event listener to user selector
    if (userSelector) {
        userSelector.addEventListener('change', function() {
            switchUser(this.value);
        });
    }

    // Add event listener to message form
    messageForm.addEventListener('submit', function(event) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            addMessage('user', message);
            sendMessage(message);
            messageInput.value = '';
        }
    });

    function addMessage(sender, text) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `message-${sender}`);
        messageElement.textContent = text;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addFormattedMessage(sender, html) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `message-${sender}`);
        messageElement.innerHTML = html;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function sendMessage(message) {
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.message === 'GENERATE_REPORT') {
                    generateReport();
                    addMessage('bot', 'Generating report, please wait...');
                } else if (data.message === 'SHOW_BUDGET_CHART') {
                    generateBudgetChart();
                    addMessage('bot', 'Generating budget chart, please wait...');
                } else if (data.message === 'CHECK_WEATHER') {
                    checkWeather();
                    addMessage('bot', 'Checking weather forecast, please wait...');
                } else if (data.message === 'ADD_NOTE') {
                    addNote(data.note);
                    addMessage('bot', 'Adding your note, please wait...');
                } else if (data.message === 'VIEW_NOTES') {
                    viewNotes();
                    addMessage('bot', 'Retrieving notes, please wait...');
                } else if (data.action === 'show_project_selector') {
                    showProjectSelector();
                    addMessage('bot', data.message);
                } else {
                    addMessage('bot', data.message);
                }
            } else {
                addMessage('bot', `Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error processing your message.');
        });
    }

    function showProjectSelector() {
        const projectSelector = document.getElementById('project-selector');
        if (projectSelector) {
            projectSelector.style.display = 'block';
            
            // Load project data for buttons
            loadProjectData();
        }
    }
    
    function switchUser(userId) {
        fetch('/api/switch_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Reload the page to update the UI
                window.location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    function initializeProjectButtons() {
        const projectButtons = document.querySelectorAll('.project-btn');
        console.log('Found project buttons:', projectButtons.length);
        
        projectButtons.forEach(button => {
            button.addEventListener('click', function() {
                const projectId = this.getAttribute('data-project-id');
                console.log('Project button clicked:', projectId);
                selectProject(projectId);
            });
        });
        
        // Load project data for buttons if they exist
        if (projectButtons.length > 0) {
            loadProjectData();
        }
    }
    
    function loadProjectData() {
        console.log('Loading project data...');
        fetch('/api/projects')
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(projects => {
            console.log('Projects data:', projects);
            
            if (Object.keys(projects).length === 0) {
                console.warn('No projects returned from API');
                return;
            }
            
            const projectButtons = document.querySelectorAll('.project-btn');
            console.log('Updating buttons:', projectButtons.length);
            
            projectButtons.forEach(button => {
                const projectId = button.getAttribute('data-project-id');
                console.log('Checking project ID:', projectId);
                
                if (projects[projectId]) {
                    console.log('Found project:', projects[projectId].name);
                    button.textContent = `${projects[projectId].name} (${projects[projectId].status})`;
                } else {
                    console.log(`Project ${projectId} not found in data`);
                }
            });
        })
        .catch(error => {
            console.error('Error loading projects:', error);
        });
    }
    
    function selectProject(projectId) {
        fetch('/api/select_project', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ project_id: projectId }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                currentProjectId = projectId;
                document.getElementById('project-selector').style.display = 'none';
                updateProjectSummary(data.project);
                addMessage('bot', `Project "${data.project.name}" selected. What would you like to know?`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
    
    function updateProjectSummary(project) {
        const projectName = document.getElementById('project-name');
        const projectStatus = document.getElementById('project-status');
        const progressBar = document.getElementById('progress-bar');
        const completionPercentage = document.getElementById('completion-percentage');
        const projectTimeline = document.getElementById('project-timeline');
        
        if (projectName && projectStatus && progressBar && completionPercentage && projectTimeline) {
            projectName.textContent = project.name;
            projectStatus.textContent = project.status;
            projectStatus.className = `project-status status-${project.status.toLowerCase().replace(' ', '-')}`;
            progressBar.style.width = `${project.completion}%`;
            completionPercentage.textContent = `Completion: ${project.completion}%`;
            projectTimeline.textContent = project.timeline;
            
            projectSummary.style.display = 'block';
        }
    }

    // Feature 1: Generate PDF Report
    function generateReport() {
        fetch('/api/generate_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const message = `${data.message}. <a href="${data.download_url}" target="_blank" class="download-link">Download Report</a>`;
                addFormattedMessage('bot', message);
            } else {
                addMessage('bot', `Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error generating the report.');
        });
    }

    // Feature 2: Generate Budget Chart
    function generateBudgetChart() {
        fetch('/api/generate_budget_chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const message = `
                    <div>
                        <p>${data.message}</p>
                        <img src="data:image/png;base64,${data.image_data}" alt="Budget Chart" class="chart-image">
                    </div>
                `;
                addFormattedMessage('bot', message);
            } else {
                addMessage('bot', `Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error generating the chart.');
        });
    }

    // Feature 3: Check Weather
    function checkWeather() {
        fetch('/api/get_weather', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({}),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const message = `
                    <div>
                        <p>${data.message}</p>
                        ${data.html}
                    </div>
                `;
                addFormattedMessage('bot', message);
            } else {
                addMessage('bot', `Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error checking the weather.');
        });
    }

    // Feature 4: Add Note
    function addNote(noteText) {
        fetch('/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ note: noteText }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                addMessage('bot', `Note added successfully: "${data.note.text}"`);
            } else {
                addMessage('bot', `Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error adding the note.');
        });
    }

    // Feature 5: View Notes
    function viewNotes() {
        fetch('/api/notes', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                if (data.notes.length === 0) {
                    addMessage('bot', 'No notes found for this project.');
                } else {
                    let notesHtml = `<div class="notes-container"><h3>Project Notes</h3><ul class="notes-list">`;
                    
                    data.notes.forEach(note => {
                        notesHtml += `
                            <li class="note-item">
                                <div class="note-header">
                                    <span class="note-date">${note.date}</span>
                                    <span class="note-user">By: ${note.user}</span>
                                </div>
                                <div class="note-text">${note.text}</div>
                            </li>
                        `;
                    });
                    
                    notesHtml += `</ul></div>`;
                    addFormattedMessage('bot', notesHtml);
                }
            } else {
                addMessage('bot', `Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', 'Sorry, there was an error retrieving the notes.');
        });
    }
});