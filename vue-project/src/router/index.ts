import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'landing-page',
            component: () => import('../views/LandingPageView.vue')
        },
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/create-account',
            name: 'create-account',
            component: () => import('../views/CreateAccountView.vue')
        },
        {
            path: '/create-new-game',
            name: 'create-new-game',
            component: () => import('../views/CreateNewGameView.vue')
        },
        {
            path: '/active-game',
            name: 'active-game',
            component: () => import('../views/ActiveGameView.vue')
        }
    ]
})

export default router
