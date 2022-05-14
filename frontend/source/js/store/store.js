import timelineStore from './timeline.js';
import archivesStore from './archives.js';
import sourcesStore from './sources.js';

export default new Vuex.Store({
  modules: {
    timeline: timelineStore,
    archives: archivesStore,
    sources: sourcesStore,
  },
});