<template>
  <div v-loading="monitorLoading" v-if="chartDataVaild">
    <el-row class="content-items">
      <el-table :data="backends" border style="width: 100%">
        <el-table-column prop="address" label="后端连接信息"></el-table-column>
        <el-table-column prop="state" label="状态"></el-table-column>
        <el-table-column prop="type" label="读写类型"></el-table-column>
        <el-table-column prop="slave_delay" label="从库延迟(ms)"></el-table-column>
        <el-table-column prop="idle_conns" label="空闲连接数"></el-table-column>
        <el-table-column prop="used_conns" label="使用连接数"></el-table-column>
        <el-table-column prop="total_conns" label="总连接数"></el-table-column>
      </el-table>
    </el-row>
    <el-row class="content-items">
      <div id="chart1" style="height:300px; width:100%"></div>
    </el-row>
    <el-row class="content-items">
      <el-select v-model="select1">
        <el-option label="QPS" value="qps"/>
        <el-option label="TPS" value="tps"/>
        <el-option label="各类型语句QPS" value="sentence"/>
      </el-select>
    </el-row>
    <el-row class="content-items">
      <div id="chart2" style="height:300px; width:100%"></div>
    </el-row>
    <el-row class="content-items">
      <el-select v-model="select2">
        <el-option label="负载" value="load"/>
        <el-option label="内存使用" value="mem"/>
      </el-select>
    </el-row>
    <el-row class="content-items">
      <div id="chart3" style="height:300px; width:100%"></div>
    </el-row>
  </div>
  <div v-else>
    <el-row>
      <p>暂无监控信息</p>
    </el-row>
  </div>
</template>

<script>
import echarts from 'echarts'

export default {
  name: 'Chart',
  props: {
    chartData: {
      type: Object
    },
    monitorLoading: {
      type: Boolean
    }
  },
  data() {
    return {
      chart1: null,
      chart2: null,
      chart3: null,
      select1: 'qps',
      select2: 'load',
      xAxis: undefined,
      backends: null,
      chartDataVaild: true
    }
  },
  watch: {
    chartData: {
      deep: true,
      handler(val) {
        if (Object.keys(val).length !== 0) {
          this.xAxis = val['xAxis']
          this.backends = val['backends']
          this.setOptions(this.chart1, val['conns'])
          this.setOptions(this.chart2, val[this.select1])
          this.setOptions(this.chart3, val[this.select2])
          this.chartDataVaild = true
        } else {
          this.chartDataVaild = false
        }
        this.$emit('chartLoading', false)
      }
    },
    select1: function(val) {
      this.setOptions(this.chart2, this.chartData[val])
    },
    select2: function(val) {
      this.setOptions(this.chart3, this.chartData[val])
    }
  },
  mounted() {
    this.initChart()
    this.__resizeHanlder = (() => {
      this.chart1.resize()
      this.chart2.resize()
      this.chart3.resize()
    })
    window.addEventListener('resize', this.__resizeHanlder)
  },
  methods: {
    setOptions(chart, val) {
      chart.clear()
      chart.setOption({
        title: {
          text: val.title
        },
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: val.legend
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.xAxis
        },
        yAxis: {
          type: 'value'
        },
        series: val.series
      })
      chart.resize()
    },
    initChart() {
      this.chart1 = echarts.init(document.getElementById('chart1'))
      this.chart2 = echarts.init(document.getElementById('chart2'))
      this.chart3 = echarts.init(document.getElementById('chart3'))
    }
  }
}
</script>
