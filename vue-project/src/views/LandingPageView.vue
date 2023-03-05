<script setup lang="ts">
import router from '../router'

function createAccount() {
  router.push('/create-account');
}

function logIn() {
  router.push('/login');
}

</script>

<template>
  <nav>
    <div class="buttons-row">
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