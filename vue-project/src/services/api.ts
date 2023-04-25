import router from '../router';
import { ref } from 'vue';
import type { Ref } from 'vue';
import { io, Socket } from "socket.io-client";
import type { Game } from '../models';

const isDevelopment = false;

const baseUrl: string = "/texas_api/";

let socket: Socket|null = null;

let token: string = sessionStorage.getItem("token") || "";
let tokenCreated: Date|null = sessionStorage.getItem("tokenCreated") ? new Date(sessionStorage.getItem("tokenCreated") || "") : null;

export let username: Ref<string> = ref(sessionStorage.getItem("username") || "");

export let currentGame: Ref<Game|null> = ref(null);
export let hand: Ref<number[]|null> = ref(null);

export async function postWithoutAuth(url: string, data: Record<string, any>) {
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
    // Prompt for login 1 hour before the token actually expires to prevent any weirdness
    if (!token.length || !username.value.length || !tokenCreated || tokenCreated.setHours(tokenCreated.getHours() + 11) < Date.now()) {
        router.push('/login');
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
    if (response.status == 401) {
        // Authentication failure. Prompt for login again.
        sessionStorage.removeItem("username");
        sessionStorage.removeItem("token");
        sessionStorage.removeItem("tokenCreated");
        token = "";
        tokenCreated = null;
        username.value = "";
        router.push('/login');
    }
    return response;
}

export async function get(url: string) {
    // Prompt for login 1 hour before the token actually expires to prevent any weirdness
    if (!token.length || !username.value.length || !tokenCreated || tokenCreated.setHours(tokenCreated.getHours() + 11) < Date.now()) {
        router.push('/login');
    }
    const response = await fetch(`${baseUrl}${url}`, {
        method: "GET",
        mode: "same-origin",
        cache: "no-store",
        credentials: "same-origin",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Token ${token}`
        },
        referrerPolicy: "no-referrer"
    });
    if (response.status == 401) {
        // Authentication failure. Prompt for login again.
        sessionStorage.removeItem("username");
        sessionStorage.removeItem("token");
        sessionStorage.removeItem("tokenCreated");
        token = "";
        tokenCreated = null;
        username.value = "";
        router.push('/login');
    }
    return response;
}

export function updateToken(newToken: string) {
    sessionStorage.setItem("token", newToken);
    const now = Date.now();
    tokenCreated = new Date(now);
    sessionStorage.setItem("tokenCreated", now.toString());
    token = newToken;
}

export function updateUsername(newUsername: string) {
    sessionStorage.setItem("username", newUsername);
    username.value = newUsername;
}

export function logout() {
    post('logout/', {}).then(response => {
        sessionStorage.removeItem("username");
        sessionStorage.removeItem("token");
        sessionStorage.removeItem("tokenCreated");
        token = "";
        tokenCreated = null;
        username.value = "";
        router.push('/');
    })
}

export function startSocket() {
    if (socket) {
        socket.close();
    }

    if (!isDevelopment) {
        socket = io({
            auth: {
                token: token
            }
        });

        console.log(socket.io)

        socket.onAny((eventName, ...args) => {
            console.log(args[0]);
            currentGame.value = args[0];
        });
    }
}

export function stopSocket() {
    if (socket) {
        socket.close();
    }
}
