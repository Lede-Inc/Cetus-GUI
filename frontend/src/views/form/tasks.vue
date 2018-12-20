<template>
  <div class="app-container">
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="Loading"
      border
      fit
      size="small"
      style="width: 100%">
      <el-table-column align="center" label="任务名称" width="200px">
        <template slot-scope="scope">
          {{ scope.row.name|taskFilter }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="任务id">
        <template slot-scope="scope">
          {{ scope.row.task_id }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="开始时间" width="200px">
        <template slot-scope="scope">
          {{ scope.row.tstamp|parseTime }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="任务状态" width="150px">
        <template slot-scope="scope">
          {{ scope.row.state }}
        </template>
      </el-table-column>
      <el-table-column align="center" label="运行总时间" width="150px">
        <template slot-scope="scope">
          {{ scope.row.runtime|timeFilter }} s
        </template>
      </el-table-column>
      <el-table-column label="详情" type="expand" width="150px">
        <template slot-scope="scope">
          <el-form label-position="left" class="demo-table-expand" size="small">
            <el-form-item label="参数列表">
              <span>{{ scope.row.kwargs }}</span>
            </el-form-item>
            <el-form-item label="返回结果">
              <span>{{ scope.row.result }}</span>
            </el-form-item>
            <el-form-item label="异常信息">
              <span style="white-space: pre-wrap">{{ scope.row.traceback }}</span>
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
  </div>
</template>

<script>
import { taskStatus } from '@/api/cetus'

export default {
  filters: {
    timeFilter(val) {
      return Number(val).toFixed(2)
    },
    taskFilter(task) {
      switch (task) {
        case 'install_cetus':
          return '安装Cetus服务'
        case 'install_node':
          return '安装Cetus节点'
        case 'upgrade_node':
          return '更新Cetus节点'
        default:
          return task
      }
    }
  },
  data() {
    return {
      list: null,
      total: null,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      taskStatus(this.listQuery).then(response => {
        this.list = response.data.results
        this.total = response.data.count
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
