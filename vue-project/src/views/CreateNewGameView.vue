<script setup lang="ts">
import { ref } from 'vue'
import type { Ref } from 'vue'
import router from '../router'
import { post } from '../services/api.js'

// Form data
let numPlayers: Ref<string> = ref("3");
let betting: Ref<string> = ref("false");

let error: Ref<string> = ref("");

function cancel() {
    router.push('/');
}

function createNewGame() {
    post('games/', {
        'num_players': Number(numPlayers.value),
        'betting': Boolean(betting.value == 'true')
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
<h2>Create New Game</h2>

<form>
    <div class="top-label">Number of Players:</div>
    <div class="radio-row">
        <input id="numPlayers3" type="radio" v-model="numPlayers" value="3" selected>
        <label for="numPlayers3">3</label>
        <input id="numPlayers4" type="radio" v-model="numPlayers" value="4">
        <label for="numPlayers4">4</label>
        <input id="numPlayers5" type="radio" v-model="numPlayers" value="5">
        <label for="numPlayers5">5</label>
        <input id="numPlayers6" type="radio" v-model="numPlayers" value="6">
        <label for="numPlayers6">6</label>
    </div>
    <label class="top-label" for="bettingInput" hidden>Betting:</label>
    <div class="radio-row" hidden>
        <input id="noBetting" type="radio" v-model="betting" value="false" selected>
        <label for="noBetting">Just for Fun</label>
        <input id="betting" type="radio" v-model="betting" value="true">
        <label for="betting">High Stakes</label>
    </div>
</form>
<div class="error" v-if="error">{{ error }}</div>
<div class="buttons-row">
    <div class="button" @click="createNewGame()">Create New Game</div>
    <div class="button" @click="cancel()">Cancel</div>
</div>
</template>

<style scoped>
.top-label {
    padding: 4px;
    margin: 4px;
    white-space: nowrap;
    justify-self: end;
}
form {
    display: grid;
    grid-template-columns: min-content max-content;
    justify-items: start;
    align-items: center;
}
input {
    width: auto;
    padding: 4px;
    margin: 4px;
}

</style>