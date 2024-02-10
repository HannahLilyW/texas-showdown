<script setup lang="ts">
import { ref, watch } from 'vue';
import type { Ref } from 'vue';
import { post, chats } from '../services/api.js';

let showChat: Ref<boolean> = ref(false);

let newChat: Ref<string> = ref("");

function hide() {
    showChat.value = false;
}

function show() {
    showChat.value = true;
}

function preventClose(event: Event) {
    event.stopPropagation();
}

const postChat = () => {
    post('games/chat/', {
        'chat': newChat.value
    }).then(response => {
        try {
            response.json().then(responseJson => {
                if (response.status != 200) {
                    console.error(`error posting chat. response status: ${response.status} json: ${responseJson.toString()}`);
                    return;
                }
            })
        } catch (e) {
            console.error(`error posting chat: ${e}`);
        }
    })
}

watch(chats, newVal => {
    console.log(newVal);
})

defineExpose({
  show
})
</script>

<template>
    <div class="modal-parent" v-if="showChat" @click="hide()">
        <div class="sidebar" @click="preventClose($event)">
            <input class="chat-input" type="text" maxlength="256" v-model="newChat" @keyup.enter="postChat">
        </div>
    </div>
</template>

<style scoped>

.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100%;
    box-shadow: 0 0 100px 60px rgba(0, 0, 0, 0.3);
    background-color: var(--color-background);
    width: 200px;

    display: flex;
    justify-content: end;
    flex-direction: column;
    gap: 4px;
    align-items: stretch;
}

.chat-input {
    margin: 4px;
    height: 40px;
}

</style>