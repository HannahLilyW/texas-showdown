<script setup lang="ts">
import { ref } from 'vue';
import type { Ref } from 'vue';
import { postWithoutAuth, updateToken, updateUsername, updateOwnProfileInfo } from '../services/api.js';
import router from '../router';

// Form data
let username: Ref<string> = ref("");
let password: Ref<string> = ref("");

let error: Ref<boolean|string> = ref(false);

function login() {
    error.value = false;

    // Send the data
    postWithoutAuth('login/', {'username': username.value, 'password': password.value}).then(response => {
        try {
            response.json().then(responseJson => {
                if (response.status != 200) {
                    error.value = 'Wrong username or password';
                    return;
                }
                if (responseJson['token'] && responseJson['username']) {
                    updateToken(responseJson['token']);
                    updateUsername(responseJson['username']);
                    updateOwnProfileInfo();
                    router.push('/');
                } else {
                    error.value = 'Error logging in';
                }
            })
        } catch (e) {
            error.value = 'Error logging in';
        }
    })
}

const passwordElement: Ref<HTMLInputElement|null> = ref(null);

const focusPasswordElement = () => {
  if (passwordElement.value) {
    passwordElement.value.focus();
  }
};
</script>

<template>
    <div class="center">
        <h2 class="rye">
            LOG IN
        </h2>
    </div>

    <form>
        <label for="username" class="rye">USERNAME</label>
        <input id="username" v-model="username" maxlength="32" autocomplete="username" @keyup.enter="focusPasswordElement">
        <label for="password" class="rye">PASSWORD</label>
        <input id="password" type="password" v-model="password" maxlength="150" autocomplete="current-password" ref="passwordElement" @keyup.enter="login">
    </form>
    <div class="error center red-text" v-if="error">{{ error }}</div>
    <div class="buttons-row buttons-row-center">
        <button class="button rye" @click="login()">
            LOG IN
        </button>
    </div>
</template>

<style scoped>
label {
    padding: 4px;
    margin: 4px;
    white-space: nowrap;
    justify-self: end;
}
form {
    display: grid;
    grid-template-columns: min-content max-content;
    justify-content: center;
}

@media (max-width: 330px) {
    form {
        display: flex;
        flex-direction: column;
    }

    label {
        text-align: center;
    }
}

input {
    padding: 4px;
    margin: 4px;
}
</style>