const { app, ipcMain} = require('electron');
const WindowManager = require('./src/window/windowManager');
const IPCHandlers = require('./src/ipc/ipcHandlers');
const UserIPCHandlers = require('./src/ipc/userIpcHandlers');
const UserDataService = require('./src/services/userDataService');

class Application {
    constructor() {
        this.windowManager = new WindowManager();
        this.userDataService = new UserDataService();
        this.ipcHandlers = null;
        this.userIpcHandlers = null;
    }

    init() {
        app.whenReady().then(() => {
            this.windowManager.createMainWindow();
            this.ipcHandlers = new IPCHandlers(this.windowManager);
            this.userIpcHandlers = new UserIPCHandlers(
                this.userDataService,
                this.windowManager
            );
            this.windowManager.mainWindow.center();
        });

        app.on('window-all-closed', () => {
            if (process.platform !== 'darwin') {
                app.quit();
            }
        });
    }
}

const electronApp = new Application();
electronApp.init();