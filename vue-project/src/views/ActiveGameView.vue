<script setup lang="ts">
import { get, post, startSocket, stopSocket, currentGame, hand, username } from '../services/api.js';
import { watch, ref, onBeforeUnmount, computed } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import Card from '../components/Card.vue';

let loading: Ref<boolean> = ref(true);
let activeCard: Ref<number|null> = ref(null);
let error: Ref<string> = ref('');

watch(currentGame, () => {
    getHand();
})

const recentHistory = computed(() => {
    /**
     * Returns the TurnHistories for the turns in this trick so far, if any.
     */
    if (currentGame.value) {
        const turnHistoriesInCurrentHand = currentGame.value.turnhistory_set.filter(turn_history => (turn_history.hand == currentGame.value?.hand));
        const firstTurnOfTrick = Math.floor(currentGame.value.turn / currentGame.value.num_players) * currentGame.value.num_players;
        return turnHistoriesInCurrentHand.slice(firstTurnOfTrick);
    }
    return [];
})

const lastTrickHistory = computed(() => {
    /**
     * Returns the TurnHistories for the turns in the last trick, if any.
     */
    if (currentGame.value) {
        const firstTurnOfTrick = Math.floor(currentGame.value.turn / currentGame.value.num_players) * currentGame.value.num_players;
        if (firstTurnOfTrick == 0) {
            // Return the last {{num_players}} TurnHistories from the last hand.
            return currentGame.value.turnhistory_set.filter(turn_history => (
                (turn_history.hand == ((currentGame.value?.hand || 0) - 1)) &&
                (turn_history.turn >= (60 - (currentGame.value?.num_players || 0)))
            ));
        } else {
            // Return the last {{num_players}} TurnHistories in this hand before the firstTurnOfTrick.
            return currentGame.value.turnhistory_set.filter(turn_history => (
                (turn_history.hand == currentGame.value?.hand) &&
                (turn_history.turn < firstTurnOfTrick) &&
                (turn_history.turn >= (firstTurnOfTrick - (currentGame.value?.num_players || 0)))
            ));
        }
    }
    return [];
})

const playersWaitingForContinue = computed(() => {
    /**
     * Returns the usernames for the users we are waiting on to click continue
     */
    if (currentGame.value) {
        return currentGame.value.player_set.filter(player => player.waiting_for_continue).map(player => player.username);
    }
    return [];
})

const winners = computed(() => {
    /**
     * Returns a nicely formatted string containing the list of winners if the game is finished,
     * else returns an empty string
     */
    if (currentGame.value && currentGame.value.is_finished) {
        let ret = currentGame.value.winners[0]
        for  (let index in currentGame.value.winners) {
            if (Number(index) > 0) {
                ret += `, ${currentGame.value.winners[index]}`;
            }
        }
        return ret;
    }
    return '';
})

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
    post('games/start_game/', {}).then(response => {})
}

function getHand() {
    get('players/hand/').then(response => {
        response.json().then(responseJson => {
            hand.value = responseJson.sort((a: number, b: number) => {return a-b});
            if (hand.value && activeCard.value && !hand.value.includes(activeCard.value)) {
                activeCard.value = null;
            }
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

function activate(cardNumber: number) {
    activeCard.value = cardNumber;
}

function playActiveCard() {
    post('cards/play/', {'number': activeCard.value || 0}).then(response => {
        response.json().then(responseJson => {
            if (response.status == 400) {
                error.value = responseJson;
            } else {
                error.value = '';
            }
        })
    })
}

function continueGame() {
    post('games/continue_game/', {}).then(response => {})
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
            <div class="player-play">
                <template v-if="playersWaitingForContinue.length">
                    <Card
                        v-if="lastTrickHistory.find(history => history.player == player.username)"
                        :number="lastTrickHistory.find(history => history.player == player.username)?.card"
                        :class="{active: player.is_turn}"
                    >
                    </Card>
                </template>
                <template v-else>
                    <Card 
                        v-if="recentHistory.find(history => history.player == player.username)"
                        :number="recentHistory.find(history => history.player == player.username)?.card"
                    >
                    </Card>
                </template>
            </div>
            <div class="player-tricks">{{ player.tricks }}</div>
            <div class="player-score">{{ player.score }}</div>
        </template>
    </div>
    <div class="game-status">
        <template v-if="currentGame.is_finished">
            Game over! {{ winners }} won!
        </template>
        <template v-else-if="playersWaitingForContinue.length">
            {{ currentGame.player_set.find(player => player.is_turn)?.username }} took the trick!
            <br/>
            <template v-if="playersWaitingForContinue.length > 1">
                Waiting for {{ playersWaitingForContinue.length }} players to click continue...
            </template>
            <template v-else>
                Waiting for {{ playersWaitingForContinue[0] }} to click continue...
            </template>
        </template>
        <template v-else-if="currentGame.turn == 0">
            <template v-if="!(hand?.includes(0))">Waiting for {{ currentGame.player_set.find(player => player.is_turn)?.username }} to play the 0...</template>
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn! You must play the 0</template>
        </template>
        <template v-else>
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn!</template>
            <template v-else>{{ currentGame.player_set.find(player => player.is_turn)?.username }}'s turn</template>
        </template>
    </div>
    <div class="buttons-row">
        <div class="button" v-if="playersWaitingForContinue.includes(username)" @click="continueGame()">Continue</div>
        <template v-else-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">
            <div class="button" v-if="typeof activeCard == 'number'" @click="playActiveCard()">Play the {{activeCard}}</div>
        </template>
        <div class="error" v-if="error">{{ error }}</div>
    </div>
    <div class="hand" v-if="hand">
        <Card
            class="hand-card"
            :class="{active: cardNumber == activeCard}"
            :id="'handCard' + cardNumber"
            :number="cardNumber"
            v-for="cardNumber in hand"
            draggable="true"
            @dragstart="dragStart($event, cardNumber)"
            @dragenter="dragEnter($event)"
            @dragover="dragOver($event)"
            @drop="drop($event, cardNumber)"
            @click="activate(cardNumber)"
        ></Card>
    </div>
    <div class="buttons-row">
        <div class="button" @click="leaveGame()">Leave Game</div>
    </div>
</div>
</template>

<style scoped>
.current-game-background {
    background-color: var(--color-button-shadow);
    width: 100vw;
    height: 100%;
    display: grid;
    grid-template-columns: fit-content(200px) min-content min-content min-content;
    column-gap: 40px;
    justify-items: center;
    align-items: center;
    justify-content: center;
}

.player-play {
    height: 94px;
}

.hand {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
}

.hand-card {
    cursor: pointer;
}

.active {
    border: 4px solid var(--color-card-selected);
}

</style>