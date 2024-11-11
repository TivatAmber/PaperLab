const UserHttpHandler = require("../http/userHttpHandler");
const UserManager = require("./userManager");

class TeammateManager {
    static init(containerId) {
        this.container = document.getElementById(containerId);
        this.leaderId = null;
        this.teamId = null;
        this.counter = 0;
    }
    static async getScrollItem(item) {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item-teammate');
        const title = item['name'];
        const description = item['description'];
        const userId = item['id'];
        scrollItem.setAttribute('data-user-id', userId);

        scrollItem.innerHTML = `
            <h4 class="teammate-item-title"> ${title} </h4>
            <p class="teammate-item-description">
                ${description}
            </p>
        `;

        const userData = await UserManager.getCurrentUser();
        const role = userData['role'];
        if (role === 'teacher' || (userData['user_id'] === this.leaderId && userId !== this.leaderId)) {
            const kick = document.createElement('div');
            kick.classList.add('bottom-right-transform');
            kick.classList.add('reject-button');
            kick.addEventListener('click', async (e) => {
                e.preventDefault();
                const userData = await UserManager.getCurrentUser();
                const userId = e.target.parentElement.getAttribute('data-user-id');
                const response = await UserHttpHandler.sentPostRequest('student_quit_group', {leader_id: userData['user_id'], group_id: this.teamId, student_id: userId});
                if (response['success']) {
                    await TeammateManager.update(this.teamId);
                    alert('已踢出');
                }
            });
            kick.innerText = '踢出';
            scrollItem.appendChild(kick);
        }

        this.counter++;
        return scrollItem;
    }

    static async update(teamId) {
        this.container.replaceChildren();
        const response = await UserHttpHandler.sentPostRequest('get_group_members_simple', {group_id: teamId});
        const leaderResponse = await UserHttpHandler.sentPostRequest('get_group_leader', {group_id: teamId});
        this.leaderId = leaderResponse['leader']['id'];
        this.teamId = teamId;
        const members = response['members'];
        for (let i = 0; i < members.length; i++) {
            const scrollItem = await this.getScrollItem(members[i]);
            this.container.appendChild(scrollItem);
        }
    }
}

// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TeammateManager;
} else {
    window.UserManager = TeammateManager;
}