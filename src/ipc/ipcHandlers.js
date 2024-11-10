// src/ipc/ipcHandlers.js
const { ipcMain, BrowserWindow } = require('electron');

class IPCHandlers {
    constructor(windowManager) {
        this.windowManager = windowManager;
        this.registerHandlers();
    }

    registerHandlers() {
        // Navigation handlers
        const pages = [
            'register', 'assignments', 'competition',
            'settings', 'student', 'teacher'
        ];

        pages.forEach(page => {
            ipcMain.on(`open-${page}`, () => {
                this.windowManager.loadPage(
                    this.windowManager.mainWindow,
                    `${page}.html`
                );
            });
        });

        ipcMain.on('open-login', () => {
            this.windowManager.loadPage(
                this.windowManager.mainWindow,
                'login.html'
            );
            this.windowManager.mainWindow.setSize(800, 600);
            this.windowManager.mainWindow.center();
        })

        // Login handler
        ipcMain.on('login-success', (event, userInfo) => {
            this.windowManager.handleLoginSuccess(
                this.windowManager.mainWindow,
                userInfo
            );
        });

        // Team handlers
        ipcMain.on('open-team', (event, data = {}) => {
            const { teamId = null } = data;
            if (!teamId) {
                console.error("No TeamId received");
                return;
            }
            console.log("TeamId: ", teamId);
            this.windowManager.loadPage(
                this.windowManager.mainWindow,
                'team.html'
            );
        });

        ipcMain.on('open-team-create', () => {
            if (this.windowManager.floatingWindow != null) return;
            this.windowManager.createFloatingWindow(
                'createTeam.html',
                this.windowManager.mainWindow
            );
        });

        ipcMain.on('open-class-create', () => {
            if (this.windowManager.floatingWindow != null) return;
            this.windowManager.createFloatingWindow(
                'createClass.html',
                this.windowManager.mainWindow
            );
        })

        ipcMain.on('create-team', (event, teamData) => {
            console.log(
                teamData.teamName + "\n",
                teamData.teamDescription + "\n" +
                teamData.teamClass
            );
            // TODO
            event.reply('team-created', { state: 'success' });
        });

        ipcMain.on('create-class', (event, classData) => {
            console.log(
                classData.className + "\n",
                classData.classDescription + "\n" +
                classData.classTeacher
            );
            // TODO
            event.reply('class-created', { state: 'success' });
        });

        ipcMain.on('close-window', (event) => {
            const win = BrowserWindow.fromWebContents(event.sender);
            if (win === this.windowManager.floatingWindow) {
                this.windowManager.floatingWindow = null;
            }
            if (win && win.closable) {
                win.close();
            }
            console.log("close window");
        });
    }
}

module.exports = IPCHandlers;