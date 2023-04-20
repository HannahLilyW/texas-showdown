<script setup lang="ts">
import { get } from '../services/api.js';
import { ref } from 'vue';
import type { Ref } from 'vue';
import type { PlayerStatistic } from '../models';

let playerStatistics: Ref<PlayerStatistic[]> = ref([]);

function getPlayerStatistics() {
    get('players/view_player_statistics/').then(response => {
        response.json().then(responseJson => {
            playerStatistics.value = responseJson;
        })
    })
}

getPlayerStatistics();
</script>

<template>
    <div class="player-statistic-table">
        <div>Player</div>
        <div>Wins</div>
        <div>Losses</div>
        <template v-for="playerStatistic in playerStatistics">
            <div>{{ playerStatistic.username }}</div>
            <div>{{ playerStatistic.wins }}</div>
            <div>{{ playerStatistic.losses }}</div>
        </template>
    </div>
</template>

<style scoped>
.player-statistic-table {
    display: grid;
    grid-template-columns: min-content min-content min-content;
    width: 100vw;
    column-gap: 40px;
    justify-items: center;
    align-items: center;
    justify-content: center;
}
</style>