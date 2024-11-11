// src/ipc/userIpcHandlers.js
const { ipcMain } = require('electron');
const UserHttpHandler = require("../http/userHttpHandler");

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

        ipcMain.handle('join-team', async() => {
            return this.userDataService.joinTeam();
        })

        ipcMain.handle('login-user', async (event, { username, password, role}) => {
            const user = await this.userDataService.loginUser(username, password, role);
            if (user) {
                user["password"] = "114514";
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

        ipcMain.handle('create-class', async (event, classData) => {
            const user = this.userDataService.getCurrentUser();
            console.log(
                classData.className + "\n",
                classData.classDescription + "\n"
            );
            return await UserHttpHandler.sentPostRequest('teacher_create_class', {
                teacher: user['user_id'],
                class: classData.className
            });
        });

        ipcMain.handle('join-class', async (event, {classCode}) => {
              const user = this.userDataService.getCurrentUser();
              console.log(
                  user['user_id'] + "join class",
              );
              return await UserHttpHandler.sentPostRequest('student_join_class_by_key', {
                  student_id: user['user_id'],
                  join_key: classCode
              });
        })
    }
}

module.exports = UserIPCHandlers;