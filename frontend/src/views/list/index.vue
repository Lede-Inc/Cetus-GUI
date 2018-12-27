<template>
  <div class="app-container">
    <el-form :inline="true" :model="listQuery">
      <el-form-item label="服务名称：">
        <el-input v-model="listQuery.cetus_name" size="small" @keyup.enter.native="handleFilter"/>
      </el-form-item>
      <el-form-item label="类型">
        <el-select v-model="listQuery.cetus_type" clearable size="small" placeholder="" @change="handleFilter" >
          <el-option label="读写分离" value="rw"/>
          <el-option label="分片" value="shard"/>
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="listQuery.status" clearable size="small" placeholder="" @change="handleFilter">
          <el-option label="运行中" value="运行中"/>
          <el-option label="已关闭" value="已关闭"/>
          <el-option label="部分运行" value="部分运行"/>
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" size="small" @click="handleFilter">查询</el-button>
      </el-form-item>
    </el-form>
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      size="small">
      <el-table-column align="center" label="Cetus名称">
        <template slot-scope="scope">
          {{ scope.row.cetus_name }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="Cetus类型">
        <template slot-scope="scope">
          {{ scope.row.cetus_type|typeFilter }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="配置库">
        <template slot-scope="scope">
          <div v-if="scope.row.config_db"><span>{{ scope.row.config_db }}</span></div>
          <div v-else><span>暂无</span></div>
        </template>
      </el-table-column>
      <el-table-column align="center" label="Cetus节点数">
        <template slot-scope="scope">
          <span>{{ scope.row.nodes.length }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="状态">
        <template slot-scope="scope">
          <span>{{ scope.row.status }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="创建时间">
        <template slot-scope="scope">
          <span>{{ scope.row.create_time|parseTime }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template slot-scope="scope">
          <el-button v-if="!scope.row.config_db" type="text" size="small" @click="installing">查看</el-button>
          <router-link v-else :to="{name:'Item', params:{id:scope.row.id}}"><el-button type="text" size="small" style="padding-right: 10px;">查看</el-button></router-link>
          <el-button type="text" size="small" @click="handleEdit(scope.row)">编辑</el-button>
        </template>
      </el-table-column>
      <el-table-column type="expand">
        <template slot-scope="scope">
          <el-form v-for="(prop,index) in scope.row.nodes" :key="prop.key" label-position="left" inline class="demo-table-expand" size="small">
            <el-form-item :label="'节点'+(index+1)">
              <span>{{ prop.salt_id }}:{{ prop.service_port }}/{{ prop.admin_port }}</span>
            </el-form-item>
            <el-form-item label="版本">
              <span>{{ prop.version }}</span>
            </el-form-item>
            <el-form-item label="状态">
              <span>{{ prop.status|statusFilter }}</span>
            </el-form-item>
            <el-form-item label="创建时间">
              <span>{{ prop.create_time|parseTime }}</span>
            </el-form-item>
            <el-form-item label="最近更新时间">
              <span v-if="prop.update_time">{{ prop.update_time|parseTime }}</span>
              <span v-else>暂无</span>
            </el-form-item>
          </el-form>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-container">
      <el-pagination
        :current-page="listQuery.page"
        :page-sizes="[10,20,30,50]"
        :page-size="listQuery.limit"
        :total="total"
        background
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange" />
    </div>

    <el-dialog :visible.sync="dialogChangeConfig" title="Edit">
      <el-form ref="dataForm" :rules="rules" :model="listEdit" label-position="left" label-width="140px" style="width: 400px; margin-left:50px;">
        <el-form-item label="Cetus名称">
          <el-input v-model="listEdit.cetus_name" class="filter-item" size="small" />
        </el-form-item>
        <el-form-item label="配置库">
          <el-input v-model="listEdit.config_db" class="filter-item" size="small" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button type="primary" @click="updateInfo">确定</el-button>
        <el-button @click="dialogChangeConfig = false">取消</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
import { cetusList, updateCetus } from '@/api/cetus'

export default {
  data() {
    return {
      list: null,
      total: null,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        cetus_name: undefined,
        cetus_type: undefined,
        status: undefined
      },
      listEdit: {
        id: undefined,
        cetus_name: undefined,
        config_db: undefined
      },
      dialogChangeConfig: false,
      rules: {
        type: [{ required: true, message: 'type is required', trigger: 'change' }],
        timestamp: [{ type: 'date', required: true, message: 'timestamp is required', trigger: 'change' }],
        title: [{ required: true, message: 'title is required', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      cetusList(this.listQuery).then(response => {
        this.list = response.data.results
        this.list = this.list.filter(v => {
          let statusFlag = 0
          for (const item of v.nodes) {
            if (item.status === 0) statusFlag = statusFlag + 1
            if (item.status === 1) {
              v.status = '安装中'
              return v
            }
            if (item.status === 2) {
              v.status = '更新中'
              return v
            }
          }
          if (statusFlag === v.nodes.length) v.status = '运行中'
          if (statusFlag && statusFlag < v.nodes.length) v.status = '部分运行'
          if (statusFlag === 0) v.status = '已关闭'
          if (this.listQuery.status && this.listQuery.status !== v.status) return false
          return v
        })
        this.total = response.data.count
        this.listLoading = false
      }).catch(() => {
        this.$message({
          type: 'error',
          message: '数据读取失败'
        })
        this.listLoading = false
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleSizeChange(val) {
      this.listQuery.limit = val
      this.getList()
    },
    handleCurrentChange(val) {
      this.listQuery.page = val
      this.getList()
    },
    handleEdit(row) {
      Object.assign(this.listEdit, row)
      this.dialogChangeConfig = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateInfo() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.listEdit)
          console.log(tempData)
          updateCetus(tempData.id, tempData).then(() => {
            for (const v of this.list) {
              if (v.id === this.listEdit.id) {
                const index = this.list.indexOf(v)
                this.list.splice(index, 1, this.listEdit)
                break
              }
            }
            this.dialogChangeConfig = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    installing() {
      this.$message({
        message: '正在安装中，请耐心等待~'
      })
    }
  }
}
</script>

<style scoped>
.el-table thead th {
  background: #f5f7fa;
}
.el-form-item__label {
  font-size: 12px;
}
.el-form-item__content {
  font-size: 12px;
}
.pagination-container {
  margin-top: 10px;
  float: right;
}
</style>
