import Vue from 'vue'
import Router from 'vue-router'

// in development-env not use lazy-loading, because lazy-loading too many pages will cause webpack hot update too slow. so only in production use lazy-loading;

Vue.use(Router)

/* Layout */
import Layout from '../views/layout/Layout'

/**
* hidden: true                   if `hidden:true` will not show in the sidebar(default is false)
* alwaysShow: true               if set true, will always show the root menu, whatever its child routes length
*                                if not set alwaysShow, only more than one route under the children
*                                it will becomes nested mode, otherwise not show the root menu
* redirect: noredirect           if `redirect:noredirect` will no redirect in the breadcrumb
* name:'router-name'             the name is used by <keep-alive> (must set!!!)
* meta : {
    title: 'title'               the name show in submenu and breadcrumb (recommend set)
    icon: 'svg-name'             the icon show in the sidebar,
  }
**/
export const constantRouterMap = [
  { path: '/login', component: () => import('@/views/login/index'), hidden: true },
  { path: '/404', component: () => import('@/views/404'), hidden: true },

  {
    path: '/',
    component: Layout,
    redirect: '/cetus',
    hidden: true
  },

  {
    path: '/cetus',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Cetus',
        component: () => import('@/views/list/index'),
        meta: { title: 'Cetus列表', icon: 'table' }
      },
      {
        path: '/cetus/:id',
        name: 'Item',
        component: () => import('@/views/item/index'),
        meta: { title: 'Cetus详情', icon: 'table' },
        hidden: true
      }
    ]
  },

  {
    path: '/install',
    component: Layout,
    children: [
      {
        path: 'cetus',
        name: 'Install',
        component: () => import('@/views/form/index'),
        meta: { title: 'Cetus安装', icon: 'clipboard' }
      }
    ]
  },

  {
    path: '/tasks',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Tasks',
        component: () => import('@/views/form/tasks'),
        meta: { title: '任务列表', icon: 'form' }
      }
    ]
  },

  {
    path: '/docs',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Docs',
        component: () => import('@/views/docs/index'),
        meta: { title: '使用说明', icon: 'documentation' }
      }
    ]
  },

  {
    path: '/links',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Links',
        component: () => import('@/views/link/index'),
        meta: { title: '友情链接', icon: 'link' }
      }
    ]
  },
  { path: '*', redirect: '/404', hidden: true }
]

export default new Router({
  // mode: 'history', //后端支持可开
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})
