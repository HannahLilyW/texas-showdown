<script setup lang="ts">
import { get, post, startSocket, stopSocket, currentGame, username } from '../services/api.js';
import { ref, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue';
import router from '../router';

let loading: Ref<boolean> = ref(true);

function getCurrentGame() {
    get('games/get_current_game/').then(response => {
        if (response.status == 204) {
            currentGame.value = null;
            router.push('/');
        }
        try {
            response.json().then(responseJson => {
                if (response.status == 200) {
                    currentGame.value = responseJson;
                    startSocket();
                    loading.value = false;
                } else {
                    console.log(`unexpected response. status: ${response.status} response: ${responseJson}`)
                }
            })
        } catch (e) {
            console.log(`error getting current game: ${e}`)
        }
    })
}

function leaveGame() {
    post('games/leave_game/', {}).then(response => {
        currentGame.value = null;
        router.push('/');
    })
}

onBeforeUnmount(() => stopSocket());

getCurrentGame();

</script>

<template>
<div v-if="currentGame">
    <h2>{{ currentGame.created_by }}'s game</h2>
    <p>Players:</p>
    <li v-for="player in currentGame.player_set">{{ player }}{{ player == currentGame.owner ? ' (Owner)' : ''}}</li>
    <div v-if="currentGame.player_set.length < currentGame.num_players">Waiting for {{ currentGame.num_players - currentGame.player_set.length }} more player(s).</div>
    <div v-if="(currentGame.player_set.length  == currentGame.num_players) && (username != currentGame.owner)">
        Waiting for {{ currentGame.owner }} to start the game.
    </div>
    <div class="buttons-row">
        <div class="button" v-if="username == currentGame.owner">Start Game</div>
        <div class="button" @click="leaveGame()">Leave Game</div>
    </div>
</div>
</template>

<style scoped>

</style>