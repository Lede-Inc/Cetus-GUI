<template>
  <div class="app-container">
    <p>404啦</p>
    <p>正在返回首页...</p>
  </div>
</template>

<script>
export default {
  name: '404',
  mounted: function() {
    setTimeout(() => {
      this.$router.push({ path: '/' })
    }, 3000)
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>

</style>
