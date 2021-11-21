import { RequestStatus } from './../../models/requests.js';
import ArchiveComponent from './archive.js';
import ArchiveService from './../../services/archive-service.js';

export default Vue.component('archives', {
  data: function() {
    return {
      archiveEndpoints: [],
      isSaving: false,
      uploadedFiles: [],
      newArchive: null,
    }
  },
  created: function() {
    this.$store.dispatch('archives/getArchives');
    ArchiveService.getEndpoints().then(archiveEndpoints => {
      this.archiveEndpoints = archiveEndpoints;
    })
  },
  computed: {
    archives: function() {
      return this.$store.state.archives.archives;
    },
  },
  methods: {
    createArchive: function() {
      this.newArchive = {
        'key': '',
        'type': 'facebook',
        'description': '',
        'date_processed': null,
      };
    }
  },
  template: `
    <div id="archives">
      <h1>
        Archives
        <div class="input-group">
          <button class="button" @click="createArchive" v-if="!newArchive">New archive</button>
        </div>
      </h1>
      <ul class="archive-list">
        <li v-if="newArchive">
          <archive :archive="newArchive" :is-new="true" @save="newArchive = null" @cancel="newArchive = null"></archive>
        </li>
        <li v-for="archive in archives">
          <archive :archive="archive"></archive>
        </li>
      </ul>
    </div>
  `
});