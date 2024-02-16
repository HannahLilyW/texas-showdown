<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import { post } from '../services/api.js';
import router from '../router';

const code: Ref<string> = ref('');
const error: Ref<string> = ref('');
const invalid: Ref<boolean> = ref(code.value.length !== 4);

watch(code, () => {
    invalid.value = (code.value.length !== 4);
})

function join() {
    if (!invalid.value) {
        post('games/join_game_by_code/', {
            'room_code': code.value
        }).then(response => {
            response.json().then(responseJson => {
                if (response.status == 200) {
                    router.push('/active-game');
                } else {
                    if (responseJson) {
                        error.value = responseJson;
                    }
                }
            })
        })
    }
}

</script>

<template>
<div class="container">
    <div class="center">
        Please enter the 4-letter room code:
    </div>
    <input type="text" class="room-code-input" maxlength="4" v-model="code">
    <div class="buttons-row buttons-row-center">
        <div class="button button-big center rye" :class="{disabled: invalid}" @click="join()">JOIN</div>
    </div>
    <div v-if="error" class="center red-text">{{ error }}</div>
</div>
</template>

<style scoped>
.room-code-input {
    width: 160px;
    height: 80px;
    font-size: 40px;
    font-family: rye;
    text-transform: uppercase;
    text-align: center;
}

.container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
}
</style>