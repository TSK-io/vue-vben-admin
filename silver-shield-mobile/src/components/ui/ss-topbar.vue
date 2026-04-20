<template>
  <app-nav-bar class="topbar" :title="title" :subtitle="subtitle" :show-back="showBack">
    <template #right>
      <slot name="right" />
    </template>
  </app-nav-bar>
</template>

<script setup lang="ts">
import AppNavBar from '@/components/app/AppNavBar.vue'

withDefaults(defineProps<{
  title: string
  subtitle?: string
  showBack?: boolean
}>(), {
  showBack: false,
})
</script>

<style scoped lang="scss">
.topbar {
  display: block;
}
</style>
