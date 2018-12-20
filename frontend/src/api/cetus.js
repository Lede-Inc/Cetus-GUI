import request from '@/utils/request'

export function cetusList(query) {
  return request({
    url: '/api/cetus/',
    method: 'get',
    params: query
  })
}

export function cetusItem(id) {
  return request({
    url: `/api/cetus/${id}/`,
    method: 'get'
  })
}

export function updateCetus(id, data) {
  return request({
    url: `/api/cetus/${id}/`,
    method: 'patch',
    data
  })
}

export function installCetus(data) {
  return request({
    url: '/api/cetus/install/',
    method: 'post',
    data
  })
}

export function manageCetus(id, data) {
  return request({
    url: `/api/cetus/${id}/command/`,
    method: 'post',
    data
  })
}

export function paramCetus(id, data) {
  return request({
    url: `/api/cetus/${id}/param/`,
    method: 'get',
    params: data
  })
}

export function changeParam(id, data) {
  return request({
    url: `/api/cetus/${id}/param/`,
    method: 'post',
    data
  })
}

export function addCetusNode(data) {
  return request({
    url: `/api/node/install/`,
    method: 'post',
    data
  })
}

export function upgradeNode(id, data) {
  return request({
    url: `/api/node/${id}/upgrade/`,
    method: 'post',
    data
  })
}

export function upgradeCetus(id, data) {
  return request({
    url: `/api/cetus/${id}/upgrade/`,
    method: 'post',
    data
  })
}

export function removeNode(id) {
  return request({
    url: `/api/node/${id}/remove/`,
    method: 'post'
  })
}

export function removeCetus(id) {
  return request({
    url: `/api/cetus/${id}/remove/`,
    method: 'post'
  })
}

export function operateNode(id, data) {
  return request({
    url: `/api/node/${id}/operate/`,
    method: 'post',
    data
  })
}

export function operateCetus(id, data) {
  return request({
    url: `/api/cetus/${id}/operate/`,
    method: 'post',
    data
  })
}

export function monitorNode(id, data) {
  return request({
    url: `/api/node/${id}/monitor/`,
    method: 'get',
    params: data
  })
}

export function taskStatus(query) {
  return request({
    url: `/api/task/`,
    method: 'get',
    params: query
  })
}
