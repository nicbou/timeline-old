import { RequestStatus } from './../models/requests.js';
import ArchiveService from './../services/archive-service.js';

export default Vue.component('archives', {
  data: function() {
    return {
      archiveEndpoints: [],
      isSaving: false,
      uploadedFiles: [],
    }
  },
  created: function() {
    this.$store.dispatch('archives/getArchives');
    ArchiveService.getArchiveEndpoints().then(archiveEndpoints => {
      this.archiveEndpoints = archiveEndpoints;
    })
  },
  computed: {
    archives: function() {
      return this.$store.state.archives.archives;
    },
    selectedArchive: function() {
      if(this.$route.name === 'archive-new') {
        return {
          archive_files: [],
          description: '',
          isNew: true,
          key: '',
          type: this.$route.params.type,
        };
      }
      return this.archives.find(a => a.type === this.$route.params.type && a.key === this.$route.params.key);
    },
  },
  methods: {
    archiveDisplayName: function(archiveType){
      return ArchiveService.getDisplayName(archiveType);
    },
    onFileInputChange: function(event) {
      this.uploadedFiles = this.$refs.fileInput.files;
    },
    relativeDate: function(date) {
      const duration = moment(date).diff(moment());
      return moment.duration(duration).humanize(true);
    },
    fileName: function(url){
      const segments = url.split('/');
      return segments.pop() || segments.pop();
    },
    updateArchive: function(archiveToSave) {
      this.isSaving = true;

      let saveArchivePromise = null;
      if(this.selectedArchive.isNew){
        saveArchivePromise = this.$store.dispatch('archives/createArchive', {archive: archiveToSave, files: this.uploadedFiles});
      }
      else {
        saveArchivePromise = this.$store.dispatch('archives/updateArchive', {archive: archiveToSave, newFiles: this.uploadedFiles});
      }

      saveArchivePromise.then(() => {
        this.isSaving = false;
        if(archiveToSave === this.selectedArchive){
          this.$refs.fileInput.value = "";
          this.uploadedFiles = [];
        }

        if(archiveToSave.isNew){
          this.$router.push({ name: 'archive-edit', params: { type: archiveToSave.type, key: archiveToSave.key }});
        }
      });
    },
    deleteArchive: function(archiveToDelete) {
      this.$store.dispatch('archives/deleteArchive', archiveToDelete).then(() => {
        if(this.selectedArchive === archiveToDelete){
          this.$router.push({ name: 'archives' });
        }
      });
    },
    deleteArchiveFile: function(fileId) {
      const archive = this.selectedArchive;
      ArchiveService.deleteArchiveFile(fileId).then(response => {
        archive.archive_files = archive.archive_files.filter(f => f.id !== fileId);
      });
    },
  },
  template: `
    <div id="archives">
      <header>
        <h1>Archives</h1>
        <router-link :to="{ name: 'timeline'}" title="Back to timeline" class="button back"><i class="fas fa-times"></i></router-link>
      </header>
      <div class="content-with-sidebar">
        <nav class="sidebar">
          <ul class="archive-list">
            <li>
              <router-link :to="{ name: 'archives' }">New archive</router-link>
            </li>
            <li v-for="archive in archives">
              <router-link :to="{ name: 'archive-edit', params: { type: archive.type, key: archive.key }}">
                <span class="name">{{ archive.key }}</span>
                <time v-if="archive.date_processed">Processed {{ relativeDate(archive.date_processed) }}</time>
                <span v-if="!archive.date_processed">Never processed</span>
              </router-link>
            </li>
          </ul>
        </nav>
        <main class="content">
          <div v-if="selectedArchive">
            <h1 v-if="!selectedArchive.isNew">Update archive</h1>
            <h1 v-if="selectedArchive.isNew">New archive</h1>
            <div class="input-group">
              <label for="archive-type">Type</label>
              <input type="text" id="archive-type" :value="archiveDisplayName(selectedArchive.type)" disabled/>
            </div>
            <div class="input-group">
              <label for="archive-key">Key</label>
              <input type="text" id="archive-key" v-model="selectedArchive.key" :disabled="!selectedArchive.isNew"/>
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
                    <i class="fas fa-check-circle"></i><span class="file-name">{{ fileName(archiveFile.url) }}</span>
                    <div class="actions">
                      <a :href="archiveFile.url" title="Download file"><i class="fas fa-download"></i></a>
                      <a href="#" @click.prevent="deleteArchiveFile(archiveFile.id)" title="Delete file"><i class="fas fa-trash"></i></a>
                    </div>
                  </li>
                  <li v-for="file in uploadedFiles">
                    <i class="fas fa-arrow-circle-up"></i><span class="file-name">{{ file.name }}</span>
                  </li>
                  <li>
                    <input type="file" ref="fileInput" id="archive-files" multiple @change="onFileInputChange">
                  </li>
                </ul>
              </div>
            </div>
            <div class="input-group" v-if="selectedArchive.isNew">
              <button :disabled="isSaving" class="button" @click="updateArchive(selectedArchive)">Create archive</button>
              <router-link class="button" :to="{name: 'archives'}">Cancel</router-link>
            </div>
            <div class="input-group" v-if="!selectedArchive.isNew">
              <button :disabled="isSaving" class="button" @click="updateArchive(selectedArchive)">Save changes</button>
              <button :disabled="isSaving" class="button" @click="deleteArchive(selectedArchive)">Delete archive</button>
            </div>
          </div>
          <div v-if="!selectedArchive">
            <h1>Create an archive</h1>
            <ul>
              <li v-for="url, archiveType in archiveEndpoints"><router-link :to="{ name: 'archive-new', params: { type: archiveType }}">{{ archiveDisplayName(archiveType) }}</router-link></li>
            </ul>
          </div>
        </main>
      </div>
    </div>
  `
});