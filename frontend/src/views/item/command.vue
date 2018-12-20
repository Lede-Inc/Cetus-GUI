<template>
  <div>
    <el-card shadow="never">
      <el-row class="el-items">
        <el-checkbox-group ref="nodeGroup" v-model="check_list">
          <el-checkbox v-for="node in formInfo.nodes" :label="node.salt_id + '：' + node.admin_port" :key="node.id" :value="node.id" checked/>
        </el-checkbox-group>
      </el-row>
      <el-row class="el-items">
        <el-col :span="21" class="text-center">
          <el-input ref="commandArea" v-model="commands" :autosize="{ minRows: 10, maxRows: 50}" type="textarea" placeholder="请输入命令"/>
        </el-col>
        <el-col :span="1" class="text-center">&nbsp;</el-col>
        <el-col :span="2" class="text-center">
          <el-button type="primary" size="small" class="bottom-button" @click="sendCommand('nodeGroup', 'commandArea')">执行</el-button>
        </el-col>
      </el-row>
      <el-row class="el-items">
        <pre ref="results" v-text="results"></pre>
      </el-row>
    </el-card>
  </div>
</template>

<script>
import { manageCetus } from '@/api/cetus'

export default {
  name: 'CetusCommand',
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
      check_list: [],
      commands: '',
      results: '>>>\n'
    }
  },
  watch: {
    results: function() {
      this.$nextTick(() => {
        const list = this.$refs['results']
        list.scrollTop = list.scrollHeight
      })
    }
  },
  methods: {
    sendCommand(nodes, item) {
      const node_group = []
      this.$refs[nodes].$children.map(function(n) {
        if (n.isChecked) { node_group.push(n.value) }
      })
      if (node_group.length && this.$refs[item].value) {
        manageCetus(this.id, {
          'commands': this.$refs[item].value,
          'nodes': node_group
        }).then(response => {
          for (const i of response.data) {
            this.results += i
          }
          this.results += '\n\n'
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '后台执行出现错误，请查看日志'
          })
        })
      } else {
        this.$message({
          type: 'info',
          message: '请选择节点或输入命令'
        })
      }
    }
  }
}
</script>

<style scoped>
pre {
  height: 400px;
  overflow: auto;
  border: 1px solid #e3e3e3;
  padding: 13px 25px 8px 13px;
  background: #f5f5f5;
  font-size: 13px;
}
</style>
