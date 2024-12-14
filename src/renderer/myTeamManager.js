// const path = require('path');
const UserManager = require('./userManager');
const UserHttpHandler = require('../http/userHttpHandler');

class MyTeamManager extends BaseManager {
    static async getScrollItem(item) {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item');

        const title = item['group_name'];
        const classTitle = item['class_name'];
        const description = item['description'];
        const teamId = item['group_id'];

        scrollItem.innerHTML = `
            <h3 class=competition-item-title> ${title} </h3>
            <h4 class="class-title"> ${classTitle}</h4>
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
        const response = await UserHttpHandler.sentPostRequest('get_user_groups', {user_id: user['user_id']});
        const groups = response['groups'];
        for (let i = 0; i < groups.length; i++) {
            const scrollItem = await this.getScrollItem(groups[i]);
            this.container.appendChild(scrollItem);
        }
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MyTeamManager;
} else {
    window.AssignmentManager = MyTeamManager;
}