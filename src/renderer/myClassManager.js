// const path = require('path');
const UserManager = require('./userManager');
const UserHttpHandler = require('../http/userHttpHandler');

class MyTeamManager extends BaseManager {

    static async getScrollItem(item) {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item');

        const title = item['name'];
        const description = item['join_key'];
        const classId = item['id'];
        scrollItem.setAttribute('data-class-id', classId);

        scrollItem.innerHTML = `
            <h3 class=competition-item-title> ${title} </h3>
            <p class="competition-item-description">
                邀请码：${description}
            </p>
        `;

        const deleteButton = document.createElement('div');
        deleteButton.classList.add('bottom-right-transform');
        deleteButton.classList.add('reject-button');
        deleteButton.innerText = '删除';
        deleteButton.addEventListener('click', async (e) => {
            e.preventDefault();
            const user = await UserManager.getCurrentUser();
            const classId = e.target.parentElement.getAttribute('data-class-id');
            const response = await UserHttpHandler.sentPostRequest('delete_class_with_groups', {user_id: user['user_id'], class_id: classId});
            if (response['success']) {
                await MyTeamManager.update();
                alert(response['message']);
            }
        });
        scrollItem.appendChild(deleteButton);

        return scrollItem;
    }

    static async update() {
        this.container.replaceChildren();
        const user = await UserManager.getCurrentUser();
        const response = await UserHttpHandler.sentPostRequest('get_user_classes', {user_id: user['user_id']});
        const classes = response['classes'];
        for (let i = 0; i < classes.length; i++) {
            const scrollItem = await this.getScrollItem(classes[i]);
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