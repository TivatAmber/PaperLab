const url = 'http://127.0.0.1:14456';

class UserHttpHandler {
    static async sentGetRequest(type, args, content = "") {
        args['type'] = type
        console.log(args)
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                ...args,
                'Content-Type': 'application/json;charset=utf-8',
                'Content-Length': content.length
            },
            body: content
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    }
    static async sentPostRequest(type, args) {
        args['type'] = type
        const body = JSON.stringify(args);
        console.log(args)
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8',
                'Content-Length': body.length
            },
            body: body
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log(data)
        return data;
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserHttpHandler;
} else {
    window.UserHttpHandler = UserHttpHandler;
}