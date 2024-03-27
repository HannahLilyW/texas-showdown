<script setup lang="ts">
import router from './router';
import { RouterView, useRoute } from 'vue-router';
import { ref } from 'vue';
import type { Ref } from 'vue';
import { username, updateOwnProfileInfo, checkForGift } from './services/api.js';
import MenuIcon from './components/icons/IconMenu.vue';
import ArrowLeftIcon from './components/icons/IconArrowLeft.vue';
import MenuComponent from './components/MenuComponent.vue';
import ModalComponent from './components/ModalComponent.vue';

let menu = ref();
let giftModal = ref();
let giftAmount: Ref<number> = ref(0);
const route = useRoute();

if (!username.value) {
  // Stop people from accidentally going to a page they need to be logged in for, before logging in
  router.push('/');
} else {
  updateOwnProfileInfo(() => {
    checkForGift((gift_amount: number) => {
      giftAmount.value = gift_amount;
      giftModal.value.show();
    });
  });
}

function hideGiftModal() {
  giftModal.value.hide();
}

function goToLanding() {
  router.push('/');
}

function showMenu() {
  menu.value.show();
}

function goBack() {
  router.go(-1);
}

</script>

<template>
  <header>
    <div class="buttons-row" id="backButton">
      <ArrowLeftIcon id="backButtonIcon" v-if="route.path != '/'" @click="goBack()"></ArrowLeftIcon>
    </div>
    <div class="title-wrapper">
      <div id="title" class="point rye" @click="goToLanding()">
        WESTERN WAGER
      </div>
    </div>
    <div class="buttons-row">
      <MenuIcon @click="showMenu()" class="point"></MenuIcon>
    </div>
  </header>

  <div class="container">
    <RouterView />
  </div>

  <MenuComponent ref="menu"></MenuComponent>
  <ModalComponent ref="giftModal">
    <div class="gift-modal-container">
      <div class="center rye">DAILY GIFT</div>
      <div class="coins center"><div class="coin-icon"></div>{{ giftAmount }}</div>
      <div class="buttons-row buttons-row-center">
        <div class="button rye" @click="hideGiftModal()">THANKS!</div>
      </div>
    </div>
  </ModalComponent>
</template>

<style scoped>
header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  flex-wrap: nowrap;
  background-color: var(--color-background-dark);
  box-shadow: 0 0 100px 60px rgba(0, 0, 0, 0.5);
  padding-right: 8px;
  padding-left: 8px;
}

.gift-modal-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.container {
  padding: 8px;
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
}

#backButton {
  width: 32px;
}

#backButtonIcon {
  cursor: pointer;
}

@media(max-width: 420px) {
  #title {
    font-size: 18px;
  }
}
</style>
