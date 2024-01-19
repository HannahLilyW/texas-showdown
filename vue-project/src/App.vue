<script setup lang="ts">
import router from './router';
import { RouterView } from 'vue-router'
import { username, logout } from './services/api.js';
import SkullIcon from './components/icons/IconSkull.vue';

if (!username.value) {
  // Stop people from accidentally going to a page they need to be logged in for, before logging in
  router.push('/');
}

function goToLanding() {
  router.push('/');
}

function createAccount() {
    router.push('/create-account');
}

function logIn() {
    router.push('/login');
}

</script>

<template>
  <header>
    <div class="title-wrapper">
      <SkullIcon class="point" @click="goToLanding()"></SkullIcon>
      <div id="title" class="point" @click="goToLanding()">
        WESTERN WAGER
      </div>
    </div>
    <div class="user-info" v-if="username">
      <div>
        Welcome, {{ username }}
      </div>
      <div class="button" @click="logout()">Log Out</div>
    </div>
    <div v-else class="buttons-row">
      <div class="subtle-button" @click="createAccount()">
        Create Account
      </div>
      <div class="subtle-button" @click="logIn()">
        Log In
      </div>
    </div>
  </header>

  <div class="container">
    <RouterView />
  </div>
</template>

<style scoped>
header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  background-color: var(--color-background-dark);
  box-shadow: 0 0 100px 60px rgba(0, 0, 0, 0.5);
}

.user-info {
  display: flex;
  justify-content: end;
  align-items: center;
}

.title-wrapper {
  display: flex;
  align-items: center;
  padding: 8px;
}

#title {
  font-size: 32px;
  padding-left: 8px;
}
</style>
