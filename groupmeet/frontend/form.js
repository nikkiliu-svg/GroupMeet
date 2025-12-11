/**
 * Form submission handler for GroupMeet.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : ''; // Empty means same origin (Heroku will serve both)

// Handle form submission
document.getElementById('submission-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const form = e.target;
    const submitButton = form.querySelector('button[type="submit"]');
    const messageDiv = document.getElementById('form-message');
    
    // Disable submit button
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';
    messageDiv.classList.add('hidden');
    
    // Collect form data
    const formData = {
        name: document.getElementById('name').value.trim(),
        email: document.getElementById('email').value.trim(),
        course: document.getElementById('course').value,
        availability: Array.from(document.querySelectorAll('input[name="availability"]:checked'))
            .map(cb => cb.value),
        study_preference: document.querySelector('input[name="study_preference"]:checked')?.value,
        commitment_confirmed: document.getElementById('commitment').checked
    };
    
    // Validate
    if (formData.availability.length === 0) {
        showMessage('Please select at least one availability time slot.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Submit';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(
                `✅ Success! Your submission has been received. Submission ID: ${data.id}`,
                'success'
            );
            form.reset();
            
            // Store submission ID for results lookup
            localStorage.setItem('lastSubmissionId', data.id);
        } else {
            showMessage(
                `❌ Error: ${data.error || 'Submission failed'}. ${data.errors ? data.errors.join(', ') : ''}`,
                'error'
            );
        }
    } catch (error) {
        showMessage(`❌ Network error: ${error.message}`, 'error');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Submit';
    }
});

function showMessage(message, type) {
    const messageDiv = document.getElementById('form-message');
    messageDiv.textContent = message;
    messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
    messageDiv.classList.remove('hidden');
    
    // Scroll to message
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showForm() {
    document.getElementById('form-view').classList.remove('hidden');
    document.getElementById('admin-view').classList.add('hidden');
    document.querySelectorAll('.nav button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.nav button')[0].classList.add('active');
}

function showAdmin() {
    document.getElementById('form-view').classList.add('hidden');
    document.getElementById('admin-view').classList.remove('hidden');
    document.querySelectorAll('.nav button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.nav button')[1].classList.add('active');
    loadSubmissions();
}

// Make functions available globally
window.showForm = showForm;
window.showAdmin = showAdmin;

