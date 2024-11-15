const { BrowserWindow } = require('electron');
const path = require('path');

class WindowManager {
    constructor() {
        this.mainWindow = null;
        this.floatingWindow = null;
    }

    createMainWindow() {
        this.mainWindow = new BrowserWindow({
            width: 800,
            height: 600,
            maximizable: true,
            resizable: false,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
                preload: path.join(__dirname, '../../preload.js')
            }
        });
        this.mainWindow.center();
        this.mainWindow.loadFile(path.join(__dirname, '../../assets/html/login.html'));
        return this.mainWindow;
    }

    createFloatingWindow(fileName, parentWindow, width = 800, height = 600) {
        this.floatingWindow = new BrowserWindow({
            width: width,
            height: height,
            resizable: false,
            frame: false,
            webPreferences: {
                nodeIntegration: true,
                contextIsolation: false,
            },
            parent: parentWindow,
        });

        this.floatingWindow.loadFile(path.join(__dirname, '../../assets/html/' + fileName));
        return this.floatingWindow;
    }

    loadPage(window, pageName) {
        window.loadFile(path.join(__dirname, '../../assets/html/' + pageName));
    }

    handleLoginSuccess(window, userInfo) {
        const { role } = userInfo;
        const page = role === 'student' ? 'student.html' : 'teacher.html';
        this.loadPage(window, page);
        window.setResizable(true);
        window.maximize();
        window.setResizable(false);
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WindowManager;
} else {
    window.AssignmentManager = WindowManager;
}