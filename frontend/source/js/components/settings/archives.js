import { RequestStatus } from './../../models/requests.js';
import ArchiveComponent from './archive.js';

export default Vue.component('archives', {
  data: function() {
    return {
      isSaving: false,
      uploadedFiles: [],
      newArchive: null,
    }
  },
  created: function() {
    this.$store.dispatch('archives/getArchives').catch(response => {
      if([401, 403].includes(response.status)) {
        this.$router.push({name: 'login'});
      }
    });
    this.$store.dispatch('archives/getArchiveEndpoints');
  },
  computed: {
    archives: function() {
      return this.$store.state.archives.archives;
    },
    archiveEndpoints: function() {
      return this.$store.state.archives.archiveEndpoints;
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
        <li v-for="archive in archives" :key="archive.key">
          <archive :archive="archive"></archive>
        </li>
      </ul>
    </div>
  `
});