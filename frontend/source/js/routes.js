import TimelineComponent from './components/timeline.js';

export default new VueRouter({
  routes: [
    { path: '/timeline', name: 'timeline', component: TimelineComponent },
    { path: '/', redirect: { name: 'timeline' }},
  ]
});