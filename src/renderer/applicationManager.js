const UserManager = require('./userManager');
const UserHttpHandler = require('../http/userHttpHandler');
const TeammateManager = require('./teammateManager');

class ApplicationManager {
    static init(containerId) {
        this.container = document.getElementById(containerId);
        this.leaderId = null;
        this.teamId = null;
        this.counter = 0;
    }

    static async getScrollItem(item) {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item-application');
        const title = item['student_name'];
        const description = item['description'];
        const userId = item['student_id'];
        scrollItem.setAttribute('data-user-id', userId);

        scrollItem.innerHTML = `
            <h4 class="teammate-item-title"> ${title} </h4>
            <p class="teammate-item-description">
                ${description}
            </p>
        `;

        const userData = await UserManager.getCurrentUser();
        const role = userData['role'];
        if (role === 'teacher' || userData['user_id'] === this.leaderId) {
            const accept = document.createElement('div');
            accept.classList.add('bottom-left-transform');
            accept.classList.add('accept-button');
            accept.addEventListener('click', async (e) => {
                e.preventDefault();
                const userData = await UserManager.getCurrentUser();
                const userId = e.target.parentElement.getAttribute('data-user-id');
                const response = await UserHttpHandler.sentPostRequest('leader_approve_application', {leader_id: userData['user_id'],group_id: this.teamId, student_id: userId});
                if (response['success']) {
                    await ApplicationManager.update(this.teamId);
                    await TeammateManager.update(this.teamId);
                    alert('已接受');
                }
            });
            accept.innerText = '接受';
            scrollItem.appendChild(accept);

            const reject = document.createElement('div');
            reject.classList.add('bottom-right-transform');
            reject.classList.add('reject-button');
            reject.addEventListener('click', async (e) => {
                e.preventDefault();
                const userData = await UserManager.getCurrentUser();
                const userId = e.target.parentElement.getAttribute('data-user-id');
                const response = await UserHttpHandler.sentPostRequest('leader_refuse_application', {leader_id: userData['user_id'], group_id: this.teamId, student_id: userId});
                if (response['success']) {
                    await ApplicationManager.update(this.teamId);
                    alert('已拒绝');
                }
            });
            reject.innerText = '拒绝';
            scrollItem.appendChild(reject);
        }

        this.counter++;
        return scrollItem;
    }

    static async update(teamId) {
        // TODO Fetch Data From Remote
        this.container.replaceChildren();
        const response = await UserHttpHandler.sentPostRequest('get_group_applications', {group_id: teamId});
        const leaderResponse = await UserHttpHandler.sentPostRequest('get_group_leader', {group_id: teamId});
        this.leaderId = leaderResponse['leader']['id'];
        this.teamId = teamId;
        const applications = response['applications'];
        for (let i = 0; i < applications.length; i++) {
            const scrollItem = await this.getScrollItem(applications[i]);
            this.container.appendChild(scrollItem);
        }
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ApplicationManager;
} else {
    window.AssignmentManager = ApplicationManager;
}