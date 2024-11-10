const { ipcMain } = require('electron');

class SearchHandler {
    constructor(windowManager, userDataService, searchService) {
        this.windowManager = windowManager;
        this.userDataService = userDataService;
        this.searchService = searchService;
        this.registerHandlers();
    }
    registerHandlers() {
        ipcMain.handle('search', async (event, input) => {

        });
    }
}

module.exports = SearchHandler;