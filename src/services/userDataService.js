// src/services/userDataService.js
const { app } = require('electron');
const path = require('path');
const fs = require('fs');
const UserHttpHandler = require('../http/userHttpHandler');

class UserDataService {
    constructor() {
        this.currentUser = null;
        this.currentTeam = null;
    }

    getCurrentUser() {
        return this.currentUser;
    }

    getCurrentTeam() {
        return this.currentTeam;
    }

    async saveUser(userData) {
        try {
            const result = await UserHttpHandler.sentPostRequest('register', userData);
            console.log("Register Result: ", result);
            if (result['success'] === true) {
                console.log("Register success");
                return true;
            }
            console.log("Register failed");
            return false;
        } catch (error) {
            console.error('Error saving user:', error);
            return false;
        }
    }

    async loginUser(account, password, role) {
        try {
            const result = await UserHttpHandler.sentPostRequest('log', { account, password, identity: role });
            console.log("Login Result: ", result);
            if (result['success'] === true) {
                console.log("Login success");
                this.currentUser = {
                    account: account,
                    role: role,
                    user_id: result['user_id'],
                    description: result['description']
                };
                console.log(this.currentUser)
                return this.currentUser;
            }
            console.log("Login failed");
            return null;
        } catch (error) {
            console.error('Error during login:', error);
            return null;
        }
    }

    logoutUser() {
        try {
            this.currentUser = null;
            return true;
        } catch (error) {
            console.error('Error during logout:', error);
            return false;
        }
    }

    updateUserDescription(description) {
        try {
            this.currentUser['description'] = description;
            const result = UserHttpHandler.sentPostRequest('update_user_description', {
                user_id: this.currentUser['user_id'],
                new_description: description
            });
            return result;
        } catch (error) {
            console.error('Error updating user description:', error);
            return false;
        }
    }
}

module.exports = UserDataService;