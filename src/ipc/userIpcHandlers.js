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

        ipcMain.handle('get-current-team', async () => {
            return this.userDataService.getCurrentTeam();
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

        ipcMain.handle('create-team', async (event, {class_id, team_name, description}) => {
            const user = this.userDataService.getCurrentUser();
            console.log(
                class_id + "\n",
                team_name + "\n",
                description + "\n"
            );
            return await UserHttpHandler.sentPostRequest('student_create_team', {
                student_id: user['user_id'],
                class_id: class_id,
                team_name: team_name,
                description: description
            });
        });

        // Team handlers
        ipcMain.on('open-team', (event, data = {}) => {
            const { teamId = null } = data;
            if (!teamId) {
                console.error("No TeamId received");
                return;
            }
            console.log("TeamId: ", teamId);
            this.userDataService.currentTeam = teamId;
            this.windowManager.loadPage(
                this.windowManager.mainWindow,
                'team.html'
            );
        });

        ipcMain.handle('apply-to-team', async (event, {group_id}) => {
            const user = this.userDataService.getCurrentUser();
            console.log(
                user['user_id'] + " apply for team " + group_id,
            );
            return await UserHttpHandler.sentPostRequest('student_apply_to_group', {
                student_id: user['user_id'],
                group_id: group_id
            });
        })

        ipcMain.handle('leave-team', async (event, {group_id}) => {
            const user = this.userDataService.getCurrentUser();
            console.log(
                user['user_id'] + " leave group " + group_id,
            );
            return await UserHttpHandler.sentPostRequest('student_quit_group', {
                student_id: user['user_id'],
                group_id: group_id
            });
        })

        ipcMain.handle('remove-team', async (event, {group_id}) => {
            const user = this.userDataService.getCurrentUser();
            console.log(
                user['user_id'] + " remove group " + group_id,
            );
            return await UserHttpHandler.sentPostRequest('teacher_remove_group', {
                teacher_id: user['user_id'],
                group_id: group_id
            });
        })
    }
}

module.exports = UserIPCHandlers;