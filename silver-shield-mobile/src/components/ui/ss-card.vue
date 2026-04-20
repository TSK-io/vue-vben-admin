<template>
  <app-card class="ss-card ss-fade-up">
    <slot />
  </app-card>
</template>

<script setup lang="ts">
import AppCard from '@/components/app/AppCard.vue'
</script>

<style scoped lang="scss">
.ss-card {
  display: block;
}
</style>
