import TimelineComponent from './components/timeline.js';
import ArchivesComponent from './components/settings/archives.js';
import SettingsComponent from './components/settings/settings.js';

export default new VueRouter({
  routes: [
    {
      path: '/settings',
      name: 'settings',
      component: SettingsComponent,
      children: [
        { path: 'archives', name: 'archives', component: ArchivesComponent },
      ],
    },
    { path: '/timeline', name: 'timeline', component: TimelineComponent },
    { path: '/', redirect: { name: 'timeline' }},
  ]
});