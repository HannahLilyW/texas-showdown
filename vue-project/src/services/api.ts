import router from '../router';
import { ref } from 'vue';
import type { Ref } from 'vue';
import { io, Socket } from "socket.io-client";
import type { Game } from '../models';


function setCookie(key: string, value: string) {
    const expiryDate = new Date();
    expiryDate.setDate(new Date().getDate() + 60);
    document.cookie = `${key}=${value}; expires=${expiryDate.toUTCString()}; path=/; SameSite=Lax; Secure`;
}

function deleteCookie(key: string) {
    const expiryDate = new Date();
    expiryDate.setDate(new Date().getDate() - 60);
    document.cookie = `${key}=; expires=${expiryDate.toUTCString()}; path=/`;
}

function getCookie(key: string) {
    const name = key + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for (let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

const baseUrl: string = "/texas_api/";

let socket: Socket | null = null;

let token: string = getCookie("token") || "";
let tokenCreated: Date | null = getCookie("tokenCreated") ? new Date(getCookie("tokenCreated") || "") : null;

export const username: Ref<string> = ref(getCookie("username") || "");
export const name: Ref<string> = ref('');
export const is_guest: Ref<boolean> = ref(false);
export const background_color: Ref<string> = ref('blank');
export const shirt_color: Ref<string> = ref('black');
export const skin_color: Ref<string> = ref('black');
export const hat_color: Ref<string> = ref('black');

export const existingGames: Ref<Game[] | null> = ref(null);
export const currentGame: Ref<Game | null> = ref(null);
export const hand: Ref<number[] | null> = ref(null);

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
    if (!token.length || !username.value.length || !tokenCreated) {
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
        deleteCookie("username");
        deleteCookie("token");
        deleteCookie("tokenCreated");
        token = "";
        tokenCreated = null;
        username.value = "";
        router.push('/login');
    }
    return response;
}

export async function get(url: string) {
    if (!token.length || !username.value.length || !tokenCreated) {
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
        deleteCookie("username");
        deleteCookie("token");
        deleteCookie("tokenCreated");
        token = "";
        tokenCreated = null;
        username.value = "";
        router.push('/login');
    }
    return response;
}

export function updateToken(newToken: string) {
    setCookie("token", newToken);
    const now = Date.now();
    tokenCreated = new Date(now);
    setCookie("tokenCreated", now.toString());
    token = newToken;
}

export function updateUsername(newUsername: string) {
    setCookie("username", newUsername);
    username.value = newUsername;
}

export function updateOwnProfileInfo() {
    get(`players/${username.value}/profile_info/`).then(response => {
        try {
            response.json().then(responseJson => {
                name.value = responseJson['name'];
                is_guest.value = responseJson['is_guest'];
                background_color.value = responseJson['background_color'];
                shirt_color.value = responseJson['shirt_color'];
                skin_color.value = responseJson['skin_color'];
                hat_color.value = responseJson['hat_color'];
            })
        } catch (e) {
            console.log(`Error getting profile info: ${e}`)
        }
    })
}

export function logout() {
    post('logout/', {}).then(() => {
        deleteCookie("username");
        deleteCookie("token");
        deleteCookie("tokenCreated");
        token = "";
        tokenCreated = null;
        username.value = "";
        name.value = "";
        is_guest.value = false;
        background_color.value = 'blank';
        shirt_color.value = 'black';
        skin_color.value = 'black';
        hat_color.value = 'black';
        router.push('/');
    })
}

export function startSocket() {
    if (socket) {
        socket.close();
    }

    socket = io({
        auth: {
            token: token
        }
    });

    socket.onAny((eventName, ...args) => {
        if (eventName == 'update_game') {
            currentGame.value = args[0];
        }

        if (eventName == 'update_existing_games') {
            existingGames.value = args[0];
        }
    });
}

export function stopSocket() {
    if (socket) {
        socket.close();
    }
}

function getCurrentGame() {
    get('games/get_current_game/').then(response => {
        if (response.status == 204) {
            currentGame.value = null;
        }
        try {
            response.json().then(responseJson => {
                if (response.status == 200) {
                    currentGame.value = responseJson;
                } else {
                    console.log(`unexpected response. status: ${response.status} response: ${responseJson}`)
                }
            })
        } catch (e) {
            console.log(`error getting current game: ${e}`)
        }
    })
}

getCurrentGame();