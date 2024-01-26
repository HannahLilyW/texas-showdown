<script setup lang="ts">
import { postWithoutAuth, post, updateToken, updateUsername, username, is_guest } from '../services/api.js'
import { watch, ref } from 'vue'
import type { Ref } from 'vue'
import router from '../router'

// Form data
let newUsername: Ref<string> = ref("");
let password: Ref<string> = ref("");
let retypePassword: Ref<string> = ref("");

// Status variables
let passwordsMismatch: Ref<boolean> = ref(false);
let passwordTooShort: Ref<boolean> = ref(false);
let invalid: Ref<boolean> = ref(true);
let error: Ref<boolean|string> = ref(false);

function isValid() {
    return ((newUsername.value.length > 0) &&
        (newUsername.value.length <= 32) &&
        (newUsername.value.match(/^[A-Za-z0-9_]+$/)) &&
        (password.value.length > 7) &&
        (password.value.length <= 150) &&
        (password.value.match(/^[A-Za-z0-9_!@#$%^&*()]+$/)) &&
        !passwordsMismatch.value
    )
}

watch(newUsername, () => {
    invalid.value = !isValid();
})
watch(password, (newVal) => {
    passwordsMismatch.value = (newVal != retypePassword.value);
    passwordTooShort.value = (newVal.length < 8);
    invalid.value = !isValid();
})
watch(retypePassword, (newVal) => {
    passwordsMismatch.value = (newVal != password.value);
    invalid.value = !isValid();
})

function upgradeGuestAccount() {
    if (isValid()) {
        post('players/upgrade_account/', {
            'username': newUsername.value,
            'password': password.value
        }).then(response => {
            try {
                response.json().then(responseJson => {
                    if (response.status != 200) {
                        error.value = `Error creating account: ${responseJson.toString()}`;
                        return;
                    }
                    updateUsername(newUsername.value);
                    is_guest.value = false;
                    router.push('/');
                })
            } catch (e) {
                error.value = `Error creating account: ${e}`;
            }
        }) 
    }
}

function createAccount() {
    error.value = false;

    if (username && is_guest) {
        upgradeGuestAccount();
        return;
    }

    if (isValid()) {
        // Send the data
        postWithoutAuth('create_account/', {
            'username': newUsername.value,
            'password': password.value
        }).then(response => {
            try {
                response.json().then(responseJson => {
                    if (response.status != 200) {
                        error.value = `Error creating account: ${responseJson.toString()}`;
                        return;
                    }
                    if (responseJson['token'] && responseJson['username']) {
                        updateToken(responseJson['token']);
                        updateUsername(responseJson['username']);
                        router.push('/');
                    } else {
                        error.value = 'Error creating account: Bad response from server';
                    }
                })
            } catch (e) {
                error.value = `Error creating account: ${e}`;
            }
        })
    }
}

function cancel() {
    router.push('/');
}
</script>

<template>
    <h2>
        Create Account
    </h2>
    <div>
        <p>Create an account to sync across devices!</p>
        <br>
        <p>Usernames may contain letters, numbers, and underscores.</p>
        <br>
        <p>Passwords may contain letters, numbers, and the following characters: _ ! @ # $ % ^ & * ( )</p>
        <br>
    </div>

    <form>
        <label for="username">Username:</label>
        <input id="username" v-model="newUsername" maxlength="32">
        <label for="password">New Password:</label>
        <input id="password" type="password" v-model="password" maxlength="150">
        <label for="retypePassword">Retype Password:</label>
        <input id="retypePassword" type="password" v-model="retypePassword" maxlength="150">
    </form>
    <div class="error" v-if="passwordTooShort">Password too short</div>
    <div class="error" v-if="passwordsMismatch">Passwords do not match</div>
    <div class="error" v-if="error">{{ error }}</div>
    <div class="buttons-row">
        <div class="button" :class="{disabled: invalid}" @click="createAccount()">Create New Account</div>
        <div class="button button-danger" @click="cancel()">
            Cancel
        </div>
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
}

@media (max-width: 380px) {
    form {
        display: flex;
        flex-direction: column;
    }

    label, input {
        margin-left: 0px;
        padding-left: 0px;
        margin-right: 0px;
        padding-right: 0px;
    }
}

input {
    padding: 4px;
    margin: 4px;
}
</style>
