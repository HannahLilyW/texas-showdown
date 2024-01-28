<script setup lang="ts">
import router from '../router';
import { username, get } from '../services/api.js';
import { ref } from 'vue';
import type { Ref } from 'vue';
import type { Game } from '../models';

let currentGame: Ref<Game|null> = ref(null);
let loading: Ref<boolean> = ref(true);

function getCurrentGame() {
    if (username.value) {
        get('games/get_current_game/').then(response => {
            if (response.status == 204) {
                loading.value = false;
                return;
            }
            try {
                response.json().then(responseJson => {
                    if (response.status == 200) {
                        currentGame.value = responseJson;
                        loading.value = false;
                    } else {
                        console.log(`unexpected response. status: ${response.status} response: ${responseJson}`)
                    }
                })
            } catch (e) {
                console.log(`error getting current game: ${e}`)
            }
        })
    } else {
        loading.value = false;
    }
}

function playNow() {
    if (username.value) {
        if (!currentGame.value) {
            router.push('/join-existing-game');
        } else {
            router.push('/active-game');
        }
    } else {
        router.push('/edit-profile');
    }
}

function createNewGame() {
    router.push('/create-new-game');
}

function activeGame() {
    router.push('/active-game')
}

function joinExistingGame() {
    router.push('/join-existing-game');
}

function viewCompletedGames() {
    router.push('/view-completed-games');
}

function viewPlayerStatistics() {
    router.push('/view-player-statistics');
}

getCurrentGame();

</script>

<template>
    <nav>
        <div class="buttons-row buttons-row-center">
            <div class="button button-big rye" @click="playNow()">PLAY</div>
        </div>
    </nav>
    <div class="rules">
        <h1>Rules</h1>
        <p>
            Western Wager is a trick-taking card game. A trick-taking game is a game which consists of a certain number of rounds, or “tricks”, and each round has a winner who “takes the trick”. Western Wager is somewhat unusual among trick-taking games because the goal of the game is to take as few tricks as possible, and the winner of the game is the player that took the fewest tricks.
        </p>
        <h2>Creating the Game</h2>
        <p>
            A game can have three, four, five, or six players. The number of players is chosen by the creator of the game, and cannot be modified once the game has been created. A game can optionally include betting. If the creator of the game selects “High Stakes” on the game creation screen, the game will include betting. If the game creator selects “Just for Fun” on the game creation screen, the game will not include betting. Similar to the number of players, whether the game includes betting cannot be changed once the game has been created.
        </p>
        <h2>Joining and Starting the Game</h2>
        <p>
            Once the game has been created, any authenticated user that is not already in another game may join the game, until the required number of players have joined the game. Once the required number of players have joined, the owner of the game may start the game. Initially, the creator of the game is the owner of the game. If the creator of the game leaves the game before the game has started, then the next player still in the game that joined the earliest becomes the new owner of the game. During the time after the game has been created but before the game has been started, players may leave the game and other players may take their place. If all players leave a game before it has been started, that game is deleted from the database and does not show up in the list of completed games.
        </p>
        <h2>Dealing</h2>
        <p>
            Once the game is started, a 60-card deck consisting of the following cards is shuffled and evenly dealt into players’ hands:
        </p>
        <ul>
            <li>11 black cards numbered 0-10</li>
            <li>10 red cards numbered 11-20</li>
            <li>9 blue cards numbered 21-29</li>
            <li>8 brown cards numbered 31-38</li>
            <li>7 green cards numbered 41-47</li>
            <li>6 yellow cards numbered 51-56</li>
            <li>5 purple cards numbered 61-65</li>
            <li>4 gray cards numbered 71-74</li>
        </ul>
        <p>
            Since there are 60 cards, the deck can be evenly split between three, four, five, or six players. Players do not know the contents of other players’ hands, except that all players know which player received the 0 card.
        </p>
        <h2>Betting Round</h2>
        <p>
            Once the players have been dealt their initial cards, if the game includes betting, then a betting round commences. If the game does not include betting, this part is skipped. Each player is given $100 (in-game money, not real money) to bet with. The player who received the 0 card starts the betting. The order of play after that is determined by the order that the players joined the game. For example, in a three-player game, if the player who joined second received the zero card, then it would first be their turn, then the player who joined third, then the player who joined first.
        </p>
        <p>
            Betting is handled somewhat similarly to poker: the owner of the game may either “check” (which means they do not place a bet), or “open” (which means they bet some amount of money). If the owner of the game chose to check, then the next player may also either check or open. Until someone opens, each player may either check or open. If all of the players check, then the betting round ends with no money on the table. Once a player opens, then the next player must either “fold” (which means they are skipped for the rest of the betting round), “call” (which means they match the highest bet which was made so far), or “raise” (which means they increase their bet amount to higher than the previous highest bet). Each subsequent player must either fold, call, or raise until every player has either folded or bet the same amount. Players who have previously folded are skipped. Once all players who have not folded have bet the same amount, the betting round ends. Each player’s bet is transferred into the pot.
            If any player quits at any point during the betting round, or takes more than 60 seconds to take their turn, the game immediately ends, and that player loses. The remaining players win the game and evenly split the total amount that has been bet so far.
        </p>
        <h2>Hand</h2>
        <p>
            Once the betting round is finished (if there was a betting round), then the first hand begins. Hands consist of multiple tricks. For each trick, each player plays one card from their hand. The loser of the trick “takes the trick”.
        </p>
        <p>
            The player who has the 0 goes first by playing the 0. If the next player has a black card in their hand, they must play a black card. Otherwise, they can play any card in their hand. If the next player has any card in their hand which is the same color as a card that has already been played, they must play that card. Otherwise, they can play any card in their hand. Play continues like this until all players have played a card.
            The player who played the highest-numbered card of the color which was played the most times takes the trick. For example, in a three-player game, if the cards 0 (black), 11 (red), and 2 (black) were played, then the player who played the 2 would take the trick since black was the most-played color, and 2 was the highest black card played.
        </p>
        <p>
            The player who took the trick goes first in the next trick. They can play any card in their hand. The next player must play a card of the same color if they have it, otherwise they too can play any card in their hand. Play continues like this until there are no more cards in the players’ hands. Once all the players are out of cards, the hand is over.
            If any player quits, or takes more than 60 seconds to take their turn, the game immediately ends. The player that took too long loses, and the remaining players win.
        </p>
        <h2>Subsequent Rounds and End of Game</h2>
        <p>
            Once a hand is over, if betting is enabled, the player who took the least tricks that hand gets all the money in the pot. If multiple players tied for the least amount of tricks taken, they split the pot. The exception is that if one of those players had folded in the last betting round, they do not get any money from the pot. If every winner of the hand folded, then the money stays in the pot and is given to the winner(s) of the next hand. If there is no money in the pot and only one player has all the money, then the game is over and the player with all the money wins. Otherwise, a new betting round commences, followed by a new hand. Gameplay continues like this until only one player has all the money.
        </p>
        <p>
            Otherwise, when a hand is over and betting is not enabled, the game is over if any player has taken more than 10 tricks in the entire game so far. The winner is the player that took the least total tricks. If there is a tie, each player who took the least tricks wins.
        </p>
    </div>
</template>

<style scoped>

nav {
    margin-top: 40px;
}

p, h1, h2, .rules {
    margin: 4px;
    padding: 4px;
}
</style>