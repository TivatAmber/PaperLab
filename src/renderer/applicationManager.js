class ApplicationManager {
    static init(containerId) {
        this.container = document.getElementById(containerId);
        this.counter = 0;
    }

    static async getScrollItem() {
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item-application');
        // TODO Get Info From remote
        const title = "Title";
        const description = "Description";
        const userId = this.counter;
        scrollItem.setAttribute('data-user-id', userId);

        scrollItem.innerHTML = `
            <h4 class="teammate-item-title"> ${title} </h4>
            <p class="teammate-item-description">
                ${description}
            </p>
        `;

        const userData = await UserManager.getCurrentUser();
        const role = userData['role'];
        if (role === 'teacher') { // TODO 是队长
            scrollItem.innerHTML += `
                <div class="bottom-left-transform accept-button"> 接受 </div>
                <div class="bottom-right-transform reject-button">拒绝 </div>
            `;
        }

        this.counter++;
        return scrollItem;
    }

    static async update() {
        // TODO Fetch Data From Remote
        for (let i = 0; i < 5; i++) {
            const scrollItem = await this.getScrollItem();
            this.container.appendChild(scrollItem);
        }
    }
}