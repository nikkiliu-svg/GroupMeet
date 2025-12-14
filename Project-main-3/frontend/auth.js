/**
 * Authentication handling for GroupMeet.
 */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : ''; // Empty means same origin (Heroku will serve both)
/**
 * Check if user is authenticated.
 */
async function checkAuthStatus() {
    try {
        const response = await fetch(`${API_BASE}/auth/status`, {
            credentials: 'include'
        });
        const data = await response.json();
        return data.authenticated === true;
    } catch (error) {
        console.error('Auth check failed:', error);
        return false;
    }
}

/**
 * Get authentication status with mode information.
 */
async function getAuthStatusWithMode() {
    try {
        const response = await fetch(`${API_BASE}/auth/status`, {
            credentials: 'include'
        });
        const data = await response.json();
        return {
            authenticated: data.authenticated === true,
            dev_mode: data.dev_mode === true
        };
    } catch (error) {
        console.error('Auth check failed:', error);
        return { authenticated: false, dev_mode: false };
    }
}

/**
 * Get current user info.
 */
async function getCurrentUser() {
    try {
        const response = await fetch(`${API_BASE}/auth/status`, {
            credentials: 'include'
        });
        const data = await response.json();
        if (data.authenticated) {
            return {
                pennkey: data.pennkey,
                attributes: data.attributes || {}
            };
        }
        return null;
    } catch (error) {
        console.error('Get user failed:', error);
        return null;
    }
}

/**
 * Redirect to login.
 */
function redirectToLogin() {
    window.location.href = `${API_BASE}/auth/login`;
}

/**
 * Logout user.
 */
async function logout() {
    try {
        await fetch(`${API_BASE}/auth/logout`, {
            credentials: 'include',
            method: 'GET'
        });
        // Redirect will happen server-side
        window.location.href = '/';
    } catch (error) {
        console.error('Logout failed:', error);
        window.location.href = '/';
    }
}

// Export functions
window.checkAuthStatus = checkAuthStatus;
window.getCurrentUser = getCurrentUser;
window.redirectToLogin = redirectToLogin;
window.logout = logout;
window.getAuthStatusWithMode = getAuthStatusWithMode;

