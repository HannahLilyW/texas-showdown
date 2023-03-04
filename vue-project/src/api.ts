import router from './router'

const baseUrl: string = "/texas_api/";

let token: string = "";
let uname: string = "";

async function postWithoutAuth(url: string, data: Record<string, any>) {
    const response = await fetch(`${baseUrl}${url}`, {
        method: "POST",
        mode: "same-origin", // If a request is made to another origin with this mode set, the result is an error. Used to ensure that a request is always being made to your origin. See https://developer.mozilla.org/en-US/docs/Web/API/Request/mode
        cache: "no-store", // The browser fetches the resource from the remote server without first looking in the cache, and will not update the cache with the downloaded resource. See https://developer.mozilla.org/en-US/docs/Web/API/Request/cache
        credentials: "same-origin", // Send user credentials (cookies, basic http auth, etc..) if the URL is on the same origin as the calling script. This is the default value. See https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials
        headers: {
            "Content-Type": "application/json"
        },
        referrerPolicy: "no-referrer", // The Referer header will be omitted: sent requests do not include any referrer information. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
        body: JSON.stringify(data),
    });
    return response;
}

export async function post(url: string, data: Record<string, any>) {
    if (!token.length) {
        router.push('/login');
        return {"error": "Login required"};
    }
    const response = await fetch(`${baseUrl}${url}`, {
        method: "POST",
        mode: "same-origin", // If a request is made to another origin with this mode set, the result is an error. Used to ensure that a request is always being made to your origin. See https://developer.mozilla.org/en-US/docs/Web/API/Request/mode
        cache: "no-store", // The browser fetches the resource from the remote server without first looking in the cache, and will not update the cache with the downloaded resource. See https://developer.mozilla.org/en-US/docs/Web/API/Request/cache
        credentials: "same-origin", // Send user credentials (cookies, basic http auth, etc..) if the URL is on the same origin as the calling script. This is the default value. See https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Token ${token}`
        },
        referrerPolicy: "no-referrer", // The Referer header will be omitted: sent requests do not include any referrer information. See https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy
        body: JSON.stringify(data),
    });
    return response;
}

export async function postCreateAccount(username: string, password: string) {
    const response = await postWithoutAuth('/create_account', {'username': username, 'password': password});
    if (response.status != 200) {
        return {"status": "error", "error": "Unable to create account"};
    }
    try {
        response.json().then(responseJson => {
            if (responseJson['token'] && responseJson['username']) {
                token = responseJson['token'];
                uname = responseJson['username'];
            } else {
                return {"status": "error", "error": "Unable to create account"};
            }
            return {"status": "success", "username": uname};
        });
    } catch (e) {
        return {"status": "error", "error": "Unable to create account"};
    }
}

export async function postLogin(username: string, password: string) {
    const response = await postWithoutAuth('/login', {'username': username, 'password': password});
    if (response.status != 200) {
        return {"status": "error", "error": "Unable to login"};
    }
    try {
        response.json().then(responseJson => {
            if (responseJson['token'] && responseJson['username']) {
                token = responseJson['token'];
                uname = responseJson['username'];
            } else {
                return {"status": "error", "error": "Unable to login"};
            }
            return {"status": "success", "username": uname};
        });
    } catch (e) {
        return {"status": "error", "error": "Unable to login"};
    }
}
