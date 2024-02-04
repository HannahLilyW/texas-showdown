<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import { post, currentGame } from '../services/api.js';
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
let betting: Ref<string> = ref("false");
let publicInput: Ref<string> = ref("public");

let error: Ref<string> = ref("");

function cancel() {
    router.push('/');
}

function createNewGame() {
    post('games/', {
        'num_players': Number(numPlayers.value),
        // 'betting': Boolean(betting.value == 'true')
        'betting': false
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