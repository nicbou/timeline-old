import archivesStore from './archives.js';
import authStore from './auth.js';
import sourcesStore from './sources.js';
import timelineStore from './timeline.js';

export default new Vuex.Store({
  modules: {
    archives: archivesStore,
    auth: authStore,
    sources: sourcesStore,
    timeline: timelineStore,
  },
});