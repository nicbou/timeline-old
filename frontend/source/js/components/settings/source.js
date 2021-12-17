import { sourceTypes } from './../../services/source-service.js';
import sourceTrakt from './sourceTrakt.js'

export default Vue.component('source-data', {
  props: ['source', 'isNew'],
  data: function() {
    return {
      sourceTypes: sourceTypes,
    }
  },
  template: `
    <div class="archive">
      <div class="archive-preview">
        <div class="archive-details">
          <h2>{{ sourceTypes[this.source.type] }} source - {{ this.source.key }}</h2>
        </div>
      </div>
      <source-trakt :source="source" v-if="this.source.type == 'trakt'"></source-trakt>
    </div>
    `
});