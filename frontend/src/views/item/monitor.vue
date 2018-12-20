<template>
  <div>
    <el-card shadow="never">
      <el-row class="el-items">
        <el-radio-group ref="nodeRadio" v-model="radio_list">
          <el-radio v-for="node in formInfo.nodes" :key="node.id" :label="node.id" :value="node.id">{{ node.salt_id + '：' + node.service_port }}</el-radio>
        </el-radio-group>
      </el-row>
      <el-row class="el-items">
        <div class="chart-container">
          <chart :chart-data="chartData" :monitor-loading="monitorLoading" @chartLoading="chartLoading" height="300px" width="100%"></chart>
        </div>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { monitorNode } from '@/api/cetus'
import Chart from '@/views/item/chart'

export default {
  name: 'CetusMonitor',
  components: { Chart },
  props: {
    id: {
      type: String,
      default: '0'
    },
    formInfo: {
      type: Object,
      default() {
        return {}
      }
    }
  },
  data() {
    return {
      radio_list: '',
      chartData: undefined,
      monitorLoading: true
    }
  },
  watch: {
    radio_list: function() {
      this.monitorLoading = true
      monitorNode(this.radio_list, { 'time': 1 }).then(response => {
        this.chartData = response.data
      })
    }
  },
  created() {
    this.radio_list = this.formInfo.nodes[0]['id']
  },
  methods: {
    getMonitorData(tab, event) {
      if (tab.name === 'fourth') {
        monitorNode(this.radio_list, { 'time': 1 }).then(response => {
          this.chartData = response.data
        })
      }
    },
    chartLoading(data) {
      this.monitorLoading = data
    }
  }
}
</script>

<style scoped>

</style>
