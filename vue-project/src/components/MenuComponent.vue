<script setup lang="ts">
import { ref } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import { username, logout, name, background_color, shirt_color, skin_color, hat_color, is_guest } from '../services/api.js';
import ProfilePicComponent from './ProfilePicComponent.vue';

let showMenu: Ref<boolean> = ref(false);

function hide() {
    showMenu.value = false;
}

function show() {
    showMenu.value = true;
}

function createAccount() {
  router.push('/create-account');
}

function logIn() {
  router.push('/login');
}

function editProfile() {
    router.push('/edit-profile');
}

function fontSize(value: string) {
    if (value.length <= 20) {
        return '';
    } else if (value.length <= 29) {
        return 'smallfont';
    } else {
        return 'tinyfont';
    }
}

defineExpose({
  show
})

</script>

<template>
    <div class="modal-parent" v-if="showMenu" @click="hide()">
        <div class="sidebar">
            <div id="profile" class="point" v-if="username" @click="editProfile()">
                <ProfilePicComponent
                    :background_color="background_color"
                    :shirt_color="shirt_color"
                    :skin_color="skin_color"
                    :hat_color="hat_color"
                ></ProfilePicComponent>
                <div class="name" :class="fontSize(name)">{{ name }}</div>
                <div class="username" :class="fontSize(username)">{{ username }}</div>
            </div>
            <div class="button" v-if="username && !is_guest" @click="logout()">
                Log Out
            </div>
            <div class="button" v-if="!username || (username && is_guest)" @click="logIn()">
                Log In
            </div>
            <div class="button" v-if="!username || (username && is_guest)" @click="createAccount()">
                Create Account
            </div>
        </div>
    </div>
</template>

<style>
#profilePic {
    background-color: lightblue;
    border-radius: 8px;
    height: 100px;
    width: 100px;
    border: 4px solid gold;
}

.modal-parent {
    position: fixed;
    height: 100%;
    width: 100%;
    left: 0;
    top: 0;
    background: rgba(0, 0, 0, 0.3);
    cursor: auto;
    z-index: 1;
}

.sidebar {
    position: fixed;
    top: 0;
    right: 0;
    height: 100%;
    box-shadow: 0 0 100px 60px rgba(0, 0, 0, 0.3);
    background-color: var(--color-background);
    width: 200px;

    display: flex;
    flex-direction: column;
    gap: 4px;
    align-items: stretch;
}

.username {
    font-size: 0.8em;
    opacity: 0.5;
    max-width: 180px;
    word-wrap: break-word;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.smallfont {
    font-size: 0.7em;
}

.tinyfont {
    font-size: 0.6em;
}

.microfont {
    font-size: 0.5em;
}

.name {
    max-width: 136px;
    word-wrap: break-word;
    overflow: hidden;
    text-overflow: ellipsis;
}

#profile {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
}
</style>