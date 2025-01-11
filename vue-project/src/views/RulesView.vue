<script setup lang="ts">
import CardComponent from '../components/CardComponent.vue';
</script>

<template>
    <div class="rules">
        <h2 class="center rye">HOW TO PLAY</h2>
        <p class="center">
            Western Wager is a trick-taking game where the goal is to take the <b>LEAST</b> tricks.
        </p>
        <p class="center">
            To start, the following deck of 60 cards is evenly dealt between players:
        </p>
        <img src="../assets/images/deck.jpg" width="250px"/>
        <br>
        <p class="center">The circled number at the top left is how many cards are in the suit. The meter on the left shows how high the card is in the suit.</p>
        <div class="buttons-row buttons-row-center">
            <p>Whoever was dealt</p>
            <CardComponent :number="0"></CardComponent>
            <p>goes first. They must play</p>
            <CardComponent :number="0"></CardComponent>
            <p>to start.</p>
        </div>
        <br>
        <img src="../assets/images/GameplayScreenshot1.jpg" width="250px">
        <p class="center">Play continues counterclockwise. So in this example game, Brandon goes next.</p>
        <p class="center"><b>On your turn, you must play a card that is the same color as a card that has already been played, if possible.</b></p>
        <p class="center">If you don't have any, you can play any color card.</p>
        <p class="center">So if Brandon has any black (pistol) cards, he HAS to play one of them. Otherwise, he can play anything. Brandon does have black (pistol) cards, so he plays one.</p>
        <img src="../assets/images/GameplayScreenshot2.jpg" width="250px">
        <p class="center">Once everyone has played a card, the person who played the <b>highest-ranked card of the most-played color</b> takes the trick.</p>
        <img src="../assets/images/GameplayScreenshot3.jpg" width="250px">
        <p class="center">So in the above example round, Hannah takes the trick because everyone played black (pistol) cards, and she played the highest-ranked black (pistol) card.</p>
        <img src="../assets/images/GameplayScreenshot4.jpg" width="250px">
        <p class="center">But in this above example, Brandon takes the trick because more blue (hat) cards were played than purple (wheel).</p>
        <img src="../assets/images/GameplayScreenshot5.jpg" width="250px">
        <p class="center">If there's a tie for most played color as above, the player who played the highest-ranked card takes the trick.</p>
        <p class="center">The player who took the trick generally opens the next trick, with one exception: If you take a trick containing the highest-ranked card of a suit, you get to choose who opens the trick.</p>
        <p class="center">You can play any card when opening a trick.</p>
        <p class="center">Once everyone has played all the cards in their hand, a new hand begins if no one has taken 10 tricks yet.</p>
        <p class="center">The game ends at the end of a hand where someone has taken 10 or more tricks. Whoever took the <b>LEAST</b> tricks wins. If there's a tie, all tied players win.</p>
    </div>
</template>

<style scoped>

p, h1, h2, .rules {
    margin: 4px;
    padding: 4px;
}

.rules {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
}

p {
    max-width: 800px;
}

</style>
