<script setup lang="ts">
    let text: string = "";
</script>

<template>
    <header>
        Log In
    </header>
    <form>
        <label for="username">Username:</label>
        <input id="username" v-model="text" placeholder="username goes here">
    </form>
</template>

<style scoped>
</style>