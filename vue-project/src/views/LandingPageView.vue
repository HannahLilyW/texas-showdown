<script setup lang="ts">
import router from '../router';
import { username } from '../api.js';

function createAccount() {
  router.push('/create-account');
}

function logIn() {
  router.push('/login');
}

function startNewGame() {

}

function joinExistingGame() {

}

function viewCompletedGames() {

}

function viewPlayerStatistics() {

}

</script>

<template>
  <nav>
    <div v-if="username" class="buttons-column">
      <button class="button" @click="startNewGame()">
          Start New Game
      </button>
      <button class="button" @click="joinExistingGame()">
          Join Existing Game
      </button>
      <button class="button" @click="viewCompletedGames()">
          View Completed Games
      </button>
      <button class="button" @click="viewPlayerStatistics()">
          View Player Statistics
      </button>
    </div>
    <div v-else class="buttons-row">
        <div class="button" @click="createAccount()">
          Create Account
        </div>
        <div class="button" @click="logIn()">
          Log In
        </div>
    </div>
  </nav>
</template>

<style scoped>
</style>