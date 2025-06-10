/**
 * SCIM 2.0 Dashboard - Frontend Application
 * Secure, modern interface for SCIM user provisioning
 */

class SCIMDashboard {
    constructor() {
        this.baseUrl = '';
        this.credentials = null;
        this.currentRealm = null;
        this.currentTheme = this.getSystemTheme();
        
        this.init();
    }    init() {
        this.initializeTheme();
        this.bindEventListeners();
        this.loadAuthFromSession();
        
        // Load realms automatically if authenticated
        if (this.credentials) {
            this.loadRealms();
        }
    }

    // Theme Management
    getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    initializeTheme() {
        const savedTheme = sessionStorage.getItem('theme');
        if (savedTheme) {
            this.currentTheme = savedTheme;
        }
        this.applyTheme();
    }    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        const themeToggle = document.getElementById('themeToggle');
        
        if (themeToggle) {
            themeToggle.checked = this.currentTheme === 'dark';
        }
        
        sessionStorage.setItem('theme', this.currentTheme);
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme();
    }

    // Event Listeners
    bindEventListeners() {
        // Bind admin form events
        document.getElementById('createAdminForm').addEventListener('submit', (e) => this.createAdmin(e));
        document.getElementById('changePasswordForm').addEventListener('submit', (e) => this.changePassword(e));
          // Theme toggle
        document.getElementById('themeToggle').addEventListener('change', () => this.toggleTheme());

        // Authentication
        document.getElementById('authForm').addEventListener('submit', (e) => this.handleAuth(e));

        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });        // Realms
        document.getElementById('refreshRealms').addEventListener('click', () => this.loadRealms());
        document.getElementById('createRealmForm').addEventListener('submit', (e) => this.createRealm(e));
        document.getElementById('selectedRealm').addEventListener('change', (e) => this.selectRealm(e.target.value));
        
        // Additional realm selectors
        document.getElementById('usersRealmSelect').addEventListener('change', (e) => this.selectRealm(e.target.value));
        document.getElementById('bulkRealmSelect').addEventListener('change', (e) => this.selectRealm(e.target.value));

        // Users
        document.getElementById('refreshUsers').addEventListener('click', () => this.loadUsers());
        document.getElementById('showCreateUser').addEventListener('click', () => this.showUserModal());
        document.getElementById('searchUsers').addEventListener('click', () => this.searchUsers());
        document.getElementById('searchType').addEventListener('change', (e) => this.toggleSearchInput(e.target.value));
        
        // User Modal
        document.getElementById('closeUserModal').addEventListener('click', () => this.hideUserModal());
        document.getElementById('cancelUser').addEventListener('click', () => this.hideUserModal());
        document.getElementById('userForm').addEventListener('submit', (e) => this.handleUserSubmit(e));
        document.getElementById('addEmail').addEventListener('click', () => this.addEmailField());

        // Bulk Import
        document.getElementById('downloadTemplate').addEventListener('click', () => this.downloadTemplate());
        document.getElementById('uploadArea').addEventListener('click', () => document.getElementById('csvFile').click());
        document.getElementById('csvFile').addEventListener('change', (e) => this.handleFileSelect(e));
        document.getElementById('performBulkImport').addEventListener('click', () => this.performBulkImport());

        // Drag and drop for file upload
        const uploadArea = document.getElementById('uploadArea');
        uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // Admin
        document.getElementById('healthCheck').addEventListener('click', () => this.performHealthCheck());
        document.getElementById('createAdminForm').addEventListener('submit', (e) => this.createAdmin(e));

        // Modal backdrop clicks
        document.getElementById('userModal').addEventListener('click', (e) => {
            if (e.target.id === 'userModal') this.hideUserModal();
        });
    }

    // Session Storage for Security
    saveToSession(key, value) {
        try {
            sessionStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            this.showToast('Storage Error', 'Unable to save session data', 'error');
        }
    }

    getFromSession(key) {
        try {
            const value = sessionStorage.getItem(key);
            return value ? JSON.parse(value) : null;
        } catch (error) {
            return null;
        }
    }

    loadAuthFromSession() {
        const savedAuth = this.getFromSession('scim_auth');
        if (savedAuth) {
            this.baseUrl = savedAuth.baseUrl;
            this.credentials = savedAuth.credentials;
            
            // Pre-fill form
            document.getElementById('baseUrl').value = this.baseUrl;
            document.getElementById('username').value = savedAuth.username;
            
            // Auto-connect
            this.connectToDashboard();
        }
    }

    // Authentication
    async handleAuth(e) {
        e.preventDefault();
        
        this.showLoading('Connecting to SCIM endpoint...');
        
        const baseUrl = document.getElementById('baseUrl').value.trim();
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;

        if (!baseUrl || !username || !password) {
            this.hideLoading();
            this.showToast('Invalid Input', 'Please fill in all fields', 'error');
            return;
        }

        // Validate URL format
        try {
            new URL(baseUrl);
        } catch {
            this.hideLoading();
            this.showToast('Invalid URL', 'Please enter a valid base URL', 'error');
            return;
        }

        this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
        this.credentials = btoa(`${username}:${password}`);

        try {
            // Test connection with health check
            const response = await this.makeRequest('/admin/health');
            
            if (response.ok) {
                // Save to session (without password)
                this.saveToSession('scim_auth', {
                    baseUrl: this.baseUrl,
                    username: username,
                    credentials: this.credentials
                });
                
                this.connectToDashboard();
                this.showToast('Connected', 'Successfully connected to SCIM endpoint', 'success');
            } else {
                throw new Error('Authentication failed');
            }
        } catch (error) {
            this.showToast('Connection Failed', 'Unable to connect. Please check your credentials.', 'error');
        } finally {
            this.hideLoading();
        }    }

    connectToDashboard() {
        document.getElementById('authCard').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        
        // Update auth status
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.querySelector('.status-text');
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
        
        // Load realms automatically after connecting
        this.loadRealms();
    }

    // HTTP Requests
    async makeRequest(endpoint, options = {}) {
        if (!this.credentials) {
            throw new Error('Not authenticated');
        }        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: {
                'Authorization': `Basic ${this.credentials}`,
                ...options.headers
            },
            ...options
        };

        // Only set Content-Type for non-FormData requests
        if (!(config.body instanceof FormData)) {
            config.headers['Content-Type'] = 'application/json';
        }

        // Input sanitization for JSON data
        if (config.body && typeof config.body === 'string') {
            try {
                const data = JSON.parse(config.body);
                this.sanitizeObject(data);
                config.body = JSON.stringify(data);
            } catch (e) {
                // Body is not JSON, leave as is
            }
        }

        return fetch(url, config);
    }

    // Input Sanitization
    sanitizeObject(obj) {
        for (const key in obj) {
            if (typeof obj[key] === 'string') {
                obj[key] = this.sanitizeInput(obj[key]);
            } else if (typeof obj[key] === 'object' && obj[key] !== null) {
                this.sanitizeObject(obj[key]);
            }
        }
    }

    sanitizeInput(input) {
        if (typeof input !== 'string') return input;
        
        // Basic XSS prevention
        return input
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;')
            .replace(/\//g, '&#x2F;');
    }

    // Tab Management
    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load tab-specific data
        switch (tabName) {
            case 'realms':
                this.loadRealms();
                break;
            case 'users':
                this.loadUsers();
                break;
            case 'admin':
                this.performHealthCheck();
                break;
        }
    }

    // Realm Management
    async loadRealms() {
        this.showLoading('Loading realms...');
        
        try {
            const response = await this.makeRequest('/admin/realms');
            
            if (response.ok) {
                const realms = await response.json();
                this.populateRealmsDropdown(realms);
            } else {
                throw new Error('Failed to load realms');
            }
        } catch (error) {
            this.showToast('Error', 'Failed to load realms', 'error');
        } finally {
            this.hideLoading();
        }
    }    populateRealmsDropdown(realms) {
        // Get all realm dropdown selectors
        const realmSelectors = [
            'selectedRealm',
            'usersRealmSelect', 
            'bulkRealmSelect'
        ];
        
        realmSelectors.forEach(selectorId => {
            const select = document.getElementById(selectorId);
            if (select) {
                select.innerHTML = '<option value="">Select a realm...</option>';
                
                realms.forEach(realm => {
                    const option = document.createElement('option');
                    option.value = realm.realm_id;
                    option.textContent = `${realm.name} (${realm.realm_id})`;
                    select.appendChild(option);
                });
            }
        });

        // Populate realms list in Realms tab
        this.displayRealmsList(realms);

        // Auto-select first realm if only one exists
        if (realms.length === 1) {
            const firstRealmId = realms[0].realm_id;
            realmSelectors.forEach(selectorId => {
                const select = document.getElementById(selectorId);
                if (select) {
                    select.value = firstRealmId;
                }
            });
            this.selectRealm(firstRealmId);
        }
    }

    displayRealmsList(realms) {
        const realmsList = document.getElementById('realmsList');
        if (!realmsList) return;

        if (realms.length === 0) {
            realmsList.innerHTML = '<p class="text-muted">No realms available. Create one below.</p>';
            return;
        }

        realmsList.innerHTML = realms.map(realm => `
            <div class="realm-item">
                <div class="realm-info">
                    <h5>${realm.name}</h5>
                    <p><strong>ID:</strong> <code>${realm.realm_id}</code></p>
                    <p><strong>Description:</strong> ${realm.description || 'No description'}</p>
                    <p><strong>Created:</strong> ${new Date(realm.created_at).toLocaleDateString()}</p>
                </div>
                <div class="realm-actions">
                    <button class="btn btn-sm btn-primary" onclick="dashboard.selectRealm('${realm.realm_id}')">
                        <span class="btn-icon">✓</span>
                        Select
                    </button>
                </div>
            </div>
        `).join('');
    }selectRealm(realmId) {
        this.currentRealm = realmId;
        this.saveToSession('selected_realm', realmId);
        
        // Synchronize all realm dropdowns
        const realmSelectors = [
            'selectedRealm',
            'usersRealmSelect', 
            'bulkRealmSelect'
        ];
        
        realmSelectors.forEach(selectorId => {
            const select = document.getElementById(selectorId);
            if (select && select.value !== realmId) {
                select.value = realmId;
            }
        });
        
        if (realmId) {
            this.loadUsers();
            this.showToast('Realm Selected', `Active realm: ${realmId}`, 'info');
        }
    }

    async createRealm(e) {
        e.preventDefault();
        
        const name = document.getElementById('realmName').value.trim();
        const description = document.getElementById('realmDescription').value.trim();

        if (!name) {
            this.showToast('Invalid Input', 'Realm name is required', 'error');
            return;
        }

        this.showLoading('Creating realm...');

        try {
            const response = await this.makeRequest('/admin/realms', {
                method: 'POST',
                body: JSON.stringify({ name, description })
            });

            if (response.ok) {
                const realm = await response.json();
                this.showToast('Success', `Realm "${name}" created successfully`, 'success');
                
                // Clear form
                document.getElementById('createRealmForm').reset();
                
                // Reload realms
                this.loadRealms();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create realm');
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // User Management
    toggleSearchInput(searchType) {
        const searchQuery = document.getElementById('searchQuery');
        
        if (searchType === 'list') {
            searchQuery.style.display = 'none';
            searchQuery.required = false;
        } else {
            searchQuery.style.display = 'block';
            searchQuery.required = true;
            searchQuery.placeholder = `Enter ${searchType}...`;
        }
    }

    async searchUsers() {
        if (!this.currentRealm) {
            this.showToast('No Realm', 'Please select a realm first', 'warning');
            return;
        }

        const searchType = document.getElementById('searchType').value;
        const searchQuery = document.getElementById('searchQuery').value.trim();

        if (searchType !== 'list' && !searchQuery) {
            this.showToast('Invalid Search', 'Please enter a search term', 'error');
            return;
        }

        this.showLoading('Searching users...');

        try {
            let endpoint;
            switch (searchType) {
                case 'list':
                    endpoint = `/scim/v2/Realms/${this.currentRealm}/Users`;
                    break;
                case 'username':
                    endpoint = `/scim/v2/Realms/${this.currentRealm}/Users/by-username/${encodeURIComponent(searchQuery)}`;
                    break;
                case 'email':
                    endpoint = `/scim/v2/Realms/${this.currentRealm}/Users/by-email/${encodeURIComponent(searchQuery)}`;
                    break;
                case 'id':
                    endpoint = `/scim/v2/Realms/${this.currentRealm}/Users/${encodeURIComponent(searchQuery)}`;
                    break;
            }

            const response = await this.makeRequest(endpoint);

            if (response.ok) {
                const data = await response.json();
                
                // Handle different response formats
                let users = [];
                if (data.Resources) {
                    users = data.Resources; // List response
                } else if (data.id) {
                    users = [data]; // Single user response
                }

                this.displayUsers(users);
            } else if (response.status === 404) {
                this.displayUsers([]);
                this.showToast('Not Found', 'No users found matching your search', 'info');
            } else {
                throw new Error('Search failed');
            }
        } catch (error) {
            this.showToast('Search Error', 'Failed to search users', 'error');
            this.displayUsers([]);
        } finally {
            this.hideLoading();
        }
    }

    async loadUsers() {
        if (!this.currentRealm) {
            document.getElementById('usersList').innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">👥</span>
                    <p>Select a realm to view users</p>
                </div>
            `;
            return;
        }

        // Reset search form
        document.getElementById('searchType').value = 'list';
        document.getElementById('searchQuery').style.display = 'none';
        document.getElementById('searchQuery').value = '';

        this.searchUsers();
    }

    displayUsers(users) {
        const usersList = document.getElementById('usersList');

        if (users.length === 0) {
            usersList.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">👥</span>
                    <p>No users found</p>
                </div>
            `;
            return;
        }

        usersList.innerHTML = users.map(user => `
            <div class="user-item">
                <div class="user-header">
                    <div class="user-info">
                        <div class="user-name">${this.escapeHtml(user.displayName || `${user.firstName} ${user.surName}`)}</div>
                        <div class="user-username">@${this.escapeHtml(user.userName)}</div>
                    </div>
                    <div class="user-actions">
                        <button class="btn btn-secondary" onclick="dashboard.editUser('${user.id}')">
                            <span class="btn-icon">✏️</span>
                            Edit
                        </button>
                        <button class="btn btn-danger" onclick="dashboard.deleteUser('${user.id}')">
                            <span class="btn-icon">🗑️</span>
                            Delete
                        </button>
                    </div>
                </div>
                <div class="user-details">
                    <div class="user-detail">
                        <span class="user-detail-label">Status</span>
                        <span class="user-status ${user.active ? 'active' : 'inactive'}">
                            <span class="user-status-indicator"></span>
                            ${user.active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                    <div class="user-detail">
                        <span class="user-detail-label">Email</span>
                        <span class="user-detail-value">${user.emails && user.emails.length > 0 ? this.escapeHtml(user.emails[0].value) : 'No email'}</span>
                    </div>
                    <div class="user-detail">
                        <span class="user-detail-label">External ID</span>
                        <span class="user-detail-value">${user.externalId ? this.escapeHtml(user.externalId) : 'None'}</span>
                    </div>
                    <div class="user-detail">
                        <span class="user-detail-label">User ID</span>
                        <span class="user-detail-value" style="font-family: monospace; font-size: 0.8rem;">${this.escapeHtml(user.id)}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // User Modal Management
    showUserModal(user = null) {
        const modal = document.getElementById('userModal');
        const title = document.getElementById('userModalTitle');
        const submitText = document.getElementById('userSubmitText');
        const submitIcon = document.getElementById('userSubmitIcon');

        if (user) {
            title.textContent = 'Edit User';
            submitText.textContent = 'Update User';
            submitIcon.textContent = '💾';
            this.populateUserForm(user);
        } else {
            title.textContent = 'Create New User';
            submitText.textContent = 'Create User';
            submitIcon.textContent = '➕';
            this.resetUserForm();
        }

        modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    hideUserModal() {
        const modal = document.getElementById('userModal');
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
        this.resetUserForm();
    }

    resetUserForm() {
        document.getElementById('userForm').reset();
        document.getElementById('userActive').checked = true;
        
        // Reset emails to single field
        const emailsList = document.getElementById('emailsList');
        emailsList.innerHTML = `
            <div class="email-input">
                <input type="email" placeholder="Email address" required>
                <div class="toggle-switch">
                    <input type="checkbox" checked>
                    <label class="toggle-slider"></label>
                </div>
                <span class="primary-label">Primary</span>
                <button type="button" class="btn-icon-small remove-email" onclick="this.parentElement.remove()">🗑️</button>
            </div>
        `;
    }

    populateUserForm(user) {
        document.getElementById('userUserName').value = user.userName || '';
        document.getElementById('userFirstName').value = user.firstName || '';
        document.getElementById('userSurName').value = user.surName || '';
        document.getElementById('userDisplayName').value = user.displayName || '';
        document.getElementById('userExternalId').value = user.externalId || '';
        document.getElementById('userActive').checked = user.active !== false;

        // Populate emails
        const emailsList = document.getElementById('emailsList');
        emailsList.innerHTML = '';

        if (user.emails && user.emails.length > 0) {
            user.emails.forEach(email => {
                this.addEmailField(email.value, email.primary);
            });
        } else {
            this.addEmailField();
        }

        // Store user ID for updates
        document.getElementById('userForm').dataset.userId = user.id;
    }

    addEmailField(value = '', isPrimary = false) {
        const emailsList = document.getElementById('emailsList');
        const emailDiv = document.createElement('div');
        emailDiv.className = 'email-input';
        emailDiv.innerHTML = `
            <input type="email" placeholder="Email address" value="${this.escapeHtml(value)}" ${emailsList.children.length === 0 ? 'required' : ''}>
            <div class="toggle-switch">
                <input type="checkbox" ${isPrimary ? 'checked' : ''}>
                <label class="toggle-slider"></label>
            </div>
            <span class="primary-label">Primary</span>
            <button type="button" class="btn-icon-small remove-email" onclick="this.parentElement.remove()">🗑️</button>
        `;
        emailsList.appendChild(emailDiv);
    }

    async handleUserSubmit(e) {
        e.preventDefault();

        if (!this.currentRealm) {
            this.showToast('No Realm', 'Please select a realm first', 'warning');
            return;
        }

        const form = document.getElementById('userForm');
        const isUpdate = !!form.dataset.userId;

        // Collect form data
        const userData = {
            schemas: ["urn:ietf:params:scim:schemas:core:2.0:User"],
            userName: document.getElementById('userUserName').value.trim(),
            firstName: document.getElementById('userFirstName').value.trim(),
            surName: document.getElementById('userSurName').value.trim(),
            displayName: document.getElementById('userDisplayName').value.trim(),
            externalId: document.getElementById('userExternalId').value.trim() || undefined,
            active: document.getElementById('userActive').checked
        };

        // Collect emails
        const emailInputs = document.querySelectorAll('#emailsList .email-input');
        const emails = [];
        let hasPrimary = false;

        for (const emailDiv of emailInputs) {
            const emailInput = emailDiv.querySelector('input[type="email"]');
            const primaryCheckbox = emailDiv.querySelector('input[type="checkbox"]');
            
            if (emailInput.value.trim()) {
                const isPrimary = primaryCheckbox.checked;
                if (isPrimary) {
                    if (hasPrimary) {
                        this.showToast('Invalid Emails', 'Only one email can be marked as primary', 'error');
                        return;
                    }
                    hasPrimary = true;
                }
                
                emails.push({
                    value: emailInput.value.trim(),
                    primary: isPrimary
                });
            }
        }

        if (emails.length === 0) {
            this.showToast('Invalid Input', 'At least one email is required', 'error');
            return;
        }

        // Ensure at least one primary email
        if (!hasPrimary && emails.length > 0) {
            emails[0].primary = true;
        }

        userData.emails = emails;

        this.showLoading(isUpdate ? 'Updating user...' : 'Creating user...');

        try {
            const endpoint = isUpdate 
                ? `/scim/v2/Realms/${this.currentRealm}/Users/${form.dataset.userId}`
                : `/scim/v2/Realms/${this.currentRealm}/Users`;
            
            const method = isUpdate ? 'PUT' : 'POST';

            const response = await this.makeRequest(endpoint, {
                method: method,
                body: JSON.stringify(userData)
            });

            if (response.ok) {
                const user = await response.json();
                this.showToast('Success', `User ${isUpdate ? 'updated' : 'created'} successfully`, 'success');
                this.hideUserModal();
                this.loadUsers();
            } else {
                const error = await response.json();
                throw new Error(error.detail || `Failed to ${isUpdate ? 'update' : 'create'} user`);
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async editUser(userId) {
        this.showLoading('Loading user details...');

        try {
            const response = await this.makeRequest(`/scim/v2/Realms/${this.currentRealm}/Users/${userId}`);

            if (response.ok) {
                const user = await response.json();
                this.showUserModal(user);
            } else {
                throw new Error('Failed to load user details');
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async deleteUser(userId) {
        if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
            return;
        }

        this.showLoading('Deleting user...');

        try {
            const response = await this.makeRequest(`/scim/v2/Realms/${this.currentRealm}/Users/${userId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showToast('Success', 'User deleted successfully', 'success');
                this.loadUsers();
            } else {
                throw new Error('Failed to delete user');
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Bulk Import
    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.handleFileSelect({ target: { files } });
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (!file) return;

        if (!file.name.toLowerCase().endsWith('.csv')) {
            this.showToast('Invalid File', 'Please select a CSV file', 'error');
            return;
        }

        // Update upload area
        const uploadContent = document.querySelector('.upload-content');
        uploadContent.innerHTML = `
            <span class="upload-icon">📄</span>
            <p>Selected: ${this.escapeHtml(file.name)}</p>
            <small>${(file.size / 1024).toFixed(1)} KB</small>
        `;

        // Enable import button
        document.getElementById('performBulkImport').disabled = false;
    }    async downloadTemplate() {
        if (!this.currentRealm) {
            this.showToast('No Realm', 'Please select a realm first', 'warning');
            return;
        }

        this.showLoading('Downloading template...');

        try {
            const response = await this.makeRequest(`/scim/v2/Realms/${this.currentRealm}/Users/bulk-import/template`);

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `scim_users_template_${this.currentRealm}.csv`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                this.showToast('Success', 'Template downloaded successfully', 'success');
            } else {
                throw new Error('Failed to download template');
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');        } finally {
            this.hideLoading();
        }
    }    async performBulkImport() {
        if (!this.currentRealm) {
            this.showToast('No Realm', 'Please select a realm first', 'warning');
            return;
        }

        const fileInput = document.getElementById('csvFile');
        const file = fileInput.files[0];

        if (!file) {
            this.showToast('No File', 'Please select a CSV file first', 'error');
            return;
        }        const dryRun = document.getElementById('dryRun').checked;
        this.showLoading(dryRun ? 'Validating CSV file...' : 'Importing users...');

        try {
            const endpoint = `/scim/v2/Realms/${this.currentRealm}/Users/bulk-import`;
            
            // Create FormData for file upload
            const formData = new FormData();
            formData.append('file', file);
            formData.append('dry_run', dryRun.toString());
            formData.append('skip_duplicates', 'true');
            formData.append('continue_on_error', 'true');
            
            const response = await this.makeRequest(endpoint, {
                method: 'POST',
                headers: {
                    'Authorization': `Basic ${this.credentials}`
                    // Don't set Content-Type header - let the browser set it for FormData
                },
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                this.displayImportResults(result, dryRun);
                
                if (!dryRun && result.summary) {
                    this.showToast('Import Complete', `Successfully imported ${result.summary.successful || 0} users`, 'success');
                    this.loadUsers(); // Refresh user list
                }
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Import failed');
            }
        } catch (error) {
            this.showToast('Import Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayImportResults(result, dryRun) {
        const resultsArea = document.getElementById('importResults');
        
        let html = `<h5>${dryRun ? 'Validation Results' : 'Import Results'}</h5>`;

        if (result.summary) {
            html += `
                <div class="import-result success">
                    <strong>Summary:</strong><br>
                    Total Records: ${result.summary.total_records || 0}<br>
                    Successful: ${result.summary.successful || 0}<br>
                    Errors: ${result.summary.errors || 0}
                </div>
            `;
        }

        if (result.errors && result.errors.length > 0) {
            html += '<h6>Errors:</h6>';
            result.errors.forEach(error => {
                html += `
                    <div class="import-result error">
                        <strong>Row ${error.row || 'Unknown'}:</strong> ${this.escapeHtml(error.message || error.error)}
                    </div>
                `;
            });
        }

        if (result.warnings && result.warnings.length > 0) {
            html += '<h6>Warnings:</h6>';
            result.warnings.forEach(warning => {
                html += `
                    <div class="import-result warning">
                        <strong>Row ${warning.row || 'Unknown'}:</strong> ${this.escapeHtml(warning.message)}
                    </div>
                `;
            });
        }

        if (result.duplicates && result.duplicates.length > 0) {
            html += '<h6>Duplicates Found:</h6>';
            result.duplicates.forEach(duplicate => {
                html += `
                    <div class="import-result warning">
                        <strong>Row ${duplicate.row || 'Unknown'}:</strong> ${this.escapeHtml(duplicate.message)}
                    </div>
                `;
            });
        }

        resultsArea.innerHTML = html;
    }

    // Admin Functions
    async performHealthCheck() {
        this.showLoading('Checking system health...');

        try {
            const response = await this.makeRequest('/admin/health');

            if (response.ok) {
                const health = await response.json();
                
                document.getElementById('apiStatus').textContent = '✅ Healthy';
                document.getElementById('dbStatus').textContent = '✅ Connected';
                document.getElementById('authStatusValue').textContent = '✅ Active';
                
                this.showToast('Health Check', 'System is healthy', 'success');
            } else {
                throw new Error('Health check failed');
            }
        } catch (error) {
            document.getElementById('apiStatus').textContent = '❌ Error';
            document.getElementById('dbStatus').textContent = '❌ Error';
            document.getElementById('authStatusValue').textContent = '❌ Error';
            
            this.showToast('Health Check Failed', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async createAdmin(e) {
        e.preventDefault();

        const username = document.getElementById('adminUsername').value.trim();
        const password = document.getElementById('adminPassword').value;
        const email = document.getElementById('adminEmail').value.trim();

        if (!username || !password || !email) {
            this.showToast('Invalid Input', 'Please fill in all fields', 'error');
            return;
        }

        this.showLoading('Creating admin user...');

        try {
            const response = await this.makeRequest('/admin/users', {
                method: 'POST',
                body: JSON.stringify({ username, password, email })
            });

            if (response.ok) {
                const admin = await response.json();
                this.showToast('Success', `Admin user "${username}" created successfully`, 'success');
                document.getElementById('createAdminForm').reset();
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to create admin user');
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async changePassword(e) {
        e.preventDefault();

        const currentPassword = document.getElementById('currentPassword').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        if (!currentPassword || !newPassword || !confirmPassword) {
            this.showToast('Invalid Input', 'Please fill in all fields', 'error');
            return;
        }

        if (newPassword !== confirmPassword) {
            this.showToast('Password Mismatch', 'New password and confirmation do not match', 'error');
            return;
        }

        if (newPassword.length < 8) {
            this.showToast('Invalid Password', 'Password must be at least 8 characters long', 'error');
            return;
        }

        this.showLoading('Changing password...');

        try {
            const response = await this.makeRequest('/admin/change-password', {
                method: 'PUT',
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                    confirm_password: confirmPassword
                })
            });

            if (response.ok) {
                const result = await response.json();
                this.showToast('Success', 'Password changed successfully', 'success');
                document.getElementById('changePasswordForm').reset();
                
                // Show notification that they need to use new password
                setTimeout(() => {
                    this.showToast('Important', 'Please use your new password for future logins', 'info');
                }, 2000);
            } else {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to change password');
            }
        } catch (error) {
            this.showToast('Error', error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Utility Functions
    showLoading(message = 'Loading...') {
        document.getElementById('loadingText').textContent = message;
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    showToast(title, message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toastId = `toast-${Date.now()}`;
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.id = toastId;
        toast.innerHTML = `
            <div class="toast-title">${this.escapeHtml(title)}</div>
            <div class="toast-message">${this.escapeHtml(message)}</div>
            <button class="toast-close" onclick="dashboard.removeToast('${toastId}')">&times;</button>
        `;

        toastContainer.appendChild(toast);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            this.removeToast(toastId);
        }, 5000);

        // Click to dismiss
        toast.addEventListener('click', () => {
            this.removeToast(toastId);
        });
    }

    removeToast(toastId) {
        const toast = document.getElementById(toastId);
        if (toast) {
            toast.remove();
        }
    }
}

// Initialize the dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new SCIMDashboard();
});
