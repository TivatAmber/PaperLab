const { ipcRenderer, contextBridge } = require('electron');

// 暴露 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
    openPage: (page) => ipcRenderer.send(page)
});
