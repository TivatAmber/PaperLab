class SearchManager extends BaseManager {
    static getScrollItem() {
        this.container.replaceChildren();
        const scrollItem = document.createElement('div');
        scrollItem.classList.add('scroll-item');
        const title = "Title";
        const description = "Description";
        const teamId = this.counter;

        scrollItem.innerHTML = `
            <h3 class="competition-item-title"> ${title} </h3>
            <p class="competition-item-description">
                ${description}
            </p>
            <div class="bottom-right-transform" data-team-id=${teamId}> details </div>
        `;

        this.counter++;
        return scrollItem;
    }

    static update() {
        // TODO Fetch Data From Remote
        for (let i = 0; i < 10; i++) {
            const scrollItem = this.getScrollItem();
            this.container.appendChild(scrollItem);
        }
    }
}
// Export for browser environment
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SearchManager;
} else {
    window.SearchManager = SearchManager;
}