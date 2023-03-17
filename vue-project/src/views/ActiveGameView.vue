<script setup lang="ts">
import { get } from '../services/api.js';
import { ref, onBeforeUnmount } from 'vue';
import type { Ref } from 'vue';
import type { Game } from '../models';
import { start, stop } from '../services/sio.js';

let currentGame: Ref<Game|null> = ref(null);
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
                    start();
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

onBeforeUnmount(() => stop());

getCurrentGame();

</script>

<template>

</template>

<style scoped>

</style>