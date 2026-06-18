<template>
  <div />
</template>

<script setup lang="ts">
const auth = useAuthStore()

onMounted(async () => {
  await auth.hydrateFromStorage()
  if (auth.isAuthenticated) {
    if (auth.isAdmin || auth.isEditor) {
      navigateTo('/admin')
    } else {
      navigateTo('/dashboard')
    }
  } else {
    navigateTo('/login')
  }
})
</script>
