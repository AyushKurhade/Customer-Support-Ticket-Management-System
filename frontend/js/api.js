/**
 * Centralized API Client & Helper Functions
 */

const API = {
    async request(url, options = {}) {
        options.headers = {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        };

        try {
            const response = await fetch(url, options);
            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                if (response.status === 401 && !url.includes('/api/auth/me')) {
                    window.location.href = '/login.html';
                }
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },

    post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async getCurrentUser() {
        return this.get('/api/auth/me');
    },

    async logout() {
        await this.post('/api/auth/logout', {});
        window.location.href = '/login.html';
    }
};

// UI Formatting Helpers
function formatStatusBadge(statusName) {
    const s = (statusName || '').toLowerCase().replace(' ', '-');
    return `<span class="badge badge-status-${s}">${statusName}</span>`;
}

function formatPriorityBadge(priorityName) {
    const p = (priorityName || '').toLowerCase();
    return `<span class="badge badge-prio-${p}">${priorityName}</span>`;
}

function formatDate(isoStr) {
    if (!isoStr) return 'N/A';
    const d = new Date(isoStr);
    return d.toLocaleString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}
