import { RequestStatus } from './../models/requests.js';

export default Vue.component('archives', {
  data: function() {
    return {
      uploadedFiles: [],
    }
  },
  created: function() {
    this.$store.dispatch('archives/getArchives');
  },
  computed: {
    archives: function() {
      return this.$store.state.archives.archives;
    },
    selectedArchive: function() {
      return this.archives.find(a => a.type === this.$route.params.type && a.key === this.$route.params.key);
    },
  },
  methods: {
    onFileInputChange: function(event) {
      this.uploadedFiles = event.target.files;
    },
  },
  template: `
    <div id="archives">
      <header>
        <router-link :to="{ name: 'timeline'}" title="Back to timeline" class="button back"><i class="fas fa-arrow-left"></i></router-link>
        <h1>Archives</h1>
      </header>
      <div class="content-with-sidebar">
        <nav class="sidebar">
          <ul class="archive-list">
            <li v-for="archive in archives">
              <router-link :to="{ name: 'archive', params: { type: archive.type, key: archive.key }}">{{ archive.key }}</router-link>
            </li>
          </ul>
        </nav>
        <main class="content">
          <div v-if="selectedArchive">
            <div class="input-group">
              <label for="archive-key">Key</label>
              <input type="text" id="archive-key" v-model="selectedArchive.key"/>
            </div>
            <div class="input-group">
              <label for="archive-description">Description</label>
              <textarea id="archive-description" v-model="selectedArchive.description"></textarea>
            </div>
            <div class="input-group">
              <label for="archive-files">Files</label>
              <div class="files-input">
                <ul>
                  <li v-for="archiveFile in selectedArchive.archive_files">
                    <i class="fas fa-check-circle"></i><span class="file-name">{{ archiveFile }}</span>
                    <div class="actions">
                      <a href="" title="Download file"><i class="fas fa-download"></i></a>
                      <a href="" title="Delete file"><i class="fas fa-trash"></i></a>
                    </div>
                  </li>
                  <li v-for="file in uploadedFiles">
                    <i class="fas fa-arrow-circle-up"></i><span class="file-name">{{ file.name }}</span>
                  </li>
                  <li>
                    <input type="file" id="archive-files" multiple @change="onFileInputChange">
                  </li>
                </ul>
              </div>
            </div>
            <div class="input-group">
              <button class="button">Save changes</button>
              <button class="button">Delete archive</button>
            </div>
          </div>
        </main>
      </div>
    </div>
  `
});