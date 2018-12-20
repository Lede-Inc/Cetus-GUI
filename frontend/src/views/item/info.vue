<template>
  <div>
    <el-card shadow="never">
      <el-row class="content-items">
        <b>Cetus节点信息</b>
        <el-button type="primary" size="small" style="float: right" @click="btnAddNode()">新增节点</el-button>
      </el-row>
      <el-row v-for="(node,index) in formInfo.nodes" :label="node.key" :key="node.key" class="content-items">
        <div class="rows">
          <el-col :span="3" class="text-center">节点{{ index + 1 }}</el-col>
          <el-col :span="7" class="text-center">SALT ID：{{ node.salt_id }}</el-col>
          <el-col :span="7" class="text-center">管理端口：{{ node.service_port }}</el-col>
          <el-col :span="7" class="text-center">服务端口：{{ node.admin_port }}</el-col>
        </div>
        <div class="rows">
          <el-col :span="3" class="text-center">&nbsp;</el-col>
          <el-col :span="7" class="text-center">版本：{{ node.version }}</el-col>
          <el-col :span="7" class="text-center">状态：{{ node.status|statusFilter }}</el-col>
          <el-col :span="7" class="text-center">
            <el-button v-if="node.status==0" type="danger" size="mini" @click="btnOperateNode(node.id, 'shutdown')">关闭</el-button>
            <el-button v-if="node.status==0" type="danger" size="mini" @click="btnOperateNode(node.id, 'restart')">重启</el-button>
            <el-button v-if="node.status==-1" type="primary" size="mini" @click="btnOperateNode(node.id, 'start')">启动</el-button>
            <el-dropdown trigger="click">
              <span class="el-dropdown-link">其他选项<i class="el-icon-arrow-down el-icon--right"></i></span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item @click.native="btnUpgradeNode(node.id)">更新节点</el-dropdown-item>
                <el-dropdown-item @click.native="btnDeleteNode(node.id)">删除节点</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </el-col>
        </div>
      </el-row>
      <el-row v-if="formInfo.nodes.length==0" class="content-items">
        <el-col class="text-center">
          <div class="rows">
            <p>暂无节点信息</p>
          </div>
        </el-col>
      </el-row>
    </el-card>
    <el-card shadow="never">
      <el-row class="content-items">
        <b>数据库与用户信息</b>
      </el-row>
      <el-row class="content-items" style="word-break: break-all">
        <div class="rows">
          <el-col class="text-center">
            <p>后端数据库(proxy-backend-addresses)</p>
            <span v-if="backends">{{ backends }}</span>
            <span v-else>暂无</span>
          </el-col>
          <el-col class="text-center">
            <p>后端只读数据库(proxy-read-only-backend-addresses)</p>
            <span v-if="readonly_backends">{{ readonly_backends }}</span>
            <span v-else>暂无</span>
          </el-col>
          <el-col class="text-center">
            <p>连接用户(users)</p>
            <div v-if="user_params.users.length">
              <span v-for="item in user_params.users" :key="item.user">{{ item.user }}&nbsp;&nbsp;&nbsp;&nbsp;</span>
            </div>
            <span v-else>暂无</span>
          </el-col>
        </div>
      </el-row>
    </el-card>

    <el-dialog :visible.sync="addNodeDialog" title="增加新Cetus节点" width="50%">
      <el-form ref="addNodeForm" :model="new_cetus" :rules="add_rules" label-width="140px" style="max-width: 410px">
        <el-form-item label="SALT ID" prop="salt_id">
          <el-input v-model="new_cetus.salt_id"/>
        </el-form-item>
        <el-form-item label="端口信息" required>
          <el-col :span="11">
            <el-form-item prop="service_port">
              <el-input v-model.number="new_cetus.service_port" placeholder="服务端口" readonly/>
            </el-form-item>
          </el-col>
          <el-col :span="2" class="line">&nbsp;</el-col>
          <el-col :span="11">
            <el-form-item prop="admin_port">
              <el-input v-model.number="new_cetus.admin_port" placeholder="管理端口" readonly/>
            </el-form-item>
          </el-col>
        </el-form-item>
        <el-form-item label="版本号" prop="version">
          <el-input v-model="new_cetus.version" placeholder="不填默认选择最新版本"/>
        </el-form-item>
        <el-form-item label="安装目录" prop="path">
          <el-input v-model="new_cetus.path" placeholder="默认为/home目录"/>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="confirmAddNode('addNodeForm')">确定新建</el-button>
          <el-button @click="addNodeDialog = false">取消</el-button>
        </el-form-item>
      </el-form>
    </el-dialog>

    <el-dialog :visible.sync="upgradeNodeDialog" title="更新Cetus节点" width="50%">
      <el-form ref="upgradeNodeForm" :model="upgrade_info" label-width="140px">
        <el-form-item label="版本号">
          <el-input v-model="upgrade_info.version" placeholder="不填默认选择最新版本"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="confirmUpgradeNode('upgradeNodeForm')">确定</el-button>
        <el-button @click="upgradeNodeDialog = false">取消</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { paramCetus, operateNode, addCetusNode, upgradeNode, removeNode } from '@/api/cetus'

export default {
  name: 'CetusInfo',
  inject: ['reload'],
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
      user_params: { 'users': [] },
      backends: undefined,
      readonly_backends: undefined,
      users: undefined,
      addNodeDialog: false,
      upgradeNodeDialog: false,
      upgrade_info: {
        'version': '',
        'id': ''
      },
      new_cetus: {
        salt_id: '',
        version: '',
        service_port: '',
        admin_port: '',
        path: '',
        group: ''
      },
      add_rules: {
        salt_id: [{ required: true, message: 'SALT ID不能为空', change: 'blur' }],
        service_port: [{ required: true, message: '端口不能为空', trigger: 'blur' },
          { type: 'number', message: '端口需要是数字', trigger: 'blur' }],
        admin_port: [{ required: true, message: '端口不能为空', trigger: 'blur' },
          { type: 'number', message: '端口需要是数字', trigger: 'blur' }]
      }
    }
  },
  created() {
    paramCetus(this.id, { 'type': 'base' }).then(response => {
      for (const item of response.data) {
        if (item.name === 'proxy-backend-addresses') {
          this.backends = item.value
        } else if (item.name === 'proxy-read-only-backend-addresses') {
          this.readonly_backends = item.value
        }
      }
    })
    paramCetus(this.id, { 'type': 'users' }).then(response => {
      if (response.data.users.length !== 0) {
        this.user_params = response.data
      }
      this.fullLoading = false
    })
  },
  methods: {
    btnOperateNode(id, type) {
      let type_name
      if (type === 'shutdown') {
        type_name = '关闭'
      } else if (type === 'start') {
        type_name = '启动'
      } else if (type === 'restart') {
        type_name = '重启'
      }
      this.$confirm('确认' + type_name + 'Cetus节点？', type_name + '节点', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({ })
        operateNode(id, { 'type': type }).then(response => {
          loading.close()
          this.$message({
            type: 'info',
            message: response.data,
            onClose: this.reload()
          })
        }).catch(() => {
          loading.close()
          this.$message({
            type: 'error',
            message: '操作出现错误，请检查log',
            onClose: this.reload()
          })
        })
      })
    },
    btnAddNode() {
      if (this.formInfo.nodes.length === 0) {
        this.new_cetus = {
          salt_id: '',
          version: '',
          service_port: '',
          admin_port: '',
          path: '',
          group: this.id
        }
      } else {
        this.new_cetus = {
          salt_id: '',
          version: '',
          service_port: this.formInfo.nodes[0]['service_port'],
          admin_port: this.formInfo.nodes[0]['admin_port'],
          path: '',
          group: this.id
        }
      }
      this.addNodeDialog = true
      this.$nextTick(() => {
        this.$refs['addNodeForm'].clearValidate()
      })
    },
    confirmAddNode(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.$confirm('确认增加新节点？', '增加新节点', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            const loading = this.$loading({})
            addCetusNode(this.new_cetus).then(response => {
              loading.close()
              this.$message({
                type: 'info',
                message: response.data,
                onClose: this.reload()
              })
            }).catch(() => {
              loading.close()
              this.$message({
                type: 'error',
                message: '新增节点失败，请检查log',
                onClose: this.reload()
              })
            })
          })
        }
      })
    },
    btnUpgradeNode(id) {
      this.upgrade_info.id = id
      this.upgradeNodeDialog = true
    },
    confirmUpgradeNode() {
      this.$confirm('确认更新Cetus节点？', '更新节点', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({})
        upgradeNode(this.upgrade_info.id, this.upgrade_info).then(response => {
          loading.close()
          this.$message({
            type: 'info',
            message: response.data,
            onClose: this.reload()
          })
        }).catch(() => {
          loading.close()
          this.$message({
            type: 'error',
            message: '更新节点失败，请检查log',
            onClose: this.reload()
          })
        })
      })
    },
    btnDeleteNode(id) {
      this.$confirm('确定删除节点？', '删除节点', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({ background: 'rgba(255, 255, 255, 0.1)' })
        removeNode(id).then(response => {
          loading.close()
          this.$message({
            type: 'info',
            message: response.data,
            onClose: this.reload()
          })
        }).catch(() => {
          loading.close()
          this.$message({
            type: 'error',
            message: '删除节点失败，请检查log',
            onClose: this.reload()
          })
        })
      })
    }
  }
}
</script>

<style scoped>

</style>
