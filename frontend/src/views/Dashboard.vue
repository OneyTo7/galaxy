<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <div>
    <h1>欢迎回来</h1>
    <p>当前角色：{{ auth.role }}</p>
  </div>
</template>
