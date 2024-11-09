const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        maximizable: true,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });
    mainWindow.center();
    mainWindow.loadFile(path.join(__dirname, 'assets/html/index.html'));
}

function createFloatingWindows(fileName) {
    // Create a window that's frameless and always on top
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        parent: mainWindow,
        modal: false
    })

    // Load your HTML file
    win.loadFile(path.join(__dirname, 'assets/html/' + fileName))

    // Make window draggable (from our custom title bar)
    win.setMovable(true)

    return win
}

ipcMain.on('open-register', () => {
    mainWindow.loadFile(path.join(__dirname, 'assets/html/register.html'));
});

ipcMain.on('open-login', () => {
    // TODO reset login info
    mainWindow.setSize(800, 600);
    mainWindow.center();
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

ipcMain.on('login-success', (event, userInfo) => {
    const username = userInfo.username
    const role = userInfo.role
    if (role === 'student') {
        mainWindow.loadFile(path.join(__dirname, 'assets/html/student.html'));
    } else if (role === 'teacher') {
        mainWindow.loadFile(path.join(__dirname, 'assets/html/teacher.html'));
    }
    mainWindow.setResizable(true);
    mainWindow.maximize();
    mainWindow.setResizable(false);
});

ipcMain.on('open-team', (event, data= {}) => {
    const {teamId = null} = data;
    if (!teamId) {
        console.error("No TeamId received");
        return;
    }
    console.log("TeamId: ", teamId);
    mainWindow.loadFile(path.join(__dirname, 'assets/html/team.html'));
})

ipcMain.on('open-team-create', () => {
    createFloatingWindows('createTeam.html')
})

ipcMain.on('create-team', (event, {teamName, teamDescription, teamClass}) => {
    console.log(teamName + "\n", teamDescription + "\n" + teamClass);
    event.reply('team-created', {state: 'success'})
})

ipcMain.on('close-window', (event) => {
    // Get the window that sent the message
    const win = BrowserWindow.fromWebContents(event.sender)
    if (win && win.closable) {
        win.close()
    }
    console.log("close window");
})

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
