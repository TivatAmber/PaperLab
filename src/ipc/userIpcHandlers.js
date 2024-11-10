// src/ipc/userIpcHandlers.js
const { ipcMain } = require('electron');

class UserIPCHandlers {
    constructor(userDataService, windowManager) {
        this.userDataService = userDataService;
        this.windowManager = windowManager;
        this.registerHandlers();
    }

    registerHandlers() {
        console.log("register Handlers");
        ipcMain.handle('get-current-user', async () => {
            return this.userDataService.getCurrentUser();
        });

        ipcMain.handle('login-user', async (event, { username, password, role}) => {
            const user = this.userDataService.loginUser(username, password, role);
            if (user) {
                user[password] = "114514";
                this.windowManager.handleLoginSuccess(
                    this.windowManager.mainWindow,
                    user
                );
            }
            return user;
        });

        ipcMain.handle('register-user', async (event, userData) => {
            return this.userDataService.saveUser(userData);
        });

        ipcMain.handle('logout-user', async () => {
            const success = this.userDataService.logoutUser();
            if (success) {
                this.windowManager.loadPage(
                    this.windowManager.mainWindow,
                    'login.html'
                );
            }
            return success;
        });

        ipcMain.handle('update-user', async (event, { username, updateData }) => {
            return this.userDataService.updateUserInfo(username, updateData);
        });
    }
}

module.exports = UserIPCHandlers;