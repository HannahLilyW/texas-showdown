<script setup lang="ts">
import { get, startSocket, stopSocket, currentGame } from '../services/api.js';
import { ref, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue';

let loading: Ref<boolean> = ref(true);

function getCurrentGame() {
    get('games/get_current_game/').then(response => {
        if (response.status == 204) {
            loading.value = false;
            return;
        }
        try {
            response.json().then(responseJson => {
                if (response.status == 200) {
                    currentGame.value = responseJson;
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

onBeforeUnmount(() => stopSocket());

getCurrentGame();

</script>

<template>
<div v-if="currentGame">
    <h2>{{ currentGame.created_by }}</h2>
</div>
</template>

<style scoped>

</style>