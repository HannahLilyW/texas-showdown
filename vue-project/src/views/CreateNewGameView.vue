<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import { post, currentGame, money } from '../services/api.js';
import InfoComponent from '../components/InfoComponent.vue';

if (currentGame.value) {
    router.push('/');
}

watch(currentGame, () => {
    if (currentGame.value) {
        router.push('/');
    }
});

// Form data
let numPlayers: Ref<string> = ref("3");
let stakes: Ref<string> = ref("0");
let publicInput: Ref<string> = ref("public");

let error: Ref<string> = ref("");

function createNewGame() {
    post('games/', {
        'num_players': Number(numPlayers.value),
        'buy_in': Number(stakes.value),
        'is_private': Boolean(publicInput.value == 'private')
    }).then(response => {
        try {
            response.json().then(responseJson => {
                if (response.status != 201) {
                    error.value = `Error creating game: ${responseJson.toString()}`;
                    return;
                } else {
                    router.push('/active-game');
                }
            })
        } catch (e) {
            error.value = `Error creating game: ${e}`;
        }
    })
}

</script>

<template>
<h2 class="center rye">NEW GAME</h2>
<br/>
<form>
    <div class="center rye">PLAYERS</div>
    <div class="radio-row radio-row-center">
        <input id="numPlayers3" type="radio" v-model="numPlayers" value="3" selected>
        <label for="numPlayers3" class="rye">3</label>
        <input id="numPlayers4" type="radio" v-model="numPlayers" value="4">
        <label for="numPlayers4" class="rye">4</label>
        <input id="numPlayers5" type="radio" v-model="numPlayers" value="5">
        <label for="numPlayers5" class="rye">5</label>
        <input id="numPlayers6" type="radio" v-model="numPlayers" value="6">
        <label for="numPlayers6" class="rye">6</label>
    </div>
    <br/>
    <div class="center rye">BUY IN</div>
    <div class="radio-row radio-row-center radio-row-wrap">
        <input id="stakes0" type="radio" v-model="stakes" value="0" selected>
        <label for="stakes0" class="rye">JUST FOR FUN</label>
        <template v-if="money >= 5">
            <input id="stakes5" type="radio" v-model="stakes" value="5" selected>
            <label for="stakes5">
                <div class="coins center rye"><div class="coin-icon"></div>5</div>
            </label>
        </template>
        <template v-if="money >= 10">
            <input id="stakes10" type="radio" v-model="stakes" value="10" selected>
            <label for="stakes10">
                <div class="coins center rye"><div class="coin-icon"></div>10</div>
            </label>
        </template>
        <template v-if="money >= 50">
            <input id="stakes50" type="radio" v-model="stakes" value="50" selected>
            <label for="stakes50">
                <div class="coins center rye"><div class="coin-icon"></div>50</div>
            </label>
        </template>
        <template v-if="money >= 100">
            <input id="stakes100" type="radio" v-model="stakes" value="100" selected>
            <label for="stakes100">
                <div class="coins center rye"><div class="coin-icon"></div>100</div>
            </label>
        </template>
        <template v-if="money >= 500">
            <input id="stakes500" type="radio" v-model="stakes" value="500" selected>
            <label for="stakes500">
                <div class="coins center rye"><div class="coin-icon"></div>500</div>
            </label>
        </template>
        <template v-if="money >= 1000">
            <input id="stakes1000" type="radio" v-model="stakes" value="1000" selected>
            <label for="stakes1000">
                <div class="coins center rye"><div class="coin-icon"></div>1000</div>
            </label>
        </template>
        <template v-if="money >= 5000">
            <input id="stakes5000" type="radio" v-model="stakes" value="5000" selected>
            <label for="stakes5000">
                <div class="coins center rye"><div class="coin-icon"></div>5000</div>
            </label>
        </template>
    </div>
    <div class="center rye coins" v-if="Number(stakes) > 0">WIN UP TO <div class="coin-icon"></div>{{ Number(stakes) * Number(numPlayers) }}</div>
    <br/>
    <div class="center buttons-row">
        <div class="rye">ACCESS</div>
        <InfoComponent>
            <p>Anyone can join public games.</p>
            <br>
            <p>Only players with the room code can join private games.</p>
        </InfoComponent>
    </div>
    <div class="radio-row radio-row-center">
        <input id="public" type="radio" v-model="publicInput" value="public" selected>
        <label for="public" class="rye">PUBLIC</label>
        <input id="private" type="radio" v-model="publicInput" value="private">
        <label for="private" class="rye">PRIVATE</label>
    </div>
</form>
<br/>
<div class="error red-text center" v-if="error">{{ error }}</div>
<div class="buttons-row buttons-row-center">
    <div class="button rye" @click="createNewGame()">START GAME</div>
</div>
</template>

<style scoped>

input {
    width: auto;
    padding: 4px;
    margin: 4px;
}

form {
    display: flex;
    flex-direction: column;
    align-items: center;
}

</style>