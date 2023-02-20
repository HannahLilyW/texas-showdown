<script setup lang="ts">
// import TheWelcome from '../components/TheWelcome.vue'
</script>

<template>
  <nav>
    <div class="route-wrapper">
      <div class="route" v-if="true">
        <RouterLink to="/create-account">Create Account</RouterLink>
      </div>
      <div class="route" v-if="true">
        <RouterLink to="/login">Log In</RouterLink>
      </div>
    </div>
  </nav>
  <!-- <main>
    <TheWelcome />
  </main> -->
</template>

<style scoped>
.route-wrapper {
  display: flex;
  align-items: center;
}
.route {
  padding-right: 8px;
}

</style>