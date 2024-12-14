class BaseManager {
    static async update(){}
    static async getScrollItem(){}
    static init(containerId) {
        this.container = document.getElementById(containerId);
        this.counter = 0;
    }
}