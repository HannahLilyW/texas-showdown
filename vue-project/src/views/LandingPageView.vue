<script setup lang="ts">
import router from '../router';
import { username, currentGame, get } from '../services/api.js';
import { ref } from 'vue';
import type { Ref } from 'vue';
import { music } from '../services/music.js';

let loading: Ref<boolean> = ref(true);

function getCurrentGame(callback?: Function) {
    if (username.value) {
        get('games/get_current_game/').then(response => {
            if (response.status == 204) {
                loading.value = false;
                if (callback) {
                    callback();
                }
                return;
            }
            try {
                response.json().then(responseJson => {
                    if (response.status == 200) {
                        currentGame.value = responseJson;
                        loading.value = false;
                    } else {
                        console.log(`unexpected response. status: ${response.status} response: ${responseJson}`)
                    }
                    if (callback) {
                        callback();
                    }
                })
            } catch (e) {
                console.log(`error getting current game: ${e}`)
                if (callback) {
                    callback();
                }
            }
        })
    } else {
        loading.value = false;
        if (callback) {
            callback();
        }
    }
}

function playNow() {
    if (localStorage.getItem("music") != "false") {
        music.value.play();
    }
    getCurrentGame(() => {
        if (username.value) {
            if (!currentGame.value) {
                router.push('/join-existing-game');
            } else {
                router.push('/active-game');
            }
        } else {
            router.push('/edit-profile/join-existing-game');
        }
    })
}

function soloPlay() {
    if (localStorage.getItem("music") != "false") {
        music.value.play();
    }
    router.push('/solo-play');
}

getCurrentGame();

</script>

<template>
    <nav>
        <div class="buttons-row buttons-row-center">
            <div class="button button-big rye" @click="soloPlay()">SINGLE PLAYER</div>
            <div class="button button-big rye" @click="playNow()">MULTIPLAYER</div>
        </div>
    </nav>
    <div class="spacer"></div>
    <img src="../assets/images/cowboyHoldingWesternWagerCards.jpg" class="cover-pic">
</template>

<style scoped>

nav {
    margin-top: 40px;
}

.spacer {
    height: 20px;
}

.cover-pic {
    max-width: 90%;
    max-height: 90%;
    margin: auto;
    display: block;
    border: 8px solid var(--color-button-shadow);
    border-radius: 8px;
}

</style>