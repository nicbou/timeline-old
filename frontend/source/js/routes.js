import TimelineComponent from './components/timeline.js';
import ArchivesComponent from './components/archives.js';

export default new VueRouter({
  routes: [
    { path: '/timeline', name: 'timeline', component: TimelineComponent },
    { path: '/archives', name: 'archives', component: ArchivesComponent },
    { path: '/', redirect: { name: 'timeline' }},
  ]
});