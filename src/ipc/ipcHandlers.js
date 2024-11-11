// src/ipc/ipcHandlers.js
const { ipcMain, BrowserWindow } = require('electron');
const UserManager = require('../renderer/userManager');
const UserHttpHandler = require('../http/userHttpHandler');

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

        ipcMain.on('open-class-join', () => {
            if (this.windowManager.floatingWindow != null) return;
            this.windowManager.createFloatingWindow(
                'joinClass.html',
                this.windowManager.mainWindow,
                300,
                250
            )
        })

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