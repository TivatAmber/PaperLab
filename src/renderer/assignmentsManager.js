// const path = require('path');
const UserManager = require('./userManager');
const UserHttpHandler = require('../http/userHttpHandler');

class AssignmentManager extends BaseManager {
    static async getScrollItem(item) {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item');

        const title = item['name'];
        const description = item['description'];
        const teamId = item['id'];

        scrollItem.innerHTML = `
            <h3 class=competition-item-title> ${title} </h3>
            <p class="competition-item-description">
                ${description}
            </p>
            <div class="bottom-right-transform" data-team-id=${teamId}> details </div>
        `;

        return scrollItem;
    }

    static async update() {
        this.container.replaceChildren();
        const user = await UserManager.getCurrentUser();
        const response = await UserHttpHandler.sentPostRequest('get_user_classes', {user_id: user['user_id']});
        const classes = response['classes'];
        for (let i = 0; i < classes.length; i++) {
            const groupResponse = await UserHttpHandler.sentPostRequest('get_all_groups', {class: classes[i]['id']});
            const groups = groupResponse['groups'];
            for (let i = 0; i < groups.length; i++) {
                const scrollItem = await this.getScrollItem(groups[i]);
                this.container.appendChild(scrollItem);
            }
        }
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AssignmentManager;
} else {
    window.AssignmentManager = AssignmentManager;
}