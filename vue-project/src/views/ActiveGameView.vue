<script setup lang="ts">
import { get, post, startSocket, stopSocket, currentGame, hand, username, unread, leaveGame } from '../services/api.js';
import type { Player } from '../models';
import { watch, ref, onBeforeUnmount, computed } from 'vue';
import type { Ref } from 'vue';
import router from '../router';
import CardComponent from '../components/CardComponent.vue';
import ProfilePicComponent from '../components/ProfilePicComponent.vue';
import ChatIcon from '../components/icons/IconChat.vue';
import ChatComponent from '../components/ChatComponent.vue';
import '../assets/game.css';

let chat = ref();

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
let roomCode: Ref<string> = ref('');

const timeout: Ref<number> = ref(0);
let timerStarted = false;

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
        && ((oldVal && !(oldVal.player_set.length  == oldVal.num_players)) || !oldVal)
        && !newVal.is_started
        && (newVal.player_set.length  == newVal.num_players)
    ) {
        // start the timer
        const secondsSinceServerTimeReset = Math.floor((new Date().getTime() - new Date(newVal.last_timer_reset).getTime()) / 1000);
        resetTimer(30 - secondsSinceServerTimeReset);
    } else if (
        newVal
        && newVal.is_started
        && (newVal.last_timer_reset)
    ) {
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
    if (newVal && !roomCode.value && newVal.is_private) {
        get('games/get_room_code/').then(response => {
            response.json().then(responseJson => {
                roomCode.value = responseJson['room_code'];
            })
        })
    }
    getHand();
})

function decrementTimer() {
    if (timeout.value > 0) {
        timeout.value -= 1;
        timerStarted = true;
        setTimeout(decrementTimer, 1000);
    } else {
        timerStarted = false;
        if (currentGame.value?.is_finished) {
            router.push('/');
        }
    }
}

function resetTimer(seconds: number) {
    if (seconds > 0) {
        timeout.value = seconds;
        if (!timerStarted) {
            timerStarted = true;
            setTimeout(decrementTimer, 1000);
        }
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

const winners = computed(() => {
    /**
     * Returns a nicely formatted string containing the list of winners if the game is finished,
     * else returns an empty string
     */
    if (currentGame.value && currentGame.value.is_finished) {
        const tempWinners = currentGame.value.winners;
        let ret = currentGame.value.winners[0].name;
        for (let index in tempWinners) {
            if (Number(index) > 0) {
                ret += `, ${currentGame.value.winners[index].name}`;
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

function playAgain() {
    leaveGame(() => {
        router.push('/join-existing-game');
    })
}

function shouldDefocusPlayer(player: Player) {
    const me = currentGame.value?.player_set.find(p => p.username == username.value)
    if (me?.choose_turn && !me?.waiting_for_continue) {
        return false;
    }
    if (player.is_turn || player.choose_turn) {
        return false;
    }
    return true;
}

function shouldShowPlayerButtons() {
    return !!currentGame.value?.player_set.find(player => player.username == username.value)?.choose_turn && !currentGame.value?.player_set.find(player => player.waiting_for_continue);
}

function chooseTurn(player: Player) {
    if (currentGame.value?.player_set.find(p => p.username == username.value)?.choose_turn) {
        post('players/choose_turn/', {'username': player.username}).then(() => {});
    }
}

function openChat() {
    chat.value.show();
}

const phonetic: {[letter: string]: string} = {
    'A': 'ALPHA',
    'B': 'BRAVO',
    'C': 'CHARLIE',
    'D': 'DELTA',
    'E': 'ECHO',
    'F': 'FOXTROT',
    'G': 'GOLF',
    'H': 'HOTEL',
    'I': 'INDIA',
    'J': 'JULIET',
    'K': 'KILO',
    'L': 'LIMA',
    'M': 'MIKE',
    'N': 'NOVEMBER',
    'O': 'OSCAR',
    'P': 'PAPA',
    'Q': 'QUEBEC',
    'R': 'ROMEO',
    'S': 'SIERRA',
    'T': 'TANGO',
    'U': 'UNIFORM',
    'V': 'VICTOR',
    'W': 'WHISKEY',
    'X': 'X-RAY',
    'Y': 'YANKEE',
    'Z': 'ZULU'
}

onBeforeUnmount(() => {
    stopSocket();
    if (currentGame.value && (currentGame.value.is_finished || !currentGame.value.is_started)) {
        leaveGame();
    }
});

getCurrentGame();

</script>

<template>
<div v-if="currentGame && !currentGame.is_started">
    <h2 class="center rye">WAITING FOR PLAYERS</h2>
    <div v-if="currentGame.is_private">
        <div class="buttons-row buttons-row-center">
            <div class="room-code-container">
                <div class="center rye">ROOM CODE:</div>
                <div class="room-code">
                    <div class="rye room-code-letter" v-for="letter in roomCode" :key="letter">
                        {{ letter }}
                    </div>
                    <div class="rye room-code-phonetic" v-for="letter in roomCode" :key="letter">
                        {{ phonetic[letter] }}
                    </div>
                </div>
            </div>
        </div>
    </div>
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
                <div class="profile-pic-container" :class="{
                    'defocus': shouldDefocusPlayer(player),
                    'button': shouldShowPlayerButtons()
                }" @click="chooseTurn(player)">
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
                    <template v-if="playersWaitingForContinue.length || currentGame.is_finished">
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
        <template v-else-if="currentGame.turn == 0">
            <template v-if="!(hand?.includes(0))">Waiting for {{ currentGame.player_set.find(player => player.is_turn)?.name }} to play the 0...</template>
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn! You must play the 0</template>
        </template>
        <template v-else-if="currentGame.player_set.find(player => player.is_turn)">
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">Your turn!</template>
            <template v-else>{{ currentGame.player_set.find(player => player.is_turn)?.name }}'s turn</template>
        </template>
        <template v-else-if="currentGame.player_set.find(player => player.choose_turn)">
            <template v-if="(currentGame.player_set.find(player => player.username == username)?.choose_turn)">
                Choose who goes first next!
            </template>
            <template v-else>Waiting for {{ currentGame.player_set.find(player => player.choose_turn)?.name }} to choose who goes first next...</template>
        </template>
    </div>
    <div class="timeout-bar-container">
        <div class="timeout-bar" v-for="i in timeout" :key="i"></div>
    </div>
    <div id="playActionButtonsContainer">
        <div class="buttons-row buttons-row-center" v-if="!currentGame.is_finished">
            <div class="button rye" v-if="playersWaitingForContinue.includes(username)" @click="continueGame()">CONTINUE</div>
            <template v-else-if="(currentGame.player_set.find(player => player.username == username)?.is_turn)">
                <div class="button rye" v-if="typeof activeCard == 'number'" @click="playActiveCard()">PLAY</div>
            </template>
            <template v-else-if="(currentGame.player_set.find(player => player.username == username)?.choose_turn)">
            </template>
            <div class="error center red-text" v-if="error">{{ error }}</div>
        </div>
        <div class="buttons-row buttons-row-center" v-else>
            <div class="button rye" @click="playAgain()">PLAY AGAIN</div>
        </div>
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
<div class="chat-placeholder"></div>
<div class="buttons-row fixed-bottom">
    <div class="chat-button button" @click="openChat()">
        <ChatIcon></ChatIcon>
        <div class="unread-dot" v-if="unread"></div>
    </div>
</div>
<ChatComponent ref="chat"></ChatComponent>
</template>

<style scoped>

.unread-dot {
    height: 12px;
    width: 12px;
    border-radius: 50%;
    background-color: var(--color-card-yellow);
    position: absolute;
    left: 40px;
    top: 10px;
}

.chat-placeholder {
    height: 60px;
}

.room-code-container {
    background-color: var(--color-background-dark);
    padding: 8px;
    margin: 8px;
    border-radius: 8px;
}

.room-code {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    justify-items: center;
    column-gap: 4px;
}

.room-code-letter {
    font-size: 40px;
}

.room-code-phonetic {
    font-size: 10px;
}

</style>