<template>
  <div>
    <el-card shadow="never">
      <el-row class="content-items">
        <b>基础配置</b>
      </el-row>
      <el-row class="content-items">
        <el-col :span="8" class="text-center">
          <el-button type="primary" size="medium" @click="btnChangeFund()">参数修改</el-button>
        </el-col>
        <el-col :span="8" class="text-center">
          <el-button type="primary" size="medium" @click="btnChangeVariables()">用户及变量信息</el-button>
        </el-col>
        <el-col v-if="formInfo.cetus_type=='shard'" :span="8" class="text-center">
          <el-button type="primary" size="medium" @click="btnChangeVdb()">分片信息修改</el-button>
        </el-col>
      </el-row>
      <el-row class="content-items">
        <b>其他配置</b>
      </el-row>
      <el-row class="content-items">
        <el-col :span="8" class="text-center">
          <el-button type="danger" size="medium" @click="btnRestartAll()">重启全部节点</el-button>
        </el-col>
        <el-col :span="8" class="text-center">
          <el-button type="danger" size="medium" @click="btnUpgradeCetus()">更新全部节点</el-button>
        </el-col>
        <el-col :span="8" class="text-center">
          <el-button type="danger" size="medium" @click="btnRemoveAll()">删除cetus服务</el-button>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog :visible.sync="changeFundDialog" title="基础参数修改" width="90%">
      <el-form ref="fundParamForm" :model="fund_params" label-position="left" class="fund_param" style="word-break: break-all">
        <el-form-item>
          <el-col :span="6" class="text-center"><span>参数名</span></el-col>
          <el-col :span="9" class="text-center"><span>当前参数值</span></el-col>
          <el-col :span="9" class="text-center"><span>修改值</span></el-col>
        </el-form-item>
        <el-form-item v-for="(item,index) in fund_params.params" :key="item.id">
          <el-tooltip v-if="item.descrip" :content="item.descrip" class="item" effect="light" placement="bottom-start">
            <el-col :span="6" class="text-center"><b v-if="item.type=='Static'">{{ item.name }}</b><span v-else>{{ item.name }}</span></el-col>
          </el-tooltip>
          <el-col v-else :span="6" class="text-center"><b v-if="item.type=='Static'">{{ item.name }}</b><span v-else>{{ item.name }}</span></el-col>
          <el-col :span="9" class="text-center"><span v-if="item.value" v-once>{{ item.value }}</span><span v-else v-once>空</span></el-col>
          <el-col :span="9" class="text-center">
            <el-input v-model="fund_params.params[index].value" size="medium"/>
          </el-col>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="confirmChangeFund('fundParamForm')">确定</el-button>
        <el-button @click="changeFundDialog = false">取消</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="upgradeCetusDialog" title="更新全部节点" width="50%">
      <el-form ref="upgradeCetusForm" :model="upgrade_info" label-width="140px">
        <el-form-item label="版本号">
          <el-input v-model="upgrade_info.version" placeholder="不填默认选择最新版本"/>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="confirmUpgradeCetus('upgradeCetusForm')">确定</el-button>
        <el-button @click="upgradeCetusDialog = false">取消</el-button>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="changeVariablesDialog" width="80%">
      <div class="dialog-table">
        <el-tabs v-model="tabVariables">
          <el-tab-pane label="用户信息" name="users">
            <el-button size="small" type="primary" icon="el-icon-circle-plus-outline" @click="addTempUser" style="float: right">新增用户</el-button>
            <el-table :data="user_params.users" style="width: 100%;min-height: 450px">
              <el-table-column label="用户名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.user }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.user"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="客户端密码">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.client_pwd }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.client_pwd"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="服务端密码">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.server_pwd }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.server_pwd"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <div class="operate-groups">
                    <el-button type="primary" size="mini" v-if="!scope.row.editing" icon="el-icon-edit-outline" @click="handleEditUser(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="primary" size="mini" v-if="scope.row.editing" icon="el-icon-success" @click="handleSaveUser(scope.$index, scope.row)">保存</el-button>
                    <el-button size="mini" type="danger" v-if="!scope.row.editing" icon="el-icon-delete" @click="handleDeleteUser(scope.$index, scope.row)">删除</el-button>
                    <el-button size="mini" type="warning" v-if="scope.row.editing" icon="el-icon-warning" @click="handleCancelUser(scope.$index, scope.row)">取消</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="变量信息" name="variables">
            <el-button size="small" type="primary" icon="el-icon-circle-plus-outline" @click="addTempVariable" style="float: right">新增变量</el-button>
            <el-table :data="variable_params.variables" style="width: 100%;min-height: 450px">
              <el-table-column label="变量名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.name }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.name"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="类型">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.type }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.type"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="静默值">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.silent_values }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.silent_values"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="允许值">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.allowed_values }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.allowed_values"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <div class="operate-groups">
                    <el-button type="primary" size="mini" v-if="!scope.row.editing" icon="el-icon-edit-outline" @click="handleEditVariable(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="primary" size="mini" v-if="scope.row.editing" icon="el-icon-success" @click="handleSaveVariable(scope.$index, scope.row)">保存</el-button>
                    <el-button size="mini" type="danger" v-if="!scope.row.editing" icon="el-icon-delete" @click="handleDeleteVariable(scope.$index, scope.row)">删除</el-button>
                    <el-button size="mini" type="warning" v-if="scope.row.editing" icon="el-icon-warning" @click="handleCancelVariable(scope.$index, scope.row)">取消</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>

    <el-dialog :visible.sync="changeVdbDialog" width="90%">
      <div class="dialog-table">
        <el-tabs v-model="tabVdb">
          <el-tab-pane label="分片信息" name="vdb">
            <el-button size="small" type="primary" icon="el-icon-circle-plus-outline" @click="addTempVdb" style="float: right">新增分片键</el-button>
            <el-table :data="vdb_params.vdb" style="width: 100%;min-height: 450px">
              <el-table-column label="分片id" width="120px">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.id }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model.number="scope.row.id"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="分片数" width="120px">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.num }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model.number="scope.row.num"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="类型" width="120px">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.type }}</span>
                  </div>
                  <div v-else>
                    <el-select v-model="scope.row.type">
                      <el-option label="str" value="str"/>
                      <el-option label="number" value="number"/>
                      <el-option label="datetime" value="datetime"/>
                    </el-select>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="方法" width="120px">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.method }}</span>
                  </div>
                  <div v-else>
                    <el-select v-model="scope.row.method">
                      <el-option label="hash" value="hash"/>
                      <el-option label="range" value="range"/>
                    </el-select>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="分片信息">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.partitions }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.partitions" width="100%" placeholder='格式如 {"groupA": [0,1,2,3]}'></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200px">
                <template slot-scope="scope">
                  <div class="operate-groups">
                    <el-button type="primary" size="mini" v-if="!scope.row.editing" icon="el-icon-edit-outline" @click="handleEditVdb(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="primary" size="mini" v-if="scope.row.editing" icon="el-icon-success" @click="handleSaveVdb(scope.$index, scope.row)">保存</el-button>
                    <el-button size="mini" type="danger" v-if="!scope.row.editing" icon="el-icon-delete" @click="handleDeleteVdb(scope.$index, scope.row)">删除</el-button>
                    <el-button size="mini" type="warning" v-if="scope.row.editing" icon="el-icon-warning" @click="handleCancelVdb(scope.$index, scope.row)">取消</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="分片表信息" name="table">
            <el-button size="small" type="primary" icon="el-icon-circle-plus-outline" @click="addTempTable" style="float: right">新增分片表</el-button>
            <el-table :data="vdb_params.table" style="width: 100%;min-height: 450px">
              <el-table-column label="分片id">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.vdb }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model.number="scope.row.vdb"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="db名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.db }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.db"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="分片键名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.pkey }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.pkey"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="表名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.table }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.table"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <div class="operate-groups">
                    <el-button type="primary" size="mini" v-if="!scope.row.editing" icon="el-icon-edit-outline" @click="handleEditTable(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="primary" size="mini" v-if="scope.row.editing" icon="el-icon-success" @click="handleSaveTable(scope.$index, scope.row)">保存</el-button>
                    <el-button size="mini" type="danger" v-if="!scope.row.editing" icon="el-icon-delete" @click="handleDeleteTable(scope.$index, scope.row)">删除</el-button>
                    <el-button size="mini" type="warning" v-if="scope.row.editing" icon="el-icon-warning" @click="handleCancelTable(scope.$index, scope.row)">取消</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
          <el-tab-pane label="单点表信息" name="single">
            <el-button size="small" type="primary" icon="el-icon-circle-plus-outline" @click="addTempSingle" style="float: right">新增单点表</el-button>
            <el-table :data="vdb_params.single_tables" style="width: 100%;min-height: 450px">
              <el-table-column label="db名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.db }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.db"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="组名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.group }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.group"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="表名">
                <template slot-scope="scope">
                  <div v-if="!scope.row.editing">
                    <span>{{ scope.row.table }}</span>
                  </div>
                  <div v-else>
                    <el-input v-model="scope.row.table"></el-input>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <div class="operate-groups">
                    <el-button type="primary" size="mini" v-if="!scope.row.editing" icon="el-icon-edit-outline" @click="handleEditSingle(scope.$index, scope.row)">编辑</el-button>
                    <el-button type="primary" size="mini" v-if="scope.row.editing" icon="el-icon-success" @click="handleSaveSingle(scope.$index, scope.row)">保存</el-button>
                    <el-button size="mini" type="danger" v-if="!scope.row.editing" icon="el-icon-delete" @click="handleDeleteSingle(scope.$index, scope.row)">删除</el-button>
                    <el-button size="mini" type="warning" v-if="scope.row.editing" icon="el-icon-warning" @click="handleCancelSingle(scope.$index, scope.row)">取消</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { paramCetus, changeParam, upgradeCetus, removeCetus, operateCetus } from '@/api/cetus'

export default {
  name: 'CetusConfig',
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
      changeFundDialog: false,
      upgradeCetusDialog: false,
      changeVariablesDialog: false,
      changeVdbDialog: false,
      fund_params: { 'params': [] },
      user_params: { 'users': [] },
      variable_params: { 'variables': [] },
      vdb_params: { 'vdb': [], 'table': [], 'single_tables': [] },
      tabVariables: 'users',
      tabVdb: 'vdb',
      upgrade_info: {
        'version': '',
        'id': ''
      }
    }
  },
  methods: {
    btnChangeFund() {
      const loading = this.$loading({ background: 'rgba(0, 0, 0, 0.1)' })
      paramCetus(this.id, { 'type': 'base' }).then(response => {
        this.fund_params.params = response.data
        this.changeFundDialog = true
        this.$nextTick(() => {
          loading.close()
        })
      }).catch(() => {
        loading.close()
      })
    },
    btnChangeVariables() {
      this.tmpUsers = false
      const loading = this.$loading({ background: 'rgba(0, 0, 0, 0.1)' })
      paramCetus(this.id, { 'type': 'users' }).then(response => {
        const items = response.data.users
        this.user_params.users = items.map(v => {
          v.originalUser = v.user
          v.originalClient = v.client_pwd
          v.originalServer = v.server_pwd
          return v
        })
      })
      paramCetus(this.id, { 'type': 'variables' }).then(response => {
        const items = response.data.variables
        this.variable_params.variables = items.map(v => {
          v.originalName = v.name
          v.originalType = v.type
          v.silent_values = JSON.stringify(v.silent_values)
          v.allowed_values = JSON.stringify(v.allowed_values)
          v.originalSilent = v.silent_values
          v.originalAllowed = v.allowed_values
          return v
        })
        this.changeVariablesDialog = true
        this.$nextTick(() => {
          loading.close()
        })
      }).catch(() => {
        loading.close()
      })
    },
    btnUpgradeCetus() {
      this.upgrade_info.id = this.id
      this.upgradeCetusDialog = true
    },
    confirmChangeFund(formName) {
      this.$confirm('确认修改参数？(修改加粗静态参数时，需要手动重启Cetus)', '修改基础参数', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({})
        changeParam(this.id, { 'type': 'base', 'data': this.fund_params.params }).then(response => {
          loading.close()
          this.$message({
            type: 'info',
            message: '修改成功',
            onClose: this.reload()
          })
        }).catch(() => {
          loading.close()
          this.$message({
            type: 'error',
            message: '参数修改失败'
          })
        })
      })
    },
    confirmUpgradeCetus() {
      this.$confirm('确认更新全部节点？', '更新全部节点', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({})
        upgradeCetus(this.upgrade_info.id, this.upgrade_info).then(response => {
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
            message: '节点更新失败'
          })
        })
      })
    },
    btnRestartAll() {
      this.$confirm('确定重启全部节点？', '重启全部节点', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({ })
        operateCetus(this.id, { 'type': 'restart' }).then(response => {
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
            message: '节点重启失败'
          })
        })
      })
    },
    btnRemoveAll() {
      this.$confirm('确定删除Cetus服务？', '删除Cetus服务', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const loading = this.$loading({ })
        removeCetus(this.id).then(response => {
          loading.close()
          this.$message({
            type: 'info',
            message: response.data,
            onClose: this.$router.push({ path: '/' })
          })
        }).catch(() => {
          loading.close()
          this.$message({
            type: 'error',
            message: '节点删除失败'
          })
        })
      })
    },
    handleEditUser($index, row) {
      this.$set(this.user_params.users[$index], 'editing', true)
    },
    handleSaveUser($index, row) {
      if (row.user && row.client_pwd && row.server_pwd) {
        changeParam(this.id, { 'type': 'users', 'data': this.user_params }).then(response => {
          row.originalUser = row.user
          row.originalClient = row.client_pwd
          row.originalServer = row.server_pwd
          this.$set(this.user_params.users[$index], 'editing', false)
          this.$message({
            type: 'success',
            message: '保存成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '保存失败，请输入正确值!'
          })
        })
      } else {
        this.$message({
          type: 'info',
          message: '请输入完整信息!'
        })
      }
      this.tmpUsers = false
    },
    handleCancelUser($index, row) {
      if (!row.originalUser) {
        this.user_params.users.splice($index, 1)
      } else {
        row.user = row.originalUser
        row.client_pwd = row.originalClient
        row.server_pwd = row.originalServer
        this.$set(this.user_params.users[$index], 'editing', false)
      }
      this.tmpUsers = false
    },
    addTempUser() {
      if (!this.tmpUsers) {
        this.user_params.users.unshift({
          user: '',
          client_pwd: '',
          server_pwd: '',
          editing: true
        })
        this.tmpUsers = true
      } else {
        this.$message({
          type: 'info',
          message: '请先完成已有数据!'
        })
      }
    },
    handleDeleteUser($index, row) {
      this.$confirm('确认删除该用户？', '删除用户', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.user_params.users.splice($index, 1)
        this.$message({
          type: 'success',
          message: '删除成功!'
        })
        changeParam(this.id, { 'type': 'users', 'data': this.user_params }).then(response => {
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '参数修改失败'
          })
        })
      })
    },
    handleEditVariable($index, row) {
      this.$set(this.variable_params.variables[$index], 'editing', true)
    },
    handleSaveVariable($index, row) {
      if (row.name && row.type && row.silent_values && row.allowed_values) {
        changeParam(this.id, { 'type': 'variables', 'data': this.variable_params }).then(response => {
          row.originalName = row.name
          row.originalType = row.type
          row.originalSilent = row.silent_values
          row.originalAllowed = row.allowed_values
          this.$set(this.variable_params.variables[$index], 'editing', false)
          this.$message({
            type: 'success',
            message: '保存成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '保存失败，请输入正确值!'
          })
        })
      } else {
        this.$message({
          type: 'info',
          message: '请输入完整信息!'
        })
      }
      this.tmpUsers = false
    },
    handleCancelVariable($index, row) {
      if (!row.originalName) {
        this.variable_params.variables.splice($index, 1)
      } else {
        row.name = row.originalName
        row.type = row.originalType
        row.silent_values = row.originalSilent
        row.allowed_values = row.originalAllowed
        this.$set(this.variable_params.variables[$index], 'editing', false)
      }
      this.tmpUsers = false
    },
    addTempVariable() {
      if (!this.tmpUsers) {
        this.variable_params.variables.unshift({
          name: '',
          type: '',
          silent_values: '',
          allowed_values: '',
          editing: true
        })
        this.tmpUsers = true
      } else {
        this.$message({
          type: 'info',
          message: '请先完成已有数据!'
        })
      }
    },
    handleDeleteVariable($index, row) {
      this.$confirm('确认删除该变量？', '删除变量', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        changeParam(this.id, { 'type': 'variables', 'data': this.variable_params }).then(response => {
          this.variable_params.variables.splice($index, 1)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '删除失败!'
          })
        })
      })
    },
    btnChangeVdb() {
      this.tmpUsers = false
      const loading = this.$loading({ background: 'rgba(0, 0, 0, 0.1)' })
      paramCetus(this.id, { 'type': 'sharding' }).then(response => {
        this.vdb_params = response.data
        if (this.vdb_params.single_tables) {
          this.vdb_params.single_tables = this.vdb_params.single_tables.map(v => {
            v.originalGroup = v.group
            v.originalTable = v.table
            v.originalDb = v.db
            return v
          })
        }
        if (this.vdb_params.table) {
          this.vdb_params.table = this.vdb_params.table.map(v => {
            v.originalPkey = v.pkey
            v.originalTable = v.table
            v.originalVdb = v.vdb
            v.originalDb = v.db
            return v
          })
        }
        if (this.vdb_params.vdb) {
          this.vdb_params.vdb = this.vdb_params.vdb.map(v => {
            v.originalType = v.type
            v.originalID = v.id
            v.originalNum = v.num
            v.originalMethod = v.method
            if (typeof v.partitions === 'object') {
              v.partitions = JSON.stringify(v.partitions)
            }
            v.originalPartitions = v.partitions
            return v
          })
        }
        this.changeVdbDialog = true
        this.$nextTick(() => {
          loading.close()
        })
      })
    },
    handleEditVdb($index, row) {
      this.$set(this.vdb_params.vdb[$index], 'editing', true)
    },
    handleSaveVdb($index, row) {
      if (row.id && row.num && row.type && row.method && row.partitions) {
        changeParam(this.id, { 'type': 'sharding', 'data': this.vdb_params }).then(response => {
          row.originalType = row.type
          row.originalID = row.id
          row.originalNum = row.num
          row.originalMethod = row.method
          row.originalPartitions = row.partitions
          this.$set(this.vdb_params.vdb[$index], 'editing', false)
          this.$message({
            type: 'success',
            message: '保存成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '保存失败，请输入正确值!'
          })
        })
      } else {
        this.$message({
          type: 'info',
          message: '请输入完整信息!'
        })
      }
      this.tmpUsers = false
    },
    handleCancelVdb($index, row) {
      if (!row.originalID) {
        this.vdb_params.vdb.splice($index, 1)
      } else {
        row.type = row.originalType
        row.id = row.originalID
        row.num = row.originalNum
        row.method = row.originalMethod
        row.partitions = row.originalPartitions
        this.$set(this.vdb_params.vdb[$index], 'editing', false)
      }
      this.tmpUsers = false
    },
    addTempVdb() {
      if (!this.tmpUsers) {
        this.vdb_params.vdb.unshift({
          type: '',
          id: '',
          num: '',
          method: '',
          partitions: '',
          editing: true
        })
        this.tmpUsers = true
      } else {
        this.$message({
          type: 'info',
          message: '请先完成已有数据!'
        })
      }
    },
    handleDeleteVdb($index, row) {
      this.$confirm('确认删除该分片信息？', '删除分片信息', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        changeParam(this.id, { 'type': 'sharding', 'data': this.vdb_params }).then(response => {
          this.vdb_params.vdb.splice($index, 1)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '删除失败!'
          })
        })
      })
    },
    handleEditTable($index, row) {
      this.$set(this.vdb_params.table[$index], 'editing', true)
    },
    handleSaveTable($index, row) {
      if (row.db && row.vdb && row.pkey && row.table) {
        changeParam(this.id, { 'type': 'sharding', 'data': this.vdb_params }).then(response => {
          row.originalDb = row.db
          row.originalVdb = row.vdb
          row.originalPkey = row.pkey
          row.originalTable = row.table
          this.$set(this.vdb_params.table[$index], 'editing', false)
          this.$message({
            type: 'success',
            message: '保存成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '保存失败，请输入正确值!'
          })
        })
      } else {
        this.$message({
          type: 'info',
          message: '请输入完整信息!'
        })
      }
      this.tmpUsers = false
    },
    handleCancelTable($index, row) {
      if (!row.originalDb) {
        this.vdb_params.table.splice($index, 1)
      } else {
        row.db = row.originalDb
        row.vdb = row.originalVdb
        row.pkey = row.originalPkey
        row.table = row.originalTable
        this.$set(this.vdb_params.table[$index], 'editing', false)
      }
      this.tmpUsers = false
    },
    addTempTable() {
      if (!this.tmpUsers) {
        this.vdb_params.table.unshift({
          db: '',
          vdb: '',
          pkey: '',
          table: '',
          editing: true
        })
        this.tmpUsers = true
      } else {
        this.$message({
          type: 'info',
          message: '请先完成已有数据!'
        })
      }
    },
    handleDeleteTable($index, row) {
      this.$confirm('确认删除该分片表？', '删除分片表', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.vdb_params.table.splice($index, 1)
        this.$message({
          type: 'success',
          message: '删除成功!'
        })
        changeParam(this.id, { 'type': 'sharding', 'data': this.vdb_params }).then(response => {
        })
      })
    },
    handleEditSingle($index, row) {
      this.$set(this.vdb_params.single_tables[$index], 'editing', true)
    },
    handleSaveSingle($index, row) {
      if (row.db && row.group && row.table) {
        changeParam(this.id, { 'type': 'sharding', 'data': this.vdb_params }).then(response => {
          row.originalDb = row.db
          row.originalGroup = row.group
          row.originalTable = row.table
          this.$set(this.vdb_params.single_tables[$index], 'editing', false)
          this.$message({
            type: 'success',
            message: '保存成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '保存失败，请输入正确值!'
          })
        })
      } else {
        this.$message({
          type: 'info',
          message: '请输入完整信息!'
        })
      }
      this.tmpUsers = false
    },
    handleCancelSingle($index, row) {
      if (!row.originalDb) {
        this.vdb_params.single_tables.splice($index, 1)
      } else {
        row.db = row.originalDb
        row.group = row.originalGroup
        row.table = row.originalTable
        this.$set(this.vdb_params.single_tables[$index], 'editing', false)
      }
      this.tmpUsers = false
    },
    addTempSingle() {
      if (!this.tmpUsers) {
        this.vdb_params.single_tables.unshift({
          db: '',
          group: '',
          table: '',
          editing: true
        })
        this.tmpUsers = true
      } else {
        this.$message({
          type: 'info',
          message: '请先完成已有数据!'
        })
      }
    },
    handleDeleteSingle($index, row) {
      this.$confirm('确认删除该单点表？', '删除单点表', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        changeParam(this.id, { 'type': 'sharding', 'data': this.vdb_params }).then(response => {
          this.vdb_params.single_tables.splice($index, 1)
          this.$message({
            type: 'success',
            message: '删除成功!'
          })
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '删除失败!'
          })
        })
      })
    }
  }
}
</script>

<style scoped>

</style>
