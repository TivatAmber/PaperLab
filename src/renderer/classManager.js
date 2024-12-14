const UserHttpHandler = require('../http/userHttpHandler');
const UserManager = require('./userManager');

class ClassManager extends BaseManager{

    static async getScrollItem(item) {
        const scrollItem = document.createElement('option');
        scrollItem.value = item['id']
        scrollItem.innerHTML = item['name'];
        return scrollItem;
    }

    static async update() {
        const user = await UserManager.getCurrentUser();
        console.log(user);
        const response = await UserHttpHandler.sentPostRequest('get_user_classes', {user_id: user['user_id']});
        const items = response['classes'];
        for (let i = 0; i < items.length; i++) {
            const scrollItem = await this.getScrollItem(items[i]);
            this.container.appendChild(scrollItem);
        }
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ClassManager;
} else {
    window.AssignmentManager = ClassManager;
}