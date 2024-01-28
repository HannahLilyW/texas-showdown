<script setup lang="ts">
import { get, post, startSocket, stopSocket, existingGames } from '../services/api.js';
import { ref, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue';
import type { Game } from '../models';
import router from '../router';

let loading: Ref<boolean> = ref(true);

function createNewGame() {
    router.push('/create-new-game');
}

function getExistingGames() {
    get('games/get_existing_games/').then(response => {
        response.json().then(responseJson => {
            if (response.status == 200) {
                existingGames.value = responseJson;
                loading.value = false;
                startSocket();
            } else {
                console.log(`unexpected response. status: ${response.status} response: ${responseJson}`)
            }
        })
    })
}

function joinGame(game: Game) {
    post('games/join_game/', {'id': game.id}).then(response => {
        response.json().then(() => {
            if (response.status == 200) {
                router.push('/active-game');
            }
        })
    })
}

getExistingGames();

onBeforeUnmount(() => {
    stopSocket();
});

</script>

<template>
<div class="buttons-row buttons-row-center">
    <div class="button rye" @click=createNewGame()>CREATE GAME</div>
    <div class="button rye">JOIN PRIVATE GAME</div>
</div>
<h2 class="rye center">PUBLIC GAMES</h2>
<template v-if="!loading">
    <div class="buttons-column" v-if="existingGames && existingGames.length">
        <div class="button" v-for="game in existingGames" @click="joinGame(game)" :key="game.id">
            <div>
                <div>{{ game.owner_name }}'s game</div>
                <div class="subtitle">{{ game.player_set.length }} of {{ game.num_players }} players</div>
            </div>
        </div>
    </div>
    <template v-else>
        <p class="center">No public games to join. Create a new one!</p>
    </template>
</template>

</template>

<style scoped>
.subtitle {
    font-size: 0.8em;
    opacity: 0.5;
}
</style>