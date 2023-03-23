<script setup lang="ts">
import { get, post, startSocket, stopSocket, currentGame, hand, username } from '../services/api.js';
import { ref, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import Card from '../components/Card.vue';

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
                    getHand();
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

function startGame() {
    post('games/start_game/', {}).then(response => {
        response.json().then(responseJson => {
            currentGame.value = responseJson;
        })
    })
}

function getHand() {
    get('players/hand/').then(response => {
        response.json().then(responseJson => {
            hand.value = responseJson.sort((a: number, b: number) => {return a-b});
        })
    })
}

function dragStart(event: DragEvent, cardNumber: number) {
    if (event.dataTransfer) {
        event.dataTransfer.setData("cardNumber", cardNumber.toString());
        event.dataTransfer.dropEffect = "move";
    }
}

function dragEnter(event: DragEvent) {
    event.preventDefault();
}

function dragOver(event: DragEvent) {
    event.preventDefault();
}

function drop(event: DragEvent, targetNumber: number) {
    if (event.dataTransfer) {
        const droppedNumber = Number(event.dataTransfer.getData("cardNumber"));
        const droppedIndex = hand.value?.indexOf(droppedNumber);
        const targetIndex = hand.value?.indexOf(targetNumber);
        if (droppedIndex != -1) {
            hand.value?.splice(droppedIndex || 0, 1); // delete this card from its old position
        }
        if (targetIndex != -1) {
            hand.value?.splice(targetIndex || 0, 0, droppedNumber) // add the card after the card it was dropped on.
        }
    }
}

onBeforeUnmount(() => stopSocket());

getCurrentGame();

</script>

<template>
<div v-if="currentGame && !currentGame.is_started">
    <h2>{{ currentGame.created_by }}'s game</h2>
    <p>Players:</p>
    <li v-for="player in currentGame.player_set">{{ player.username }}{{ player.username == currentGame.owner ? ' (Owner)' : ''}}</li>
    <div v-if="currentGame.player_set.length < currentGame.num_players">Waiting for {{ currentGame.num_players - currentGame.player_set.length }} more player(s).</div>
    <div v-if="(currentGame.player_set.length  == currentGame.num_players) && (username != currentGame.owner)">
        Waiting for {{ currentGame.owner }} to start the game.
    </div>
    <div class="buttons-row">
        <div class="button"
            v-if="username == currentGame.owner && (currentGame.num_players == currentGame.player_set.length)"
            @click="startGame()">Start Game</div>
        <div class="button" @click="leaveGame()">Leave Game</div>
    </div>
</div>
<div v-if="currentGame && currentGame.is_started">
    <div class="current-game-background">
        <div>Player</div>
        <div>Play</div>
        <div>Tricks</div>
        <div>Score</div>
        <template class="other-player" v-for="player in currentGame.player_set" :key="player.position">
            <div class="player-username">{{ player.username }}</div>
            <div class="player-play"></div>
            <div class="player-tricks">tricks</div>
            <div class="player-score">5</div>
        </template>
    </div>
    <h2>Your Hand</h2>
    <div class="hand" v-if="hand">
        <Card
            class="card"
            :id="'handCard' + cardNumber"
            :number="cardNumber"
            v-for="cardNumber in hand"
            draggable="true"
            @dragstart="dragStart($event, cardNumber)"
            @dragenter="dragEnter($event)"
            @dragover="dragOver($event)"
            @drop="drop($event, cardNumber)"
        ></Card>
    </div>
    <div class="buttons-row">
        <div class="button" @click="leaveGame()">Leave Game</div>
    </div>
</div>
</template>

<style scoped>
.current-game-background {
    background-color: #35654d;
    width: 100vw;
    height: 100%;
    display: grid;
    grid-template-columns: 10% 20% 60% 10%;
    justify-items: center;
    align-items: center;
}

.player-play {
    height: 80px;
}

.hand {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.card {
    cursor: pointer;
}

</style>