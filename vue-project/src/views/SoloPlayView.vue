<script setup lang="ts">
import type { Player, Game, Card } from '../models';
import { ref, watch, computed } from 'vue';
import type { Ref } from 'vue';
import { randomName, randomColor } from '../services/fake.js';
import { name, background_color, shirt_color, skin_color, hat_color } from '../services/api.js';
import CardComponent from '../components/CardComponent.vue';
import ProfilePicComponent from '../components/ProfilePicComponent.vue';
import '../assets/game.css';

// Form data
let numPlayers: Ref<string> = ref("3");

const reorderedPlayerSet: Ref<Player[]> = ref([]);

let cards: Card[] = [];
const hand: Ref<number[]> = ref([]);

let activeCard: Ref<number|null> = ref(null);

const initGame: Game = {
    id: 0,
    created: new Date(),
    created_by: '',
    num_players: 3,
    pot: 0,
    is_started: false,
    owner: '',
    owner_name: '',
    player_set: [],
    turn: 0,
    hand: 1,
    buy_in: 0,
    turnhistory_set: [],
    is_finished: false,
    winners: [],
    last_timer_reset: new Date(),
    is_private: true
};

const currentGame: Ref<Game> = ref(JSON.parse(JSON.stringify(initGame)));

const initDeck = [
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
    11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
    21, 22, 23, 24, 25, 26, 27, 28, 29,
    31, 32, 33, 34, 35, 36, 37, 38,
    41, 42, 43, 44, 45, 46, 47,
    51, 52, 53, 54, 55, 56,
    61, 62, 63, 64, 65,
    71, 72, 73, 74
];

const maxCardsInSuit = [10, 20, 29, 38, 47, 56, 65, 74];

function createNewGame() {
    currentGame.value.num_players = parseInt(numPlayers.value);
    const youPlayer: Player = {
        username: 'You',
        name: name.value || 'You',
        background_color: background_color.value,
        shirt_color: shirt_color.value,
        skin_color: skin_color.value,
        hat_color: hat_color.value,
        position: 0,
        is_turn: false,
        choose_turn: false,
        waiting_for_continue: false,
        tricks: 0,
        score: 0,
        money: 0
    }
    currentGame.value.player_set.push(youPlayer);
    for (let i = 0; i < (currentGame.value.num_players - 1); i++) {
        const newPlayer: Player = {
            username: 'fake' + i.toString(),
            name: randomName(),
            background_color: randomColor(),
            shirt_color: randomColor(),
            skin_color: randomColor(),
            hat_color: randomColor(),
            position: i + 1,
            is_turn: false,
            choose_turn: false,
            waiting_for_continue: false,
            tricks: 0,
            score: 0,
            money: 0
        }
        currentGame.value.player_set.push(newPlayer);
    }
    let deck = JSON.parse(JSON.stringify(initDeck));
    let shuffledDeck = [];
    for (let i = 0; i < initDeck.length; i++) {
        const cardIndex = Math.floor(Math.random()*deck.length);
        const cardNum = deck[cardIndex];
        deck.splice(cardIndex, 1);
        shuffledDeck.push(cardNum);
        const playerReceivingCard = currentGame.value.player_set.filter(player => player.position == i % currentGame.value.num_players)[0];
        cards.push({
            player: playerReceivingCard.username,
            number: cardNum
        });
        if (cardNum == 0) {
            currentGame.value.player_set.filter(player => player.position == i % currentGame.value.num_players)[0].is_turn = true;
        }
    }
    currentGame.value.is_started = true;
    autoplay()
}

function getReorderedPosition(originalPosition: number) {
    if (window.screen.width < 360) {
        return originalPosition;
    }
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
    return originalPosition;
}

function canPlay(cardNumber: number, username: string) {
    if (!currentGame.value) {
        return false;
    }
    if (!currentGame.value.player_set.find(player => player.username == username)?.is_turn) {
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
    for (let handCard of cards.filter(card => card.player == username)) {
        if (playedColors.indexOf(handCard.number) != -1) {
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
    return false;
}

function activate(cardNumber: number) {
    if (canPlay(cardNumber, 'You')) {
        activeCard.value = cardNumber;
    }
}

function playCard(cardNumber: number) {
    const card = cards.find(c => c.number == cardNumber)
    if (!card) {
        throw new Error('something went very wrong');
    }

    const currentPlayer = card.player

    // Create the TurnHistory
    currentGame.value.turnhistory_set.push({
        turn: currentGame.value.turn,
        hand: currentGame.value.hand,
        player: card.player,
        card: card.number,
        end_game: false
    })

    // Update the game state
    if (currentGame.value.turn < 59) {
        currentGame.value.turn += 1
    } else {
        currentGame.value.turn = 0
        currentGame.value.hand += 1
    }

    // Remove the card from this player's hand
    cards.find(c => c.number == cardNumber)!.player = ''

    // Make it the next player's turn
    currentGame.value.player_set.find(player => player.username == currentPlayer)!.is_turn = false;

    const firstTurnOfTrick = Math.floor(currentGame.value.turn / currentGame.value.num_players) * currentGame.value.num_players;
    const isFirstTurnOfTrick = firstTurnOfTrick == currentGame.value.turn;
    if (currentGame.value.turn == 0) {
        // The next turn is the first turn of the hand.

        const firstTurnOfLastTrick = 60 - currentGame.value.num_players;
        const turnHistoriesInLastTrick = currentGame.value.turnhistory_set.filter(th => (th.hand == (currentGame.value.hand - 1)) && (th.turn >= firstTurnOfLastTrick));

        // Figure out which color(s) occured the most times
        let colorFrequencies = [0, 0, 0, 0, 0, 0, 0, 0];
        const colors = [black, red, blue, brown, green, yellow, purple, gray];
        for (let turnHistory of turnHistoriesInLastTrick) {
            for (let i = 0; i < colors.length; i++) {
                if (colors[i].indexOf(turnHistory.card!) > -1) {
                    colorFrequencies[i] += 1
                }
            }
        }
        let maxColors: number[] = []
        for (let i = 0; i < colorFrequencies.length; i++) {
            if (colorFrequencies[i] == Math.max(...colorFrequencies)) {
                maxColors = maxColors.concat(colors[i])
            }
        }

        // For cards played in that (those) color(s), figure out which card had the highest number
        let maxNumber = 0
        for (let turnHistory of turnHistoriesInLastTrick) {
            if ((maxColors.indexOf(turnHistory.card!) > -1) && (turnHistory.card! > maxNumber)) {
                maxNumber = turnHistory.card!
            }
        }

        const playerTakingTrick = turnHistoriesInLastTrick.find(th => th.card == maxNumber)!.player
        currentGame.value.player_set.find(player => player.username == playerTakingTrick)!.tricks += 1;

        // Transfer the tricks taken this round to each player's score.
        // Determine if the game is finished.
        for (let otherPlayer of currentGame.value.player_set) {
            currentGame.value.player_set.find(player => player.username == otherPlayer.username)!.score += otherPlayer.tricks
            currentGame.value.player_set.find(player => player.username == otherPlayer.username)!.tricks = 0
            if (currentGame.value.player_set.find(player => player.username == otherPlayer.username)!.score >= 10) {
                currentGame.value.is_finished = true;
            }
        }

        if (currentGame.value.is_finished) {
            // Figure out the winner(s) of the game

            // Find the lowest score
            const lowestScore = currentGame.value.player_set.sort((a, b) => a.score - b.score)[0].score

            // Get all players with the lowest score. These players are the winners.
            for (let otherPlayer of currentGame.value.player_set.filter(player => (player.score == lowestScore))) {
                currentGame.value.winners.push({
                    username: otherPlayer.username,
                    name: otherPlayer.name || ''
                })
            }

            // Don't give players new cards if game is finished.
            return;
        }

        let deck = JSON.parse(JSON.stringify(initDeck));
        let shuffledDeck = [];
        cards = [];
        for (let i = 0; i < initDeck.length; i++) {
            const cardIndex = Math.floor(Math.random()*deck.length);
            const cardNum = deck[cardIndex];
            deck.splice(cardIndex, 1);
            shuffledDeck.push(cardNum);
            const playerReceivingCard = currentGame.value.player_set.filter(player => player.position == i % currentGame.value.num_players)[0];
            cards.push({
                player: playerReceivingCard.username,
                number: cardNum
            });
            if (cardNum == 0) {
                currentGame.value.player_set.filter(player => player.position == i % currentGame.value.num_players)[0].is_turn = true;
            }
        }

        // Wait for human to click continue, to ensure they see the results of the trick that just finished.
        currentGame.value.player_set.find(player => (player.username == 'You'))!.waiting_for_continue = true;
    } else if (isFirstTurnOfTrick) {
        // The next turn is the first turn of the trick, but not the first turn of the hand.
        // Analyze the last trick to figure out who goes first in this trick.
        const firstTurnOfLastTrick = firstTurnOfTrick - currentGame.value.num_players;
        const turnHistoriesInLastTrick = currentGame.value.turnhistory_set.filter(th => (
            (th.hand == currentGame.value.hand) && (th.turn < firstTurnOfTrick) && (th.turn >= firstTurnOfLastTrick)
        ));

        // Figure out which color(s) occured the most times
        let colorFrequencies = [0, 0, 0, 0, 0, 0, 0, 0]
        const colors = [black, red, blue, brown, green, yellow, purple, gray];
        for (let turnHistory of turnHistoriesInLastTrick) {
            for (let i = 0; i < colors.length; i++) {
                if (colors[i].indexOf(turnHistory.card!) > -1) {
                    colorFrequencies[i] += 1
                }
            }
        }
        let maxColors: number[] = []
        for (let i = 0; i < colorFrequencies.length; i++) {
            if (colorFrequencies[i] == Math.max(...colorFrequencies)) {
                maxColors = maxColors.concat(colors[i])
            }
        }

        // For cards played in that (those) color(s), figure out which card had the highest number
        let maxNumber = 0
        for (let turnHistory of turnHistoriesInLastTrick) {
            if ((maxColors.indexOf(turnHistory.card!) > -1) && (turnHistory.card! > maxNumber)) {
                maxNumber = turnHistory.card!
            }
        }

        const playerTakingTrick = turnHistoriesInLastTrick.find(th => th.card == maxNumber)!.player

        let chooseNextPlayer = false
        for (let turnHistory of turnHistoriesInLastTrick) {
            if (maxCardsInSuit.indexOf(turnHistory.card!) > -1) {
                chooseNextPlayer = true
            }
        }
        if (chooseNextPlayer) {
            // If there were any highest cards of suit played, player gets to choose who goes next.
            currentGame.value.player_set.find(player => player.username == playerTakingTrick)!.choose_turn = true
        } else {
            // Otherwise it's their turn.
            currentGame.value.player_set.find(player => player.username == playerTakingTrick)!.is_turn = true
        }
        currentGame.value.player_set.find(player => player.username == playerTakingTrick)!.tricks += 1

        // Wait for human to click continue, to ensure they see the results of the trick that just finished.
        currentGame.value.player_set.find(player => (player.username == 'You'))!.waiting_for_continue = true
    } else {
        // The next turn is not the first turn of the trick.
        // The next player is the one with position (current_player.position + 1) % num_players
        const currentPlayerPosition = currentGame.value.player_set.find(player => player.username == currentPlayer)!.position
        currentGame.value.player_set.find(player => player.position == ((currentPlayerPosition + 1) % currentGame.value.num_players))!.is_turn = true
    }
    autoplay()
}

let autoplayTimeoutId: any = undefined;

function autoplay() {
    if (typeof autoplayTimeoutId == 'number') {
        clearTimeout(autoplayTimeoutId);
    }
    autoplayTimeoutId = setTimeout(() => {
        if (currentGame.value.is_finished) {
            return;
        }
    
        let humanPlayer = currentGame.value.player_set.find(player => player.username == 'You')!
    
        if (humanPlayer.waiting_for_continue || humanPlayer.is_turn || humanPlayer.choose_turn) {
            return;
        }
    
        if (currentGame.value.player_set.find(player => player.choose_turn)) {
            currentGame.value.player_set.find(player => player.choose_turn)!.choose_turn = false;
            currentGame.value.player_set[Math.floor(Math.random()*currentGame.value.player_set.length)].is_turn = true;
            autoplay();
            return;
        }

        const usernameToPlay = currentGame.value.player_set.find(player => player.is_turn)!.username
    
        for (let card of cards.filter(c => c.player == usernameToPlay)) {
            if (canPlay(card.number, usernameToPlay)) {
                playCard(card.number)
                return;
            }
        }
    }, 2000)
}

function playAgain() {
    cards = [];
    activeCard.value = null;
    currentGame.value = JSON.parse(JSON.stringify(initGame));
    if (typeof autoplayTimeoutId == 'number') {
        clearTimeout(autoplayTimeoutId);
    }
}

function playActiveCard() {
    playCard(activeCard.value || 0);
    activeCard.value = null;
}

function getHand() {
    hand.value = cards.filter(
        card => card.player == 'You'
    ).map(
        card => card.number
    ).sort(
        (a: number, b: number) => {return a-b}
    );
    if (hand.value && activeCard.value && !hand.value.includes(activeCard.value)) {
        activeCard.value = null;
    }
}

watch(currentGame, (newVal) => {
    reorderedPlayerSet.value = [];
    for (let player of newVal.player_set) {
        let playerClone = JSON.parse(JSON.stringify(player));
        playerClone.position = getReorderedPosition(playerClone.position);
        reorderedPlayerSet.value.push(playerClone);
    }
    reorderedPlayerSet.value.sort((a, b) => {
        return a.position - b.position;
    });
    getHand();
}, {deep: true})

function shouldDefocusPlayer(player: Player) {
    const me = currentGame.value?.player_set.find(p => p.username == 'You')
    if (me?.choose_turn && !me?.waiting_for_continue) {
        return false;
    }
    if (player.is_turn || player.choose_turn) {
        return false;
    }
    return true;
}

function shouldShowPlayerButtons() {
    return !!currentGame.value?.player_set.find(player => player.username == 'You')?.choose_turn && !currentGame.value?.player_set.find(player => player.waiting_for_continue);
}

function chooseTurn(player: Player) {
    if (currentGame.value.player_set.find(p => p.username == 'You')!.choose_turn) {
        currentGame.value.player_set.find(p => p.username == 'You')!.choose_turn = false
        currentGame.value.player_set.find(p => p.username == player.username)!.is_turn = true
        autoplay()
    }
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

const playersWaitingForContinue = computed(() => {
    /**
     * Returns the usernames for the users we are waiting on to click continue
     */
    if (currentGame.value) {
        return currentGame.value.player_set.filter(player => player.waiting_for_continue).map(player => player.username);
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

const black = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const red = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20];
const blue = [21, 22, 23, 24, 25, 26, 27, 28, 29];
const brown = [31, 32, 33, 34, 35, 36, 37, 38];
const green = [41, 42, 43, 44, 45, 46, 47];
const yellow = [51, 52, 53, 54, 55, 56];
const purple = [61, 62, 63, 64, 65];
const gray = [71, 72, 73, 74];

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

function continueGame() {
    currentGame.value.player_set.find(player => player.username == 'You')!.waiting_for_continue = false;
    autoplay()
}



</script>

<template>
<div v-if="!currentGame.is_started">
    <h2 class="center rye">SINGLE PLAYER</h2>
    <br/>
    <form class="form-center">
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
    </form>
    <br/>
    <div class="buttons-row buttons-row-center">
        <div class="button rye" @click="createNewGame()">START GAME</div>
    </div>
</div>
<div v-else>
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
        </template>
        <template v-else-if="currentGame.turn == 0">
            <template v-if="!(hand?.includes(0))">Waiting for {{ currentGame.player_set.find(player => player.is_turn)?.name }} to play the 0...</template>
            <template v-if="(currentGame.player_set.find(player => player.username == 'You')?.is_turn)">Your turn! You must play the 0</template>
        </template>
        <template v-else-if="currentGame.player_set.find(player => player.is_turn)">
            <template v-if="(currentGame.player_set.find(player => player.username == 'You')?.is_turn)">Your turn!</template>
            <template v-else>{{ currentGame.player_set.find(player => player.is_turn)?.name }}'s turn</template>
        </template>
        <template v-else-if="currentGame.player_set.find(player => player.choose_turn)">
            <template v-if="(currentGame.player_set.find(player => player.username == 'You')?.choose_turn)">
                Choose who goes first next!
            </template>
            <template v-else>Waiting for {{ currentGame.player_set.find(player => player.choose_turn)?.name }} to choose who goes first next...</template>
        </template>
    </div>
    <div id="playActionButtonsContainer">
        <div class="buttons-row buttons-row-center" v-if="!currentGame.is_finished">
            <div class="button rye" v-if="playersWaitingForContinue.includes('You')" @click="continueGame()">CONTINUE</div>
            <template v-else-if="(currentGame.player_set.find(player => player.username == 'You')?.is_turn)">
                <div class="button rye" v-if="typeof activeCard == 'number'" @click="playActiveCard()">PLAY</div>
            </template>
            <template v-else-if="(currentGame.player_set.find(player => player.username == 'You')?.choose_turn)">
            </template>
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
                'cant-play': !canPlay(cardNumber, 'You')
            }"
            :id="'handCard' + cardNumber"
            :number="cardNumber"
            v-for="cardNumber in hand"
            :key="cardNumber"
            @click="activate(cardNumber)"
        ></CardComponent>
    </div>
</div>
</template>