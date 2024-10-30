const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile(path.join(__dirname, 'assets/html/index.html'));
}

ipcMain.on('open-register', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/register.html'));
});

ipcMain.on('open-login', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/index.html'));
});

ipcMain.on('open-assignments', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/assignments.html'));
});

ipcMain.on('open-competition', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/competition.html'));
});

ipcMain.on('open-settings', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/settings.html'));
});

ipcMain.on('open-student', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/student.html'));
});

ipcMain.on('open-teacher', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/teacher.html'));
});

ipcMain.on('login-success', (event, role) => {
    if (role === 'student') {
        mainWindow.loadFile(path.join(__dirname, 'assets/html/student.html'));
    } else if (role === 'teacher') {
        mainWindow.loadFile(path.join(__dirname, 'assets/html/teacher.html'));
    }
});

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
