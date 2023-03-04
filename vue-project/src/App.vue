<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
// import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <header>
    <div class="title-wrapper">
      <RouterLink to="/"><img alt="Flag of Texas" class="logo" src="@/assets/flag64.png" width="64" height="43" /></RouterLink>
      <div id="title">
        TEXAS SHOWDOWN
      </div>
    </div>
  </header>

  <div class="container">
    <RouterView />
  </div>
</template>

<style scoped>
.title-wrapper {
  display: flex;
  align-items: center;
  padding: 8px;
}
#title {
  font-size: 32px;
  padding-left: 8px;
}
.container {
  margin: 8px;
}
</style>
