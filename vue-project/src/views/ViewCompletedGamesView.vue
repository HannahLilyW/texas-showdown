<script setup lang="ts">
import { get } from '../services/api.js';
import type { GameMetadata } from '../models';
import { ref } from 'vue';
import type { Ref } from 'vue';
import router from '../router';


let completedGames: Ref<GameMetadata[]> = ref([]);

function getCompletedGames() {
    get('games/get_finished_games/').then(response => {
        response.json().then(responseJson => {
            completedGames.value = responseJson;
        })
    })
}

function viewCompletedGame(id: number) {
    router.push(`view-completed-game/${id}`)
}

getCompletedGames();

</script>

<template>
<h2>View Completed Games</h2>
<div class="buttons-column">
    <div class="button" v-for="game in completedGames" @click="viewCompletedGame(game.id)">
        {{ game.owner }}'s game
        <br>
        created on {{ (new Date(game.created)).toDateString() }} at {{ (new Date(game.created)).toLocaleTimeString() }}
    </div>
</div>
</template>

<style scoped></style>