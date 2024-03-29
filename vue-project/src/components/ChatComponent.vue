<script setup lang="ts">
import { ref, watch, nextTick } from 'vue';
import type { Ref } from 'vue';
import { post, chats, currentGame, unread } from '../services/api.js';

let showChat: Ref<boolean> = ref(false);

let newChat: Ref<string> = ref("");

const chatsRef = ref();
const newChatInput = ref();

function hide() {
    showChat.value = false;
    unread.value = false;
}

function show() {
    showChat.value = true;
    unread.value = false;
    nextTick(() => {
        chatsRef.value.scrollTo({top: chatsRef.value.scrollHeight})
        newChatInput.value.focus();
    })
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
                chatsRef.value.scrollTo({top: chatsRef.value.scrollHeight})
            })
        } catch (e) {
            console.error(`error posting chat: ${e}`);
        }
    })
    newChat.value = '';
}

watch(chats, () => {
    setTimeout(() => {
        chatsRef.value?.scrollTo({top: chatsRef.value.scrollHeight})
    }, 100)
}, {deep: true})

defineExpose({
  show
})

</script>

<template>
    <div class="modal-parent" v-if="showChat" @click="hide()">
        <div class="sidebar" @click="preventClose($event)">
            <div class="chats" ref="chatsRef">
                <div v-for="chat in chats" class="chat">
                    <span class="yellow-text">
                        {{ currentGame?.player_set.find(player => player.username == chat['username'])?.name }}:
                    </span> {{ chat['chat'] }}
                </div>
            </div>
            <input class="chat-input" type="text" maxlength="256" v-model="newChat" ref="newChatInput" @keyup.enter="postChat">
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
    scrollbar-color: var(--color-button) var(--color-background);
}

.chat-input {
    margin: 4px;
    height: 40px;
    min-height: 40px;
    font-size: 16px;
}

.chat {
    padding-left: 4px;
}

.chats {
    overflow: auto;
}

</style>