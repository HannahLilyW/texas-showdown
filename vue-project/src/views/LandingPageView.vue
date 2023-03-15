<script setup lang="ts">
import router from '../router';
import { username, get } from '../services/api.js';
import { ref } from 'vue';
import type { Ref } from 'vue';
import type { Game } from '../models';

let currentGame: Ref<Game|null> = ref(null);
let loading: Ref<boolean> = ref(true);

function getCurrentGame() {
    if (username.value) {
        get('games/get_current_game/').then(response => {
            if (response.status == 204) {
                loading.value = false;
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
                })
            } catch (e) {
                console.log(`error getting current game: ${e}`)
            }
        })
    } else {
        loading.value = false;
    }
}

function createAccount() {
    router.push('/create-account');
}

function logIn() {
    router.push('/login');
}

function createNewGame() {
    router.push('/create-new-game');
}

function activeGame() {
    router.push('/active-game')
}

function joinExistingGame() {
    router.push('/join-existing-game');
}

function viewCompletedGames() {
    router.push('/view-completed-games');
}

function viewPlayerStatistics() {
    router.push('/view-player-statistics');
}

getCurrentGame();

</script>

<template>
    <nav v-if="!loading">
        <div v-if="username" class="buttons-row">
            <div class="button" v-if="!currentGame" @click="createNewGame()">
                Create New Game
            </div>
            <div class="button" v-if="!currentGame" @click="joinExistingGame()">
                Join Existing Game
            </div>
            <div class="button" v-if="currentGame" @click="activeGame()">
                Go to Active Game
            </div>
            <div class="button" @click="viewCompletedGames()">
                View Completed Games
            </div>
            <div class="button" @click="viewPlayerStatistics()">
                View Player Statistics
            </div>
        </div>
        <div v-else class="buttons-row">
            <div class="button" @click="createAccount()">
                Create Account
            </div>
            <div class="button" @click="logIn()">
                Log In
            </div>
        </div>
    </nav>
</template>

<style scoped>
</style>