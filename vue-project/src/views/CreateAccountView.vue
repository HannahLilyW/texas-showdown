<script setup lang="ts">
import { postWithoutAuth, post, updateToken, updateUsername, username, is_guest } from '../services/api.js';
import { watch, ref } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import InfoComponent from '../components/InfoComponent.vue';

// Form data
let newUsername: Ref<string> = ref("");
let password: Ref<string> = ref("");
let retypePassword: Ref<string> = ref("");

// Status variables
let passwordsMismatch: Ref<boolean> = ref(false);
let passwordTooShort: Ref<boolean> = ref(false);
let passwordDisallowedCharacter: Ref<boolean> = ref(false);
let usernameDisallowedCharacter: Ref<boolean> = ref(false);
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

watch(newUsername, (newVal) => {
    invalid.value = !isValid();
    usernameDisallowedCharacter.value = !(newUsername.value.match(/^[A-Za-z0-9_]+$/)) && !!newVal.length;
})
watch(password, (newVal) => {
    passwordsMismatch.value = (newVal != retypePassword.value);
    passwordTooShort.value = (newVal.length < 8);
    passwordDisallowedCharacter.value = !(newVal.match(/^[A-Za-z0-9_!@#$%^&*()]+$/)) && !!newVal.length;
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

    if (username.value && is_guest.value) {
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

const passwordElement: Ref<HTMLInputElement|null> = ref(null);
const retypePasswordElement: Ref<HTMLInputElement|null> = ref(null);

const focusPasswordElement = () => {
  if (passwordElement.value) {
    passwordElement.value.focus();
  }
};

const focusRetypePasswordElement = () => {
  if (retypePasswordElement.value) {
    retypePasswordElement.value.focus();
  }
};
</script>

<template>
    <div class="center">
        <h2 class="rye">
            CREATE ACCOUNT
        </h2>
        <p>Create an account to save your progress and sync across devices!</p>
    </div>

    <form>
        <div class="label">
            <label for="username" class="rye">USERNAME</label>
            <InfoComponent>
                Usernames may contain letters, numbers, and underscores.
            </InfoComponent>
        </div>
        <input id="username" v-model="newUsername" maxlength="32" autocomplete="username" @keyup.enter="focusPasswordElement">
        <div class="label">
            <label for="password" class="rye">NEW PASSWORD</label>
            <InfoComponent>
                Passwords may contain letters, numbers, and the following characters: _ ! @ # $ % ^ & * ( )
            </InfoComponent>
        </div>
        <input id="password" type="password" v-model="password" maxlength="150" autocomplete="new-password" ref="passwordElement" @keyup.enter="focusRetypePasswordElement">
        <div class="label">
            <label for="retypePassword" class="rye">RETYPE PASSWORD</label>
        </div>
        <input id="retypePassword" type="password" v-model="retypePassword" maxlength="150" autocomplete="new-password" ref="retypePasswordElement" @keyup.enter="createAccount">
    </form>
    <div class="error center red-text" v-if="passwordTooShort">Password too short</div>
    <div class="error center red-text" v-if="passwordsMismatch">Passwords do not match</div>
    <div class="error center red-text" v-if="passwordDisallowedCharacter">Password contains a character that is not allowed</div>
    <div class="error center red-text" v-if="usernameDisallowedCharacter">Username contains a character that is not allowed</div>
    <div class="error center red-text" v-if="error">{{ error }}</div>
    <div class="buttons-row buttons-row-center">
        <div class="button rye" :class="{disabled: invalid}" @click="createAccount()">CREATE ACCOUNT</div>
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

@media (max-width: 380px) {
    form {
        display: flex;
        flex-direction: column;
    }
}

input {
    padding: 4px;
    margin: 4px;
}

.label {
    display: flex;
    align-items: center;
    text-align: center;
    justify-content: end;
}

@media (max-width: 380px) {
    .label {
        justify-content: center;
    }
}
</style>
