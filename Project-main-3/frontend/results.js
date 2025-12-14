/**
 * Results page for displaying match information.
 * This page is typically accessed via a unique URL: /results/<student_id>
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : ''; // Empty means same origin (Heroku will serve both)

// Get student ID from URL
function getStudentIdFromURL() {
    const path = window.location.pathname;
    const match = path.match(/\/results\/([^\/]+)/);
    return match ? match[1] : null;
}

// Get student ID from localStorage as fallback
function getStudentId() {
    return getStudentIdFromURL() || localStorage.getItem('lastSubmissionId');
}

async function loadResults() {
    const studentId = getStudentId();
    
    if (!studentId) {
        document.body.innerHTML = `
            <div style="max-width: 800px; margin: 50px auto; padding: 40px; background: white; border-radius: 12px;">
                <h1>No Student ID Found</h1>
                <p>Please provide a student ID in the URL or submit a form first.</p>
                <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 6px;">Go to Form</a>
            </div>
        `;
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/results/${studentId}`);
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            displayError(data.error || 'Failed to load results');
        }
    } catch (error) {
        displayError(`Network error: ${error.message}`);
    }
}

function displayResults(data) {
    const container = document.createElement('div');
    container.style.cssText = 'max-width: 800px; margin: 50px auto; padding: 40px; background: white; border-radius: 12px;';
    
    if (data.message) {
        container.innerHTML = `
            <h1>🎓 GroupMeet Results</h1>
            <p style="margin-top: 20px; color: #666;">${data.message}</p>
            <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 6px;">Submit Form</a>
        `;
    } else {
        const groupMembersHtml = data.group_members.map(member => `
            <div class="group-member">
                <h4>${member.name}</h4>
                <p><strong>Email:</strong> ${member.email}</p>
                <p><strong>Study Preference:</strong> ${member.study_preference}</p>
            </div>
        `).join('');
        
        container.innerHTML = `
            <h1>🎓 Your Study Group Match</h1>
            
            <div style="margin-top: 30px;">
                <h2>Your Information</h2>
                <p><strong>Name:</strong> ${data.student.name}</p>
                <p><strong>Course:</strong> ${data.student.course}</p>
                <p><strong>Study Preference:</strong> ${data.student.study_preference}</p>
            </div>
            
            <div style="margin-top: 30px;">
                <h2>Your Group Members</h2>
                ${groupMembersHtml || '<p>No group members found.</p>'}
            </div>
            
            <div class="stats" style="margin-top: 30px;">
                <div class="stat-card">
                    <div class="stat-value">${(data.availability_overlap * 100).toFixed(0)}%</div>
                    <div class="stat-label">Availability Overlap</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(data.preference_alignment * 100).toFixed(0)}%</div>
                    <div class="stat-label">Preference Alignment</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${(data.avg_compatibility * 100).toFixed(0)}%</div>
                    <div class="stat-label">Overall Compatibility</div>
                </div>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>Submit Feedback</h3>
                <form id="feedback-form" style="margin-top: 15px;">
                    <div style="margin-bottom: 15px;">
                        <label>Rating (1-5 stars):</label>
                        <select name="rating" required style="width: 100%; padding: 10px; margin-top: 5px;">
                            <option value="">Select rating</option>
                            <option value="5">5 - Excellent</option>
                            <option value="4">4 - Very Good</option>
                            <option value="3">3 - Good</option>
                            <option value="2">2 - Fair</option>
                            <option value="1">1 - Poor</option>
                        </select>
                    </div>
                    <div style="margin-bottom: 15px;">
                        <label>Comments (optional):</label>
                        <textarea name="comments" rows="4" style="width: 100%; padding: 10px; margin-top: 5px; border: 2px solid #e0e0e0; border-radius: 6px;"></textarea>
                    </div>
                    <button type="submit" style="padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 6px; cursor: pointer;">Submit Feedback</button>
                </form>
                <div id="feedback-message" style="margin-top: 15px;"></div>
            </div>
            
            <a href="/" style="display: inline-block; margin-top: 30px; padding: 10px 20px; background: #6c757d; color: white; text-decoration: none; border-radius: 6px;">Back to Form</a>
        `;
        
        // Add feedback form handler
        const feedbackForm = container.querySelector('#feedback-form');
        if (feedbackForm) {
            feedbackForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await submitFeedback(data.match_id, data.student.id, feedbackForm);
            });
        }
    }
    
    document.body.innerHTML = '';
    document.body.appendChild(container);
}

function displayError(message) {
    document.body.innerHTML = `
        <div style="max-width: 800px; margin: 50px auto; padding: 40px; background: white; border-radius: 12px;">
            <h1>Error</h1>
            <p style="margin-top: 20px; color: #d32f2f;">${message}</p>
            <a href="/" style="display: inline-block; margin-top: 20px; padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 6px;">Go to Form</a>
        </div>
    `;
}

async function submitFeedback(matchId, studentId, form) {
    const formData = new FormData(form);
    const messageDiv = document.getElementById('feedback-message');
    
    const feedbackData = {
        match_id: matchId,
        student_id: studentId,
        rating: parseInt(formData.get('rating')),
        comments: formData.get('comments') || ''
    };
    
    try {
        const response = await fetch(`${API_BASE}/feedback`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            messageDiv.innerHTML = '<div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 6px;">✅ Feedback submitted successfully!</div>';
            form.reset();
        } else {
            messageDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 6px;">❌ Error: ${data.error}</div>`;
        }
    } catch (error) {
        messageDiv.innerHTML = `<div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 6px;">❌ Network error: ${error.message}</div>`;
    }
}

// Load results when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadResults);
} else {
    loadResults();
}

