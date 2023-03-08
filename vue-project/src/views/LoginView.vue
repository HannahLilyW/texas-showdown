<script setup lang="ts">
import { ref } from 'vue';
import type { Ref } from 'vue';
import { postWithoutAuth, updateToken, updateUsername } from '../api.js';
import router from '../router';

// Form data
let username: Ref<string> = ref("");
let password: Ref<string> = ref("");

let error: Ref<boolean|string> = ref(false);

function login(event: Event) {
    error.value = false;

    // Needed because by default, pressing a button in a form will reload the page. We don't want that.
    event.preventDefault();

    // Send the data
    postWithoutAuth('login/', {'username': username.value, 'password': password.value}).then(response => {
        try {
            response.json().then(responseJson => {
                if (response.status != 200) {
                    error.value = 'Error logging in';
                    return;
                }
                if (responseJson['token'] && responseJson['username']) {
                    updateToken(responseJson['token']);
                    updateUsername(responseJson['username']);
                    router.push('/');
                } else {
                    error.value = 'Error logging in';
                }
            })
        } catch (e) {
            error.value = 'Error logging in';
        }
    })
};

function cancel() {
    router.push('/');
}
</script>

<template>
    <header>
        Log In
    </header>

    <form>
        <label for="username">Username:</label>
        <input id="username" v-model="username" maxlength="150">
        <label for="password">Password:</label>
        <input id="password" type="password" v-model="password" maxlength="150">
    </form>
    <div class="error" v-if="error">{{ error }}</div>
    <div class="buttons-row">
        <button class="button" @click="login($event)">
            Log In
        </button>
        <button class="button" @click="cancel()">
            Cancel
        </button>
    </div>
</template>

<style scoped>
label {
    padding: 4px;
    margin: 4px;
    white-space: nowrap;
}
form {
    display: grid;
    grid-template-columns: min-content max-content;
}

input {
    width: 100%;
    padding: 4px;
    margin: 4px;
}
</style>