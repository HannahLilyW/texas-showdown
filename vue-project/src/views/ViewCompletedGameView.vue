<script setup lang="ts">
import { get } from '../services/api.js';
import type { Game } from '../models';
import { ref } from 'vue';
import type { Ref } from 'vue';
import CardComponent from '../components/CardComponent.vue';

const props = defineProps(['id']);

let game: Ref<Game|null> = ref(null);
let winners: Ref<string> = ref('');

function getCompletedGame() {
    get(`games/${props.id}/get_finished_game/`).then(response => {
        response.json().then(responseJson => {
            game.value = responseJson;


            winners.value = responseJson.winners[0];
            for (let index in responseJson.winners) {
                if (Number(index) > 0) {
                    winners.value += `, ${responseJson.winners[index]}`
                }
            }

        })
    })
}

getCompletedGame();

</script>

<template>
    <div class="turnhistory-set" v-if="game">
        <template v-for="turnhistory in game.turnhistory_set">
            <template v-if="turnhistory.turn == 0">
                <div class="hand">Hand {{ turnhistory.hand }}</div>
                <div v-for="betturnhistory in game.betturnhistory_set.filter(bth => bth.hand == turnhistory.hand)">
                    {{ betturnhistory.player }} {{ betturnhistory.bet_action.toLowerCase() }}s. Bet: ${{ betturnhistory.bet_amount }}. Remaining money: ${{ betturnhistory.player_money }}.
                </div>
            </template>
            <div class="spacer" v-if="(turnhistory.turn % game.num_players) == 0"></div>
            <div class="turnhistory">
                <div v-if="turnhistory.end_game">{{ turnhistory.player }} left the game</div>
                <template v-else>
                    <div class="played">{{ turnhistory.player }} played </div>
                    <CardComponent
                        :number="turnhistory.card"
                    ></CardComponent>
                </template>
            </div>
        </template>
        <div>Winner(s): {{ winners }}</div>
    </div>
</template>

<style scoped>
.turnhistory-set {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.turnhistory {
    display: flex;
    align-items: center;
    gap: 4px;
}

.spacer {
    height: 4px;
}

.played {
    width: 40em;
}
</style>
