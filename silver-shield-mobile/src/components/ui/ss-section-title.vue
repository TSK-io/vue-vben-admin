<template>
  <app-section class="section-title-wrap" :title="title" :subtitle="subtitle">
    <template #action>
      <slot name="action" />
    </template>
  </app-section>
</template>

<script setup lang="ts">
import AppSection from '@/components/app/AppSection.vue'

defineProps<{
  title: string
  subtitle?: string
}>()
</script>

<style scoped lang="scss">
.section-title-wrap {
  display: block;
}
</style>
