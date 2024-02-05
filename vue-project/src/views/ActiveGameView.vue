<script setup lang="ts">
import { get, post, startSocket, stopSocket, currentGame, hand, username } from '../services/api.js';
import type { Player } from '../models';
import { watch, ref, onBeforeUnmount, computed } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import CardComponent from '../components/CardComponent.vue';
import ProfilePicComponent from '../components/ProfilePicComponent.vue';

const black = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const red = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20];
const blue = [21, 22, 23, 24, 25, 26, 27, 28, 29];
const brown = [31, 32, 33, 34, 35, 36, 37, 38];
const green = [41, 42, 43, 44, 45, 46, 47];
const yellow = [51, 52, 53, 54, 55, 56];
const purple = [61, 62, 63, 64, 65];
const gray = [71, 72, 73, 74];

let loading: Ref<boolean> = ref(true);
let activeCard: Ref<number|null> = ref(null);
let error: Ref<string> = ref('');
let betAmount: Ref<number|null> = ref(null);

const timeout: Ref<number> = ref(0);

const reorderedPlayerSet: Ref<Player[]> = ref([]);

function getReorderedPosition(originalPosition: number) {
    if (window.screen.width < 360) {
        return originalPosition;
    }
    if (currentGame.value) {
        if (currentGame.value.num_players == 3) {
            if (originalPosition == 0) return 0;
            if (originalPosition == 1) return 2;
            if (originalPosition == 2) return 1;
        } else if (currentGame.value.num_players == 4) {
            if (originalPosition == 0) return 0;
            if (originalPosition == 1) return 2;
            if (originalPosition == 2) return 3;
            if (originalPosition == 3) return 1;
        } else if (currentGame.value.num_players == 5) {
            if (originalPosition == 0) return 0;
            if (originalPosition == 1) return 2;
            if (originalPosition == 2) return 4;
            if (originalPosition == 3) return 3;
            if (originalPosition == 4) return 1;
        } else if (currentGame.value.num_players == 6) {
            if (originalPosition == 0) return 0;
            if (originalPosition == 1) return 2;
            if (originalPosition == 2) return 4;
            if (originalPosition == 3) return 5;
            if (originalPosition == 4) return 3;
            if (originalPosition == 5) return 1;
        }
    }
    return originalPosition;
}

watch(currentGame, (newVal, oldVal) => {
    error.value = '';
    if (
        newVal
        && oldVal
        && !newVal.is_started
        && (newVal.player_set.length  == newVal.num_players)
        && !(oldVal.player_set.length  == oldVal.num_players)
    ) {
        // start the timer
        const secondsSinceServerTimeReset = Math.floor((new Date().getTime() - new Date(newVal.last_timer_reset).getTime()) / 1000);
        resetTimer(30 - secondsSinceServerTimeReset);
    }
    if (newVal) {
        reorderedPlayerSet.value = [];
        for (let player of newVal.player_set) {
            let playerClone = JSON.parse(JSON.stringify(player));
            playerClone.position = getReorderedPosition(playerClone.position);
            reorderedPlayerSet.value.push(playerClone);
        }
        reorderedPlayerSet.value.sort((a, b) => {
            return a.position - b.position;
        })
    }
    getHand();
})

function decrementTimer() {
    if (timeout.value > 0) {
        timeout.value -= 1;
        setTimeout(decrementTimer, 1000);
    }
}

function resetTimer(seconds: number) {
    if (seconds > 0) {
        timeout.value = seconds;
        setTimeout(decrementTimer, 1000);
    }
}

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

const lastTrickTaker = computed(() => {
    // Return the TurnHistory for the player who took the trick in the last trick
    // Figure out which color(s) was played most
    let colorFrequencies = [0, 0, 0, 0, 0, 0, 0, 0];
    const colors = [black, red, blue, brown, green, yellow, purple, gray];
    for (let turnHistory of lastTrickHistory.value) {
        let i = 0;
        for (let color of colors) {
            if (color.indexOf(turnHistory.card || 0) != -1) {
                colorFrequencies[i]++;
            }
            i++;
        }
    }
    let maxColors: number[] = [];
    for (let i = 0; i < colorFrequencies.length; i++) {
        if (colorFrequencies[i] == Math.max(...colorFrequencies)) {
            maxColors = maxColors.concat(colors[i]);
        }
    }

    // Figure out the losing turnHistory
    let maxNumber = 0;
    for (let turnHistory of lastTrickHistory.value) {
        if ((maxColors.indexOf(turnHistory.card || 0) != -1) && ((turnHistory.card || 0) > maxNumber)) {
            maxNumber = turnHistory.card || 0;
        }
    }

    return lastTrickHistory.value.find(turnHistory => turnHistory.card == maxNumber);
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

const canCheck = computed(() => {
    if (currentGame.value) {
        return (currentGame.value.is_betting_round && (currentGame.value.player_set.filter(player => player.bet > 0).length == 0));
    }
    return false;
})

function check() {
    post('games/check/', {}).then(() => {})
}

const canOpen = computed(() => {
    if (currentGame.value) {
        return (currentGame.value.is_betting_round && (currentGame.value.player_set.filter(player => player.bet > 0).length == 0));
    }
    return false;
})

function open() {
    post('games/open_betting/', {'bet': betAmount.value}).then(() => {})
}

const canFold = computed(() => {
    if (currentGame.value) {
        if (currentGame.value.player_set.filter(player => player.username == username.value)[0].fold) {
            return false;
        }
        return (currentGame.value.is_betting_round && (currentGame.value.player_set.filter(player => player.bet > 0).length > 0));
    }
    return false;
})

function fold() {
    post('games/fold/', {}).then(() => {})
}

const canCall = computed(() => {
    if (currentGame.value) {
        if (currentGame.value.player_set.filter(player => player.username == username.value)[0].fold) {
            return false;
        }
        return (currentGame.value.is_betting_round && (currentGame.value.player_set.filter(player => player.bet > 0).length > 0));
    }
    return false;
})

function call() {
    post('games/call/', {}).then(() => {})
}

const canRaise = computed(() => {
    if (currentGame.value) {
        if (currentGame.value.player_set.filter(player => player.username == username.value)[0].fold) {
            return false;
        }
        return (currentGame.value.is_betting_round && (currentGame.value.player_set.filter(player => player.bet > 0).length > 0));
    }
    return false;
})

function raise() {
    post('games/raise_bet/', {'bet': betAmount.value}).then(() => {})
}

const winners = computed(() => {
    /**
     * Returns a nicely formatted string containing the list of winners if the game is finished,
     * else returns an empty string
     */
    if (currentGame.value && currentGame.value.is_finished) {
        const winners = currentGame.value.winners
        let ret = currentGame.value.player_set.find(player => player.username == winners[0])?.name
        for  (let index in winners) {
            if (Number(index) > 0) {
                ret += `, ${currentGame.value.player_set.find(player => player.username == winners[index])?.name}`;
            }
        }
        return (ret && ret.length) ? ret : 'No one';
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

function startGame() {
    post('games/start_game/', {}).then(() => {})
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
    if (canPlay(cardNumber)) {
        activeCard.value = cardNumber;
    }
}

function playActiveCard() {
    post('cards/play/', {'number': activeCard.value || 0}).then(response => {
        response.json().then(responseJson => {
            if (response.status == 400) {
                error.value = responseJson;
            } else {
                error.value = '';
                activeCard.value = null;
            }
        })
    })
}

function continueGame() {
    post('games/continue_game/', {}).then(() => {})
}

function fontSize(value: string) {
    if (value.length <= 19) {
        return '';
    } else if (value.length <= 29) {
        return 'smallfont';
    } else {
        return 'tinyfont';
    }
}

function canPlay(cardNumber: number) {
    if (!currentGame.value) {
        return false;
    }
    if (!currentGame.value.player_set.find(player => player.username == username.value)?.is_turn) {
        return false;
    }
    if (currentGame.value.player_set.find(player => player.waiting_for_continue)) {
        return false;
    }
    if (currentGame.value.turn == 0) {
        if (cardNumber == 0) {
            return true;
        }
        return false;
    }
    const firstTurnOfTrick = Math.floor(currentGame.value.turn / currentGame.value.num_players) * currentGame.value.num_players;
    if (firstTurnOfTrick == currentGame.value.turn) {
        return true;
    }
    let playedColors: Array<number> = [];
    for (
        let turnHistory of currentGame.value.turnhistory_set.filter(turn_history => 
            (turn_history.hand == currentGame.value?.hand) && (turn_history.turn >= firstTurnOfTrick)
        )
    ) {
        const colors = [black, red, blue, brown, green, yellow, purple, gray]
        for (let color of colors) {
            if ((turnHistory.card != null) && color.indexOf(turnHistory.card) != -1) {
                playedColors = playedColors.concat(color);
            }
        }
    }
    let canPlayAnything = true;
    if (hand.value) {
        for (let handCard of hand.value) {
            if (playedColors.indexOf(handCard) != -1) {
                canPlayAnything = false;
                break;
            }
        }
        if (canPlayAnything) {
            return true;
        } else {
            if (playedColors.indexOf(cardNumber) != -1) {
                return true;
            }
        }
    }
    return false;
}

onBeforeUnmount(() => {
    stopSocket();
    if (currentGame.value && currentGame.value.is_finished) {
        post('games/leave_game/', {}).then(() => {
            currentGame.value = null;
        })
    }
});

getCurrentGame();

</script>

<template>
<div v-if="currentGame && !currentGame.is_started">
    <h2 class="center rye">WAITING FOR PLAYERS</h2>
    <div class="profiles">
        <div v-for="slot in currentGame.num_players" :key="slot">
            <div class="waiting-profile-pic-container" v-if="slot <= currentGame.player_set.length">
                <ProfilePicComponent
                    :background_color="currentGame.player_set[slot-1].background_color"
                    :shirt_color="currentGame.player_set[slot-1].shirt_color"
                    :skin_color="currentGame.player_set[slot-1].skin_color"
                    :hat_color="currentGame.player_set[slot-1].hat_color"
                ></ProfilePicComponent>
                <pre class="name" :class="fontSize(currentGame.player_set[slot-1].name || '')">{{ currentGame.player_set[slot-1].name }}</pre>
            </div>
            <div class="waiting-profile-pic-container" v-else>
                <div class="empty-slot">
                    <div class="empty-slot-inner">?</div>
                </div>
                <div class="name-placeholder"></div>
            </div>
        </div>
    </div>
    <div class="center" v-if="(currentGame.player_set.length  == currentGame.num_players)">
        <template v-if="username != currentGame.owner">
            Waiting for {{ currentGame.owner_name }} to start the game.
        </template>
        <div class="timeout-bar-container">
            <div class="timeout-bar" v-for="i in timeout" :key="i"></div>
        </div>
    </div>
    <div class="buttons-row buttons-row-center">
        <div class="button rye"
            v-if="username == currentGame.owner && (currentGame.num_players == currentGame.player_set.length)"
            @click="startGame()">START GAME</div>
    </div>
</div>
<div v-if="currentGame && currentGame.is_started">
    <div class="current-game-background">
        <template v-for="player in reorderedPlayerSet" :key="player.position">
            <div class="player-card-container">
                <div class="profile-pic-container" :class="player.is_turn ? '' : 'not-turn'">
                    <ProfilePicComponent
                        :background_color="player.background_color"
                        :shirt_color="player.shirt_color"
                        :skin_color="player.skin_color"
                        :hat_color="player.hat_color"
                        :small="true"
                    ></ProfilePicComponent>
                    <div class="name-container">
                        <pre class="name" :class="fontSize(player.name || '')">
                            {{ player.name }}
                        </pre>
                    </div>
                    <div class="score yellow-text rye">{{ player.tricks + player.score }} TRICK{{ player.tricks + player.score == 1 ? '' : 'S' }}</div>
                </div>
                <div class="player-play">
                    <template v-if="playersWaitingForContinue.length">
                        <CardComponent
                            v-if="lastTrickHistory.find(history => history.player == player.username)"
                            :number="lastTrickHistory.find(history => history.player == player.username)?.card"
                            :class="{active: lastTrickTaker?.card == lastTrickHistory.find(history => history.player == player.username)?.card}"
                        >
                        </CardComponent>
                        <div v-else class="card-placeholder"></div>
                    </template>
                    <template v-else>
                        <CardComponent
                            v-if="recentHistory.find(history => history.player == player.username)"
                            :number="recentHistory.find(history => history.player == player.username)?.card"
                        >
                        </CardComponent>
                        <div v-else class="card-placeholder"></div>
                    </template>
                </div>
            </div>
        </template>
    </div>
    <div class="pot" v-if="currentGame.betting">Pot: ${{ currentGame.pot }}</div>
    <div class="game-status center">
        <template v-if="currentGame.is_finished">
            Game over! {{ winners }} won!
        </template>
        <template v-else-if="playersWaitingForContinue.length">
            {{ currentGame.player_set.find(player => player.username == lastTrickTaker?.player)?.name }} took the trick!
            <br/>
            <template v-if="playersWaitingForContinue.length > 1">
                Waiting for {{ playersWaitingForContinue.length }} players to click continue...
            </template>
            <template v-else>
                Waiting for {{ currentGame.player_set.find(player => player.username == playersWaitingForContinue[0])?.name }} to click continue...
            </template>
        </template>
        <template v-else-if="currentGame.is_betting_round">
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn!</template>
            <template v-else>{{ currentGame.player_set.find(player => player.is_turn)?.name }}'s turn</template>
        </template>
        <template v-else-if="currentGame.turn == 0">
            <template v-if="!(hand?.includes(0))">Waiting for {{ currentGame.player_set.find(player => player.is_turn)?.name }} to play the 0...</template>
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn! You must play the 0</template>
        </template>
        <template v-else>
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn!</template>
            <template v-else>{{ currentGame.player_set.find(player => player.is_turn)?.name }}'s turn</template>
        </template>
    </div>
    <div class="buttons-row buttons-row-center" v-if="!currentGame.is_finished">
        <div class="button rye" v-if="playersWaitingForContinue.includes(username)" @click="continueGame()">CONTINUE</div>
        <template v-else-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">
            <template v-if="currentGame.is_betting_round">
                <form v-if="canOpen || canRaise">
                    <label for="betAmount">Amount to {{ canOpen ? 'Open With' : 'Raise To' }}: $</label>
                    <input id="betAmount" type="number" v-model="betAmount" :min="1" :max="currentGame.player_set.find(player => player.username == username)?.money">
                </form>
                <div class="button" v-if="canOpen" @click="open()">Open</div>
                <div class="button" v-if="canCheck" @click="check()">Check</div>
                <div class="button" v-if="canRaise" @click="raise()">Raise</div>
                <div class="button" v-if="canCall" @click="call()">Call</div>
                <div class="button" v-if="canFold" @click="fold()">Fold</div>
            </template>
            <div class="button rye" v-else-if="typeof activeCard == 'number'" @click="playActiveCard()">PLAY</div>
        </template>
        <div class="error center red-text" v-if="error">{{ error }}</div>
    </div>
    <div class="hand" v-if="hand">
        <CardComponent
            class="hand-card"
            :class="{
                active: cardNumber == activeCard,
                'cant-play': !canPlay(cardNumber)
            }"
            :id="'handCard' + cardNumber"
            :number="cardNumber"
            v-for="cardNumber in hand"
            :key="cardNumber"
            draggable="true"
            @dragstart="dragStart($event, cardNumber)"
            @dragenter="dragEnter($event)"
            @dragover="dragOver($event)"
            @drop="drop($event, cardNumber)"
            @click="activate(cardNumber)"
        ></CardComponent>
    </div>
</div>
</template>

<style scoped>

.not-turn {
    opacity: 0.5;
}

.timeout-bar-container {
    display: flex;
    justify-content: center;
}

.timeout-bar {
    width: 8px;
    height: 4px;
    background-color: var(--color-text);
}

.profiles {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
}

.waiting-profile-pic-container {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.profile-pic-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 80px;
}

.empty-slot {
    height: 100px;
    width: 100px;
    border: 2px dashed var(--color-text);
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
}

.empty-slot-inner {
    font-size: 50px;
    text-align: center;
    font-family: rye;
}
.player-card-container {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
}


@media (min-width: 360px) {

    .player-card-container {
        justify-self: end;
    }
    .player-card-container:nth-child(even) {
        flex-direction: row-reverse;
        justify-self: start;
    }

    .current-game-background {
        display: grid;
        grid-template-columns: 50% 50%;
        row-gap: 20px;
        column-gap: 8px;
    }
}

.name-placeholder {
    height: 1em;
}

.name-container {
    height: 25px;
    display: flex;
    align-items: center;
}

.card-placeholder {
    width: 70px;
    height: 90px;
}

.current-game-betting-round-background {
    background-color: var(--color-button-shadow);
    width: 100vw;
    height: 100%;
    display: grid;
    grid-template-columns: fit-content(200px) min-content;
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
    justify-content: center;
}

.hand-card {
    cursor: pointer;
}

.active {
    border: 4px solid var(--color-card-selected);
}

.cant-play {
    opacity: 0.5;
    cursor: auto;
}

input {
    padding: 4px;
    margin: 4px;
}

</style>