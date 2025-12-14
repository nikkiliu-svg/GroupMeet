/**
 * Admin dashboard functionality for GroupMeet.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : ''; // Empty means same origin (Heroku will serve both)

async function loadSubmissions() {
    const tableDiv = document.getElementById('submissions-table');
    const messageDiv = document.getElementById('admin-message');
    
    tableDiv.innerHTML = '<p>Loading submissions...</p>';
    messageDiv.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/submissions`);
        const data = await response.json();
        
        if (response.ok) {
            displaySubmissions(data.submissions || []);
        } else {
            showAdminMessage(`Error loading submissions: ${data.error}`, 'error');
        }
    } catch (error) {
        showAdminMessage(`Network error: ${error.message}`, 'error');
        tableDiv.innerHTML = '';
    }
}

function displaySubmissions(submissions) {
    const tableDiv = document.getElementById('submissions-table');
    
    if (submissions.length === 0) {
        tableDiv.innerHTML = '<p>No submissions yet.</p>';
        return;
    }
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Course</th>
                    <th>Availability</th>
                    <th>Preference</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    submissions.forEach(sub => {
        html += `
            <tr>
                <td>${sub.id ? sub.id.substring(0, 8) + '...' : 'N/A'}</td>
                <td>${sub.name || 'N/A'}</td>
                <td>${sub.email || 'N/A'}</td>
                <td>${sub.course || 'N/A'}</td>
                <td>${Array.isArray(sub.availability) ? sub.availability.length + ' slots' : 'N/A'}</td>
                <td>${sub.study_preference || 'N/A'}</td>
            </tr>
        `;
    });
    
    html += `
            </tbody>
        </table>
        <p style="margin-top: 15px; color: #666;">Total: ${submissions.length} submissions</p>
    `;
    
    tableDiv.innerHTML = html;
}

async function runMatching() {
    const messageDiv = document.getElementById('admin-message');
    const matchButton = event.target;
    
    matchButton.disabled = true;
    matchButton.textContent = 'Generating matches...';
    messageDiv.classList.add('hidden');
    
    try {
        const response = await fetch(`${API_BASE}/match`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAdminMessage(
                `✅ Matching complete! Created ${data.matches_created} groups. ` +
                `${data.unmatched_count} students unmatched. ` +
                `Check console for email notifications.`,
                'success'
            );
            
            // Display match results
            if (data.matches && data.matches.length > 0) {
                let matchesHtml = '<h3 style="margin-top: 20px;">Match Results:</h3><ul>';
                data.matches.forEach(match => {
                    matchesHtml += `<li>Course: ${match.course}, Group Size: ${match.group_size}</li>`;
                });
                matchesHtml += '</ul>';
                
                if (data.unmatched_students && data.unmatched_students.length > 0) {
                    matchesHtml += '<h3 style="margin-top: 20px;">Unmatched Students:</h3><ul>';
                    data.unmatched_students.forEach(student => {
                        matchesHtml += `<li>${student.name} (${student.email})</li>`;
                    });
                    matchesHtml += '</ul>';
                }
                
                document.getElementById('submissions-table').innerHTML += matchesHtml;
            }
        } else {
            showAdminMessage(`❌ Error: ${data.error}`, 'error');
        }
    } catch (error) {
        showAdminMessage(`❌ Network error: ${error.message}`, 'error');
    } finally {
        matchButton.disabled = false;
        matchButton.textContent = 'Generate Matches';
    }
}

function exportData() {
    // Simple CSV export
    fetch(`${API_BASE}/submissions`)
        .then(response => response.json())
        .then(data => {
            if (!data.submissions || data.submissions.length === 0) {
                showAdminMessage('No data to export', 'error');
                return;
            }
            
            // Create CSV
            const headers = ['ID', 'Name', 'Email', 'Course', 'Availability', 'Study Preference'];
            const rows = data.submissions.map(sub => [
                sub.id || '',
                sub.name || '',
                sub.email || '',
                sub.course || '',
                Array.isArray(sub.availability) ? sub.availability.join('; ') : '',
                sub.study_preference || ''
            ]);
            
            const csv = [
                headers.join(','),
                ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
            ].join('\n');
            
            // Download
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `groupmeet-submissions-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showAdminMessage('✅ Data exported successfully', 'success');
        })
        .catch(error => {
            showAdminMessage(`❌ Export error: ${error.message}`, 'error');
        });
}

function showAdminMessage(message, type) {
    const messageDiv = document.getElementById('admin-message');
    messageDiv.textContent = message;
    messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
    messageDiv.classList.remove('hidden');
}

// Make functions available globally
window.loadSubmissions = loadSubmissions;
window.runMatching = runMatching;
window.exportData = exportData;

