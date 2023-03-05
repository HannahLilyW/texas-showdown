<script setup lang="ts">
import { postWithoutAuth, updateToken, updateUsername } from '../api.js'
import { watch, ref } from 'vue'
import type { Ref } from 'vue'
import router from '../router'

// Form data
let username: Ref<string> = ref("");
let password: Ref<string> = ref("");
let retypePassword: Ref<string> = ref("");

// Status variables
let passwordsMismatch: Ref<boolean> = ref(false);
let invalid: Ref<boolean> = ref(true);
let error: Ref<boolean|string> = ref(false);

function isValid() {
    return ((username.value.length > 0) &&
        (username.value.length <= 150) &&
        (username.value.match(/^[A-Za-z0-9_]+$/)) &&
        (password.value.length > 7) &&
        (password.value.length <= 150) &&
        (password.value.match(/^[A-Za-z0-9_!@#$%^&*()]+$/)) &&
        !passwordsMismatch.value
    )
}

watch(username, () => {
    invalid.value = !isValid();
})
watch(password, (newVal) => {
    passwordsMismatch.value = (newVal != retypePassword.value);
    invalid.value = !isValid();
})
watch(retypePassword, (newVal) => {
    passwordsMismatch.value = (newVal != password.value);
    invalid.value = !isValid();
})

function createAccount(event: Event) {
    error.value = false;

    // Needed because by default, pressing a button in a form will reload the page. We don't want that.
    event.preventDefault();

    if (isValid()) {
        // Send the data
        postWithoutAuth('create_account/', {'username': username.value, 'password': password.value}).then(response => {
            try {
                response.json().then(responseJson => {
                    if (response.status != 200) {
                        error.value = `Error creating account: ${responseJson.toString()}`;
                        return;
                    }
                    if (responseJson['token'] && responseJson['username']) {
                        updateToken(responseJson['token']);
                        updateUsername(responseJson['username']);
                        router.push('/home');
                    } else {
                        error.value = 'Error creating account: Bad response from server';
                    }
                })
            } catch (e) {
                error.value = `Error creating account: ${e}`;
            }
        })
    }
};

function cancel() {
    router.push('/');
}
</script>

<template>
    <header>
        Create New Account
    </header>
    <div>
        <p>Usernames must be 1-150 characters and may consist of letters, numbers, and underscores.</p>
        <p>Passwords must be 8-150 characters and may only contain letters, digits, and the following characters: _ ! @ # $ % ^ & * ( )</p>
    </div>

    <form>
        <label for="username">Username:</label>
        <input id="username" v-model="username" maxlength="150">
        <label for="password">New Password:</label>
        <input id="password" type="password" v-model="password" maxlength="150">
        <label for="retypePassword">Retype Password:</label>
        <input id="retypePassword" type="password" v-model="retypePassword" maxlength="150">
    </form>
    <div class="error" v-if="passwordsMismatch">Passwords do not match</div>
    <div class="error" v-if="error">{{ error }}</div>
    <div class="buttons-row">
        <button class="button" :class="{disabled: invalid}" @click="createAccount($event)">Create New Account</button>
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
