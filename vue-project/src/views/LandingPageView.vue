<script setup lang="ts">
</script>

<template>
  <nav>
    <div class="route-wrapper">
      <RouterLink to="/create-account">
        <div class="route button" v-if="true">
          Create Account
        </div>
      </RouterLink>
      <RouterLink to="/login">
        <div class="route button" v-if="true">
          Log In
        </div>
      </RouterLink>
    </div>
  </nav>
</template>

<style scoped>
.route-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px;
}
.route {
  margin-right: 8px;
  margin: auto;
  width: 150px;
}

</style>