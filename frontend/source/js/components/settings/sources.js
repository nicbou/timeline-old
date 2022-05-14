import { RequestStatus } from './../../models/requests.js';
import SourceComponent from './source.js';
import SourceService from './../../services/source-service.js';

export default Vue.component('sources', {
  data: function() {
    return {
      sourceEndpoints: [],
      isSaving: false,
      uploadedFiles: [],
      newSource: null,
    }
  },
  created: function() {
    this.$store.dispatch('sources/getSources');
    SourceService.getSourceEndpoints().then(sourceEndpoints => {
      this.sourceEndpoints = sourceEndpoints;
    })
  },
  computed: {
    sources: function() {
      return this.$store.state.sources.sources;
    },
  },
  methods: {
    createSource: function() {
      this.newSource = {
        'key': '',
        'type': 'trakt',
        'description': '',
        'date_processed': null,
      };
    }
  },
  template: `
    <div id="Sources">
      <h1>
        Sources
        <!--<div class="input-group">
          <button class="button" @click="createSource" v-if="!newSource">New source</button>
        </div>-->
      </h1>
      <ul class="archive-list">
        <li v-if="newSource">
          <source-data :source="newSource" :is-new="true" @save="newSource = null" @cancel="newSource = null"></source-data>
        </li>
        <li v-for="source in sources">
          <source-data :source="source"></source-data>
        </li>
      </ul>
    </div>
  `
});