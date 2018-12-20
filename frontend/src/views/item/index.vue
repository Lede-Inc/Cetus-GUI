<template>
  <el-main v-loading="fullLoading" element-loading-background="rgba(255, 255, 255, 1)">
    <div class="item-main-header">
      <el-card class="box-card" shadow="never">
        <el-row>
          <h3>{{ formInfo.cetus_name }}</h3>
        </el-row>
        <el-row class="header-items">
          <el-col :span="6" class="text-center">Cetus类型：{{ formInfo.cetus_type|typeFilter }}</el-col>
          <el-col v-if="formInfo.config_db" :span="6" class="text-center">配置库：{{ formInfo.config_db }}</el-col>
          <el-col v-else :span="6">配置库：暂无</el-col>
        </el-row>
        <el-row class="header-items">
          <el-col v-if="formInfo.create_time" :span="6" class="text-center">创建时间：{{ formInfo.create_time|parseTime }}</el-col>
          <el-col v-else :span="6" class="text-center">创建时间：暂无</el-col>
        </el-row>
      </el-card>
    </div>
    <el-tabs v-model="activeTab">
      <el-tab-pane label="基础信息" name="info">
        <cetus-info :id="id" :form-info="formInfo"></cetus-info>
      </el-tab-pane>
      <el-tab-pane label="配置" name="config">
        <cetus-config :id="id" :form-info="formInfo"></cetus-config>
      </el-tab-pane>
      <el-tab-pane label="管理命令" name="command">
        <cetus-command :id="id" :form-info="formInfo"></cetus-command>
      </el-tab-pane>
      <el-tab-pane :lazy="true" label="监控信息" name="monitor">
        <cetus-monitor :id="id" :form-info="formInfo"></cetus-monitor>
      </el-tab-pane>
    </el-tabs>
  </el-main>
</template>
<script>
import { cetusItem } from '@/api/cetus'
import CetusInfo from '@/views/item/info'
import CetusConfig from '@/views/item/config'
import CetusCommand from '@/views/item/command'
import CetusMonitor from '@/views/item/monitor'

export default {
  inject: ['reload'],
  components: { CetusInfo, CetusConfig, CetusCommand, CetusMonitor },
  data() {
    return {
      id: this.$route.params.id,
      activeTab: 'info',
      formInfo: {
        cetus_name: '',
        cetus_type: '',
        config_db: '',
        create_time: undefined,
        nodes: []
      },
      fullLoading: true
    }
  },
  created() {
    this.$nextTick(() => {
      this.getInfo()
    })
  },
  methods: {
    getInfo() {
      cetusItem(this.id).then(response => {
        this.formInfo = response.data
        this.fullLoading = false
      }).catch(() => {
        this.$message({
          type: 'error',
          message: '请求后端数据错误，请查看日志'
        })
      })
    }
  }
}
</script>
<style>
.header-items {
  margin-bottom: 10px;
  font-size: 13px;
  color: #909399;
}
.el-items {
  margin: 25px 0 25px 5px;
}
.content-items {
  padding: 15px 0 15px 5px;
  color: #606266;
  line-height: 43px;
  border-bottom: 1px solid #d8d8d8;
}
.content-items .rows {
  margin: 0 0 30px 5px;
  line-height: 43px;
  font-size: 14px;
}
.box-card {
  background-color: #F2F6FC;
}
.el-tabs__nav {
  margin-left: 20px;
}
.bottom-button {
  position: absolute;
  bottom: 0;
}
.el-textarea.is-disabled .el-textarea__inner {
  color: #606266;
}
.el-dropdown {
  margin-left: 50px;
  color: #409eff;
  cursor: pointer;
}
.el-card__body {
  padding: 0 20px 20px 20px !important;
}
.fund_param .el-form-item {
  margin-bottom: 12px;
}
.el-dialog {
  position: absolute;
  top: 50%;
  left: 50%;
  margin: 0 !important;
  transform: translate(-50%, -50%);
  max-height: calc(100% - 30px);
  max-width: calc(100% - 30px);
  display: flex;
  flex-direction: column;
}
.el-dialog .el-dialog__body {
  overflow: auto;
  padding: 10px 20px;
}
.dialog-table {
  width: 95%;
  margin: 0 auto;
}
</style>
