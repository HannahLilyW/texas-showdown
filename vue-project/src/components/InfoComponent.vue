<script setup lang="ts">

import { ref } from 'vue';
import type { Ref } from 'vue';

let showTooltip: Ref<boolean> = ref(false);

function hide() {
    showTooltip.value = false;
}

function show() {
    showTooltip.value = true;
}

</script>

<template>
    <div class="overlay" v-if="showTooltip" @click="hide()">
    </div>
    <div class="info-container" v-if="showTooltip">
        <div class="info-message">
            <slot />
        </div>
    </div>
    <div class="info rye" @click="show()">?</div>
</template>

<style scoped>

.info {
    width: 1.5em;
    height: 1.5em;
    border-radius: 0.5em;
    background-color: var(--color-text);
    color: var(--color-background);
    cursor: pointer;
}

.info-message {
    background-color: var(--color-button);
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 100);
    padding: 8px 12px;
    margin: 4px;
    border-radius: 8px;
    left: 50%;
    transform: translate(-50%, 0);
    position: absolute;
    z-index: 2;
}

.overlay {
    position: fixed;
    height: 100%;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 1;
    background: rgba(0, 0, 0, 0.3);
}

</style>