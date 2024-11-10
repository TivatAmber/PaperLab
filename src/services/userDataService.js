// src/services/userDataService.js
const { app } = require('electron');
const path = require('path');
const fs = require('fs');

class UserDataService {
    constructor() {
        this.userDataPath = path.join(app.getPath('userData'), 'user.json');
        this.currentUser = null;
        this.initUserData();
    }

    initUserData() {
        if (!fs.existsSync(this.userDataPath)) {
            fs.writeFileSync(this.userDataPath, JSON.stringify({
                users: {},
                currentUser: null
            }));
        }
        this.loadCurrentUser();
    }

    loadCurrentUser() {
        try {
            const data = JSON.parse(fs.readFileSync(this.userDataPath, 'utf8'));
            this.currentUser = data.currentUser;
            return this.currentUser;
        } catch (error) {
            console.error('Error loading current user:', error);
            return null;
        }
    }

    getCurrentUser() {
        return this.currentUser;
    }

    saveUser(userData) {
        try {
            const data = JSON.parse(fs.readFileSync(this.userDataPath, 'utf8'));
            data.users[userData.username] = userData;
            data.currentUser = userData;
            this.currentUser = userData;
            fs.writeFileSync(this.userDataPath, JSON.stringify(data, null, 2));
            return true;
        } catch (error) {
            console.error('Error saving user:', error);
            return false;
        }
    }

    loginUser(username, password, role) {
        try {
            const data = JSON.parse(fs.readFileSync(this.userDataPath, 'utf8'));
            const user = data.users;
            // TODO Associate with database
            if (user["username"] === username && password === data.users["password"] && role === data.users["role"]) {
                data.currentUser = user;
                this.currentUser = user;
                fs.writeFileSync(this.userDataPath, JSON.stringify(data, null, 2));
                return user;
            }
            return null;
        } catch (error) {
            console.error('Error during login:', error);
            return null;
        }
    }

    logoutUser() {
        try {
            const data = JSON.parse(fs.readFileSync(this.userDataPath, 'utf8'));
            data.currentUser = null;
            this.currentUser = null;
            fs.writeFileSync(this.userDataPath, JSON.stringify(data, null, 2));
            return true;
        } catch (error) {
            console.error('Error during logout:', error);
            return false;
        }
    }

    updateUserInfo(username, updateData) {
        try {
            const data = JSON.parse(fs.readFileSync(this.userDataPath, 'utf8'));
            data.users[username] = { ...data.users[username], ...updateData };

            if (this.currentUser && this.currentUser.username === username) {
                data.currentUser = data.users[username];
                this.currentUser = data.currentUser;
            }

            fs.writeFileSync(this.userDataPath, JSON.stringify(data, null, 2));
            return true;
        } catch (error) {
            console.error('Error updating user:', error);
            return false;
        }
    }
}

module.exports = UserDataService;