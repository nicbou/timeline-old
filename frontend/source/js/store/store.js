import timelineStore from './timeline.js';
import archivesStore from './archives.js';

export default new Vuex.Store({
  modules: {
    timeline: timelineStore,
    archives: archivesStore,
  },
});