<template>
  <div id="app">
    <router-view v-if="isRouteAlive"/>
  </div>
</template>

<script>
export default {
  name: 'App',
  provide() {
    return {
      reload: this.reload
    }
  },
  data() {
    return {
      isRouteAlive: true
    }
  },
  methods: {
    reload() {
      this.isRouteAlive = false
      this.$nextTick(function() {
        this.isRouteAlive = true
      })
    }
  }
}
</script>
