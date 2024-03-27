<script setup lang="ts">

import { ref } from 'vue';
import type { Ref } from 'vue';

let showModal: Ref<boolean> = ref(false);

function hide() {
    showModal.value = false;
}

function show() {
    showModal.value = true;
}

defineExpose({
  show,
  hide
})

</script>

<template>
    <div class="overlay" v-if="showModal" @click="hide()">
    </div>
    <div class="modal-container" v-if="showModal">
        <div class="modal-message">
            <slot />
        </div>
    </div>
</template>

<style scoped>

.modal-message {
    background-color: var(--color-background);
    box-shadow: 0px 0px 10px rgba(0, 0, 0, 100);
    padding: 8px 12px;
    margin: 4px;
    border-radius: 8px;
    left: 50%;
    top: 20%;
    width: 80%;
    transform: translate(-50%, 0);
    position: fixed;
    z-index: 2;
}

.overlay {
    position: fixed;
    height: 100%;
    width: 100%;
    left: 0;
    top: 0;
    z-index: 1;
    background: rgba(0, 0, 0, 0.6);
}

</style>