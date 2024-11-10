const {ipcRenderer} = require('electron');

class UserManager {
    static async getCurrentUser() {
        return await ipcRenderer.invoke('get-current-user');
    }

    static async login(username, password, role) {
        return await ipcRenderer.invoke('login-user', { username, password, role});
    }

    static async register(userData) {
        return await ipcRenderer.invoke('register-user', userData);
    }

    static async logout() {
        return await ipcRenderer.invoke('logout-user');
    }

    static async updateUser(username, updateData) {
        return await ipcRenderer.invoke('update-user', { username, updateData });
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserManager;
} else {
    window.UserManager = UserManager;
}