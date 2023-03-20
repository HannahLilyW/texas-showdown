<script setup lang="ts">
import router from './router';
import { RouterView } from 'vue-router'
import { username, logout } from './services/api.js';

if (!username.value) {
  // Stop people from accidentally going to a page they need to be logged in for, before logging in
  router.push('/');
}

function goToLanding() {
  router.push('/');
}

</script>

<template>
  <header>
    <div class="title-wrapper">
      <img alt="Flag of Texas" class="logo point" src="@/assets/flag64.png" width="64" height="43" @click="goToLanding()"/>
      <div id="title" class="point" @click="goToLanding()">
        TEXAS SHOWDOWN
      </div>
    </div>
    <div class="user-info" v-if="username">
      <div>
        Welcome, {{ username }}
      </div>
      <div class="button" @click="logout()">Log Out</div>
    </div>
  </header>

  <div class="container">
    <RouterView />
  </div>
</template>

<style scoped>

header {
  display: flex;
  justify-content: space-between;
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
