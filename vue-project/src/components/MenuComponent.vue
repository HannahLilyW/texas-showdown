<script setup lang="ts">
import { ref, computed } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import { username, money, logout, name, background_color, shirt_color, skin_color, hat_color, is_guest, currentGame, leaveGame, updateOwnProfileInfo } from '../services/api.js';
import ProfilePicComponent from './ProfilePicComponent.vue';
import MusicIcon from './icons/IconMusic.vue';
import '../assets/switch.css';

let showMenu: Ref<boolean> = ref(false);

let music = ref();
let musicCheckbox = ref();

const musicUnpaused = computed(() => {
    return !music.value.paused;
})

function hide() {
    showMenu.value = false;
}

function show() {
    if (username.value) {
        updateOwnProfileInfo();
    }
    showMenu.value = true;
}

function createAccount() {
  router.push('/create-account');
}

function logIn() {
  router.push('/login');
}

function rules() {
  router.push('/rules');
}

function editProfile() {
    router.push('/edit-profile/landing-page');
}

function quitCurrentGame() {
    leaveGame(() => {
        router.push('/');
    })
}

function multiplayer() {
    if (username.value) {
        if (!currentGame.value) {
            router.push('/join-existing-game');
        } else {
            router.push('/active-game');
        }
    } else {
        router.push('/edit-profile/join-existing-game');
    }
}

function soloPlay() {
    router.push('/solo-play');
}

function toggleMusic(event: Event) {
    event.stopPropagation();
    if (music.value.paused) {
        music.value.play();
        musicCheckbox.value.checked = true;
    } else {
        music.value.pause();
        musicCheckbox.value.checked = false;
    }
}

function fontSize(value: string) {
    if (value.length <= 19) {
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
    <audio autoplay src="/sounds/oldwesternmusic.mp3" type="audio/mpeg" ref="music"></audio>
    <div class="modal-parent" v-if="showMenu" @click="hide()">
        <div class="sidebar">
            <div id="profile" class="point" v-if="username" @click="editProfile()">
                <ProfilePicComponent
                    :background_color="background_color"
                    :shirt_color="shirt_color"
                    :skin_color="skin_color"
                    :hat_color="hat_color"
                ></ProfilePicComponent>
                <pre class="name" :class="fontSize(name)">{{ name }}</pre>
                <pre class="username" :class="fontSize(username)">{{ username }}</pre>
            </div>
            <div class="coins" v-if="username"><div class="coin-icon"></div>{{ money }}</div>
            <div class="button rye" @click="soloPlay()">
                SINGLE PLAYER
            </div>
            <div class="button rye" @click="multiplayer()">
                MULTIPLAYER
            </div>
            <div class="button button-danger rye" v-if="currentGame" @click="quitCurrentGame()">QUIT CURRENT GAME</div>
            <div class="button rye" v-if="username && !is_guest" @click="logout()">
                LOG OUT
            </div>
            <div class="button rye" v-if="!username || (username && is_guest)" @click="logIn()">
                LOG IN
            </div>
            <div class="button rye" v-if="!username || (username && is_guest)" @click="createAccount()">
                CREATE ACCOUNT
            </div>
            <div class="button rye" @click="rules()">
                RULES
            </div>
            <div class="button rye relative buttons-row buttons-row-space-between" @click="toggleMusic($event)">
                    <MusicIcon class="icon-small"></MusicIcon>
                    <div class="rye">MUSIC</div>
                    <label class="switch">
                        <input type="checkbox" v-model="musicUnpaused" ref="musicCheckbox" readonly>
                        <span class="slider round"></span>
                    </label>
                <div class="button-overlay">
                </div>
            </div>
        </div>
    </div>
</template>

<style>

.relative {
    position: relative;
}

.button-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;

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

#profile {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 8px;
}
</style>