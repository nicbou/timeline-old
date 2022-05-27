import TimelineComponent from './components/timeline.js';
import ArchivesComponent from './components/settings/archives.js';
import SettingsComponent from './components/settings/settings.js';
import SourcesComponent  from './components/settings/sources.js';
import store from './store/store.js';


const router = new VueRouter({
  mode: 'history',
  routes: [
    {
      path: '/settings',
      name: 'settings',
      component: SettingsComponent,
      children: [
        { path: 'archives', name: 'archives', component: ArchivesComponent },
        { path: 'sources', name: 'sources', component: SourcesComponent },
      ],
      meta: { requiresAuth: true },
    },
    {
      path: '/timeline',
      name: 'timeline',
      component: TimelineComponent,
      meta: { requiresAuth: true },
    },
    {
      name: 'login',
      path: '/login',
      async beforeEnter(to, from, next) {
        window.location.replace(await store.dispatch('auth/getAuthorizationCodeUrl'));
      }
    },
    {
      path: '/',
      redirect: { name: 'timeline' }
    },
    {
      name: 'oauth-redirect',
      path: '/oauth-redirect',
      beforeEnter: async (to, from, next) => {
        if(to.query.code) {
          store.dispatch('auth/getToken', to.query.code).then(_ => next({ name: 'timeline' }));
        }
        else {
          next({ name: 'login' });
        }
      },
    }
  ]
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    if(store.state.auth.accessToken === null) {
      next({ name: 'login' }); // TODO: remember path
    }
    else {
      next();
    }
  }
  else {
    next();
  }
});

export default router;
