const {ipcRenderer} = require('electron');

class UserManager {
    static async getCurrentUser() {
        return await ipcRenderer.invoke('get-current-user');
    }

    static async getCurrentTeam() {
        return await ipcRenderer.invoke('get-current-team');
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

    static async createClass(className, classDescription) {
        return await ipcRenderer.invoke('create-class', {className, classDescription});
    }

    static async joinClass(classCode) {
        return await ipcRenderer.invoke('join-class', {classCode});
    }

    static async createTeam(class_id, team_name, description) {
        return await ipcRenderer.invoke('create-team', {class_id, team_name, description});
    }

    static async applyToTeam(group_id) {
        return await ipcRenderer.invoke('apply-to-team', {group_id});
    }

    static async leaveTeam(group_id) {
        return await ipcRenderer.invoke('leave-team', {group_id});
    }

    static async removeTeam(group_id) {
        return await ipcRenderer.invoke('remove-team', {group_id});
    }

    static async AppearInfo() {
        const user = await this.getCurrentUser();
        document.getElementById('student-id').innerText = user['user_id'];
        document.getElementById('nickname').innerText = user['account'];
    }

    static async updateUserDescription(description) {
        return await ipcRenderer.invoke('update-user-description', {description});
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserManager;
} else {
    window.UserManager = UserManager;
}