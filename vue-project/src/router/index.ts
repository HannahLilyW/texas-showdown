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
        },
        {
            path: '/join-existing-game',
            name: 'join-existing-game',
            component: () => import('../views/JoinExistingGameView.vue')
        },
        {
            path: '/view-completed-games',
            name: 'view-completed-games',
            component: () => import('../views/ViewCompletedGamesView.vue')
        },
        {
            path: '/view-completed-game/:id',
            name: 'view-completed-game',
            component: () => import('../views/ViewCompletedGameView.vue'),
            props: true
        },
        {
            path: '/view-player-statistics',
            name: 'view-player-statistics',
            component: () => import('../views/ViewPlayerStatisticsView.vue')
        },
        {
            path: '/edit-profile/:next',
            name: 'edit-profile',
            component: () => import('../views/EditProfileView.vue'),
            props: true
        },
        {
            path: '/join-private-game',
            name: 'join-private-game',
            component: () => import('../views/JoinPrivateGameView.vue')
        },
        {
            path: '/solo-play',
            name: 'solo-play',
            component: () => import('../views/SoloPlayView.vue')
        }
    ]
})

export default router
