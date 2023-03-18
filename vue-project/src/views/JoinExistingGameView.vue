<script setup lang="ts">
import { get, post } from '../services/api.js';
import { ref } from 'vue';
import type { Ref } from 'vue';
import type { Game } from '../models';
import router from '../router';

let existingGames: Ref<Game[]|null> = ref(null);
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
            } else {
                console.log(`unexpected response. status: ${response.status} response: ${responseJson}`)
            }
        })
    })
}

function joinGame(game: Game) {
    post('games/join_game/', {'id': game.id}).then(response => {
        response.json().then(responseJson => {
            if (response.status == 200) {
                router.push('/active-game');
            }
        })
    })
}

getExistingGames();

</script>

<template>
<h2>Join Existing Game</h2>
<template v-if="!loading">
    <div class="buttons-column" v-if="existingGames">
        <div class="button" v-for="game in existingGames" @click="joinGame(game)">
            {{ game.owner }}'s game - {{ game.betting ? 'High Stakes' : 'Just for Fun' }} ({{ game.player_set.length }} out of {{ game.num_players }} players)
        </div>
    </div>
    <template v-else>
        <p>No existing games to join.</p>
        <div class="button" @click=createNewGame()>Create New Game</div>
    </template>
</template>

</template>

<style scoped>

</style>