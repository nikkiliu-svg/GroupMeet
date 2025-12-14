/**
 * Dashboard functionality for GroupMeet.
 */

// API_BASE is defined in auth.js
let calendar = null;

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
});

async function initializeApp() {
    // Check if we're in dev mode (from URL parameter or auth status)
    const urlParams = new URLSearchParams(window.location.search);
    const devModeParam = urlParams.get('dev_mode') === 'true';
    
    // Check auth status and get dev mode info
    const authStatus = await getAuthStatusWithMode();
    const isAuthenticated = authStatus.authenticated;
    const devMode = authStatus.dev_mode || devModeParam;
    
    // Show mode indicator if in dev mode
    if (devMode && !document.getElementById('mode-indicator')) {
        const indicator = document.createElement('div');
        indicator.id = 'mode-indicator';
        indicator.className = 'mode-indicator';
        indicator.textContent = '🔧 DEV MODE';
        document.body.appendChild(indicator);
    }
    
    if (isAuthenticated) {
        showDashboard();
        await loadUserInfo();
        await loadGroups();
        initializeCalendar();
        setupEventListeners();
        setupNavbarListeners();
    } else {
        showHomePage(devMode);
        setupHomeListeners(devMode);
    }
}

function showHomePage(devMode = false) {
    document.getElementById('home-page').classList.remove('hidden');
    document.getElementById('dashboard-page').classList.add('hidden');
    
    // Show appropriate login UI based on mode
    if (devMode) {
        showDevLoginForm();
    } else {
        showPennKeyLoginButton();
    }
}

function showDashboard() {
    document.getElementById('home-page').classList.add('hidden');
    document.getElementById('dashboard-page').classList.remove('hidden');
    // Default to dashboard view
    showDashboardView();
}

function showPennKeyLoginButton() {
    const loginBtn = document.getElementById('login-btn');
    const devLoginForm = document.getElementById('dev-login-form');
    
    if (loginBtn) {
        loginBtn.style.display = 'block';
        loginBtn.textContent = 'Login with PennKey';
    }
    if (devLoginForm) {
        devLoginForm.style.display = 'none';
    }
}

function showDevLoginForm() {
    const loginBtn = document.getElementById('login-btn');
    const devLoginForm = document.getElementById('dev-login-form');
    
    if (loginBtn) {
        loginBtn.style.display = 'none';
    }
    if (devLoginForm) {
        devLoginForm.classList.remove('hidden');
        // Add mode indicator
        if (!document.getElementById('mode-indicator')) {
            const indicator = document.createElement('div');
            indicator.id = 'mode-indicator';
            indicator.className = 'mode-indicator';
            indicator.textContent = '🔧 DEV MODE';
            document.body.appendChild(indicator);
        }
    }
}

function setupHomeListeners(devMode = false) {
    if (devMode) {
        // Setup dev login form
        const devForm = document.getElementById('dev-login-form-element');
        if (devForm) {
            devForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await handleDevLogin();
            });
        }
    } else {
        // Setup PennKey login button
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (typeof redirectToLogin === 'function') {
                    redirectToLogin();
                } else {
                    window.location.href = 'http://localhost:5000/auth/login';
                }
            });
        }
    }
}

async function handleDevLogin() {
    const usernameInput = document.getElementById('dev-username');
    const messageDiv = document.getElementById('dev-login-message');
    const submitBtn = document.querySelector('#dev-login-form-element button[type="submit"]');
    
    if (!usernameInput) {
        console.error('Username input not found');
        return;
    }
    
    const username = usernameInput.value.trim();
    
    if (!username) {
        if (messageDiv) {
            messageDiv.textContent = 'Please enter a username';
            messageDiv.className = 'error-message';
            messageDiv.classList.remove('hidden');
        }
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Logging in...';
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username: username })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Success - reload page to show dashboard
            window.location.href = '/';
        } else {
            if (messageDiv) {
                messageDiv.textContent = `Error: ${data.error || 'Login failed'}`;
                messageDiv.className = 'error-message';
                messageDiv.classList.remove('hidden');
            }
            submitBtn.disabled = false;
            submitBtn.textContent = 'Login';
        }
    } catch (error) {
        console.error('Dev login error:', error);
        if (messageDiv) {
            messageDiv.textContent = `Network error: ${error.message}`;
            messageDiv.className = 'error-message';
            messageDiv.classList.remove('hidden');
        }
        submitBtn.disabled = false;
        submitBtn.textContent = 'Login';
    }
}

function showDashboardView() {
    document.getElementById('dashboard-view').classList.remove('hidden');
    document.getElementById('join-group-view').classList.add('hidden');
    
    // Update navbar active state
    document.getElementById('nav-dashboard').classList.add('active');
    document.getElementById('nav-join').classList.remove('active');
}

function showJoinGroupView() {
    document.getElementById('join-group-view').classList.remove('hidden');
    document.getElementById('dashboard-view').classList.add('hidden');
    
    // Update navbar active state
    document.getElementById('nav-join').classList.add('active');
    document.getElementById('nav-dashboard').classList.remove('active');
    
    // Initialize calendar if not already done
    initializeCalendar();
}

function setupNavbarListeners() {
    // Dashboard link
    document.getElementById('nav-dashboard').addEventListener('click', (e) => {
        e.preventDefault();
        showDashboardView();
        loadGroups(); // Reload groups when switching to dashboard
    });
    
    // Join Group link
    document.getElementById('nav-join').addEventListener('click', (e) => {
        e.preventDefault();
        showJoinGroupView();
    });
}

async function loadUserInfo() {
    const user = await getCurrentUser();
    if (user) {
        const name = user.attributes?.name || user.pennkey || 'Student';
        document.getElementById('user-name').textContent = name;
    }
}

async function loadGroups() {
    const container = document.getElementById('groups-container');
    container.innerHTML = '<p>Loading your groups...</p>';
    
    try {
        // Fetch both groups and pending submissions
        const [groupsResponse, submissionsResponse] = await Promise.all([
            fetch(`${API_BASE}/api/my-groups`, { credentials: 'include' }),
            fetch(`${API_BASE}/api/my-submissions`, { credentials: 'include' })
        ]);
        
        if (groupsResponse.status === 401 || submissionsResponse.status === 401) {
            redirectToLogin();
            return;
        }
        
        const groupsData = await groupsResponse.json();
        const submissionsData = await submissionsResponse.json();
        
        // Get all match IDs for this user to filter out matched submissions
        const matchedSubmissionIds = new Set();
        if (groupsData.groups && groupsData.groups.length > 0) {
            groupsData.groups.forEach(group => {
                if (group.submission_id) {
                    matchedSubmissionIds.add(group.submission_id);
                }
            });
        }
        
        // Filter out matched submissions
        const pendingSubmissions = (submissionsData.submissions || []).filter(sub => {
            return !matchedSubmissionIds.has(sub.id);
        });
        
        // Display groups and pending submissions
        let hasContent = false;
        let html = '';
        
        // Display matched groups
        if (groupsData.groups && groupsData.groups.length > 0) {
            html += displayGroups(groupsData.groups);
            hasContent = true;
        }
        
        // Display pending submissions
        if (pendingSubmissions.length > 0) {
            html += displayPendingSubmissions(pendingSubmissions);
            hasContent = true;
        }
        
        if (hasContent) {
            container.innerHTML = html;
            container.classList.remove('empty');
        } else {
            // Empty state
            container.innerHTML = `
                <div class="empty-groups">
                    <p class="empty-message">You are not in any groups yet.</p>
                    <p class="empty-explanation">Groups are automatically formed when 3 or more students join the same course. Join a course below to get started!</p>
                    <button id="add-group-btn" class="add-group-btn" title="Join a new group">
                        <span class="add-icon">+</span>
                    </button>
                    <p class="empty-hint">Click to join a group</p>
                </div>
            `;
            container.classList.add('empty');
            
            // Add click listener to + button
            const addBtn = document.getElementById('add-group-btn');
            if (addBtn) {
                addBtn.addEventListener('click', () => {
                    showJoinGroupView();
                });
            }
        }
    } catch (error) {
        console.error('Error loading groups:', error);
        container.innerHTML = '<p class="error-message">Error loading groups. Please refresh the page.</p>';
    }
}

function displayGroups(groups) {
    let html = '<div class="groups-section"><h3 class="section-title">Matched Groups</h3>';
    
    groups.forEach(group => {
        html += `
            <div class="group-card" data-match-id="${group.match_id}">
                <div class="group-card-header">
                    <h3>${group.course}</h3>
                    <span class="group-badge">${group.group_size} members</span>
                </div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value">${Math.round(group.availability_overlap * 100)}%</div>
                        <div class="stat-label">Availability Match</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${Math.round(group.preference_alignment * 100)}%</div>
                        <div class="stat-label">Preference Match</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${Math.round(group.avg_compatibility * 100)}%</div>
                        <div class="stat-label">Overall Match</div>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Add click listeners to group cards
    setTimeout(() => {
        document.querySelectorAll('.group-card').forEach(card => {
            card.addEventListener('click', () => {
                const matchId = card.getAttribute('data-match-id');
                if (matchId) {
                    showGroupDetails(matchId);
                }
            });
        });
    }, 0);
    
    return html;
}

function displayPendingSubmissions(submissions) {
    let html = '<div class="pending-section"><h3 class="section-title">Pending Submissions</h3>';
    html += '<p class="pending-explanation">These submissions are waiting for more students to join. Groups form automatically when 3 or more students join the same course.</p>';
    
    // Group by course
    const byCourse = {};
    submissions.forEach(sub => {
        const course = sub.course || 'Unknown';
        if (!byCourse[course]) {
            byCourse[course] = [];
        }
        byCourse[course].push(sub);
    });
    
    Object.keys(byCourse).forEach(course => {
        const courseSubs = byCourse[course];
        const needed = Math.max(0, 3 - courseSubs.length);
        const progress = Math.round((courseSubs.length / 3) * 100);
        
        html += `
            <div class="pending-card">
                <div class="pending-card-header">
                    <h4>${course}</h4>
                    <span class="pending-badge">${courseSubs.length} / 3 students</span>
                </div>
                <div class="pending-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${progress}% complete</span>
                </div>
                <p class="pending-status">
                    ${needed > 0 
                        ? `Waiting for ${needed} more student${needed !== 1 ? 's' : ''} to form a group`
                        : 'Ready to match! Group will be formed soon.'}
                </p>
                <div class="pending-details">
                    <span><strong>Study Preference:</strong> ${courseSubs[0].study_preference || 'Not specified'}</span>
                    <span><strong>Location:</strong> ${courseSubs[0].location_preference || 'Either'}</span>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

async function showGroupDetails(matchId) {
    try {
        const response = await fetch(`${API_BASE}/api/group/${matchId}`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (response.ok && data.match) {
            const match = data.match;
            const modal = document.getElementById('group-modal');
            const modalBody = document.getElementById('modal-body');
            const modalTitle = document.getElementById('modal-title');
            
            modalTitle.textContent = `${match.course} Study Group`;
            
            let html = `
                <div class="stats" style="margin-bottom: 20px;">
                    <div class="stat">
                        <div class="stat-value">${Math.round(match.availability_overlap * 100)}%</div>
                        <div class="stat-label">Availability Overlap</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${Math.round(match.preference_alignment * 100)}%</div>
                        <div class="stat-label">Preference Alignment</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${Math.round(match.avg_compatibility * 100)}%</div>
                        <div class="stat-label">Overall Compatibility</div>
                    </div>
                </div>
                <h3 style="margin-top: 20px;">Group Members</h3>
            `;
            
            match.group_members.forEach(member => {
                html += `
                    <div class="group-member">
                        <h4>${member.name}</h4>
                        <p><strong>Email:</strong> ${member.email}</p>
                        <p><strong>Study Preference:</strong> ${member.study_preference}</p>
                        <p><strong>Location Preference:</strong> ${member.location_preference || 'Either'}</p>
                    </div>
                `;
            });
            
            modalBody.innerHTML = html;
            modal.classList.remove('hidden');
        } else {
            alert('Error loading group details');
        }
    } catch (error) {
        console.error('Error loading group details:', error);
        alert('Error loading group details');
    }
}

function initializeCalendar() {
    if (!calendar) {
        calendar = new AvailabilityCalendar('calendar-container');
    }
}

function setupEventListeners() {
    // Logout button
    document.getElementById('logout-btn').addEventListener('click', () => {
        logout();
    });
    
    // Form submission
    document.getElementById('join-group-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        await submitJoinForm();
    });
    
    // Modal close
    document.querySelector('.close-modal').addEventListener('click', () => {
        document.getElementById('group-modal').classList.add('hidden');
    });
    
    // Close modal on outside click
    document.getElementById('group-modal').addEventListener('click', (e) => {
        if (e.target.id === 'group-modal') {
            document.getElementById('group-modal').classList.add('hidden');
        }
    });
}

async function submitJoinForm() {
    const form = document.getElementById('join-group-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const messageDiv = document.getElementById('form-message');
    
    submitButton.disabled = true;
    submitButton.textContent = 'Submitting...';
    messageDiv.classList.add('hidden');
    
    // Get form data
    const formData = {
        course: document.getElementById('course-select').value,
        availability: calendar.getSelectedSlots(),
        study_preference: document.querySelector('input[name="study_preference"]:checked')?.value,
        location_preference: document.querySelector('input[name="location_preference"]:checked')?.value,
        commitment_confirmed: document.getElementById('commitment').checked
    };
    
    // Validate
    if (formData.availability.length === 0) {
        showMessage('Please select at least one availability time slot.', 'error');
        submitButton.disabled = false;
        submitButton.textContent = 'Join Group';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage(
                `Success! You've joined the group for ${formData.course}. ${data.message || ''}`,
                'success'
            );
            form.reset();
            calendar.clear();
            
            // Switch to dashboard view and reload groups
            showDashboardView();
            await loadGroups();
        } else {
            showMessage(
                `Error: ${data.error || 'Submission failed'}. ${data.errors ? data.errors.join(', ') : ''}`,
                'error'
            );
        }
    } catch (error) {
        showMessage(`Network error: ${error.message}`, 'error');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = 'Join Group';
    }
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('form-message');
    messageDiv.textContent = message;
    messageDiv.className = type === 'error' ? 'error-message' : 'success-message';
    messageDiv.classList.remove('hidden');
    
    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

