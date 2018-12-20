export function parseTime(time, cFormat) {

  // if (arguments.length === 0) {
  //   return null
  // }
  // const format = cFormat || '{y}-{m}-{d} {h}:{i}:{s}'
  // let date
  // if (typeof time === 'object') {
  //   date = time
  // } else {
  //   if (('' + time).length === 10) {
  //     time = parseInt(time) * 1000
  //   }
  //   date = new Date(time)
  // }
  // const formatObj = {
  //   y: date.getFullYear(),
  //   m: date.getMonth() + 1,
  //   d: date.getDate(),
  //   h: date.getHours(),
  //   i: date.getMinutes(),
  //   s: date.getSeconds(),
  //   a: date.getDay()
  // }
  // const time_str = format.replace(/{(y|m|d|h|i|s|a)+}/g, (result, key) => {
  //   let value = formatObj[key]
  //   // Note: getDay() returns 0 on Sunday
  //   if (key === 'a') { return ['日', '一', '二', '三', '四', '五', '六'][value ] }
  //   if (result.length > 0 && value < 10) {
  //     value = '0' + value
  //   }
  //   return value || 0
  // })
  // console.log(time)
  // console.log(typeof time)
  const time_str = time.substr(0, 19).replace('T', ' ')
  return time_str
}

export function formatTime(time, option) {
  time = +time * 1000
  const d = new Date(time)
  const now = Date.now()

  const diff = (now - d) / 1000

  if (diff < 30) {
    return '刚刚'
  } else if (diff < 3600) {
    // less 1 hour
    return Math.ceil(diff / 60) + '分钟前'
  } else if (diff < 3600 * 24) {
    return Math.ceil(diff / 3600) + '小时前'
  } else if (diff < 3600 * 24 * 2) {
    return '1天前'
  }
  if (option) {
    return parseTime(time, option)
  } else {
    return (
      d.getMonth() +
      1 +
      '月' +
      d.getDate() +
      '日' +
      d.getHours() +
      '时' +
      d.getMinutes() +
      '分'
    )
  }
}

export function statusFilter(status) {
  const statusMap = {
    '0': '运行中',
    '1': '创建中',
    '-1': '关闭',
    '-2': '关闭中',
    '2': '更新中',
    '3': '启动中'
  }
  return statusMap[status]
}

export function typeFilter(type) {
  const typeMap = {
    'rw': '读写分离版',
    'shard': '分片版'
  }
  return typeMap[type]
}
