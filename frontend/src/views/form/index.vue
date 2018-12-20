<template>
  <div class="app-container">
    <el-form ref="cetusForm" :model="cetus" :rules="rules" label-width="140px" >
      <el-form-item label="Cetus名称" prop="cetus_name">
        <el-input v-model="cetus.cetus_name"/>
      </el-form-item>
      <el-form-item label="Cetus类型" prop="cetus_type">
        <el-radio-group v-model="cetus.cetus_type">
          <el-radio label="rw">读写分离</el-radio>
          <el-radio label="shard">分片</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="版本号" prop="version">
        <el-input v-model="cetus.version" placeholder="不填默认选择最新版本"/>
      </el-form-item>
      <el-form-item
        v-for="(node,index) in cetus.nodes"
        :label="'Cetus节点'+(index+1)"
        :key="node.key"
        :prop="'nodes.' + index + '.salt_id'"
        :rules="{required: true, message: 'SALT ID不能为空', trigger: 'blur'}">
        <el-input v-model="node.salt_id" placeholder="SALT ID" />
        <el-button v-if="index==0" :span="4" type="primary" size="small" @click.prevent="addNode">增加新节点</el-button>
        <el-button v-if="index!=0" :span="4" type="danger" size="small" @click.prevent="removeNode(node)">删除该节点</el-button>
      </el-form-item>
      <el-form-item label="端口信息" required>
        <el-col :span="11">
          <el-form-item prop="service_port">
            <el-input v-model.number="cetus.service_port" placeholder="服务端口"/>
          </el-form-item>
        </el-col>
        <el-col :span="2" class="line">&nbsp;</el-col>
        <el-col :span="11">
          <el-form-item prop="admin_port">
            <el-input v-model.number="cetus.admin_port" placeholder="管理端口"/>
          </el-form-item>
        </el-col>
      </el-form-item>
      <el-form-item label="安装目录" prop="path">
        <el-input v-model="cetus.path" placeholder="默认为/home目录"/>
      </el-form-item>
      <el-form-item label="管理文件配置" prop="control">
        <el-radio-group v-model="cetus.control">
          <el-radio label="remote">远程统一管理</el-radio>
          <el-radio label="local" disabled>本地单独管理</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="submitForm('cetusForm')">创建</el-button>
        <el-button @click="resetForm('cetusForm')">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import { installCetus } from '@/api/cetus'

export default {
  data() {
    return {
      cetus: {
        cetus_name: '',
        cetus_type: '',
        version: '',
        nodes: [{
          salt_id: ''
        }],
        service_port: '',
        admin_port: '',
        path: '',
        control: ''
      },
      rules: {
        cetus_name: [{ required: true, message: '名称不能为空', trigger: 'blur' }],
        cetus_type: [{ required: true, message: '类型不能为空', change: 'blur' }],
        service_port: [{ required: true, message: '端口不能为空', trigger: 'blur' },
          { type: 'number', message: '端口需要是数字', trigger: 'blur' }],
        admin_port: [{ required: true, message: '端口不能为空', trigger: 'blur' },
          { type: 'number', message: '端口需要是数字', trigger: 'blur' }],
        control: [{ required: true, message: '类型不能为空', change: 'blur' }]
      }
    }
  },
  methods: {
    submitForm(formName) {
      this.$refs[formName].validate((valid) => {
        if (valid) {
          this.$confirm('确认安装Cetus服务？', '安装Cetus服务', {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }).then(() => {
            const loading = this.$loading({})
            installCetus(this.cetus).then(response => {
              loading.close()
              this.$message({
                message: response.data,
                type: 'success',
                onClose: () => {
                  this.$router.push({ path: '/cetus' })
                }
              })
            }).catch(() => {
              loading.close()
              this.$message({
                message: '安装失败',
                type: 'error'
              })
            })
          })
        } else {
          return false
        }
      })
    },
    resetForm(formName) {
      this.$refs[formName].resetFields()
    },
    removeNode(item) {
      var index = this.cetus.nodes.indexOf(item)
      if (index !== -1) {
        this.cetus.nodes.splice(index, 1)
      }
    },
    addNode() {
      this.cetus.nodes.push({
        value: '',
        key: Date.now()
      })
    }
  }
}
</script>

<style scoped>
.el-form {
  width: 550px;
}
.el-input {
  max-width: 270px;
}
.line {
  text-align: center;
}
</style>

