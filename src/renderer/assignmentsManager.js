// const path = require('path');
const UserManager = require('./userManager');
const UserHttpHandler = require('../http/userHttpHandler');

class AssignmentManager {
    static init(containerId) {
        this.container = document.getElementById(containerId);
        this.counter = 0;
    }

    static async getScrollItem() {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item');
        // TODO Get Info From remote

        const title = "Title";
        const description = "Description";
        const teamId = this.counter;

        scrollItem.innerHTML = `
            <h3 class=competition-item-title> ${title} </h3>
            <p class="competition-item-description">
                ${description}
            </p>
            <div class="bottom-right-transform" data-team-id=${teamId}> details </div>
        `;

        this.counter++;
        return scrollItem;
    }

    static async update() {
        const user = await UserManager.getCurrentUser();
        const response = await UserHttpHandler.sentPostRequest('get_user_classes', {user_id: user['user_id']});
        console.log(response)
        // TODO Fetch Data From Remote
        for (let i = 0; i < 10; i++) {
            const scrollItem = await this.getScrollItem();
            this.container.appendChild(scrollItem);
        }
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AssignmentManager;
} else {
    window.AssignmentManager = AssignmentManager;
}