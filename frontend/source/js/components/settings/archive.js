import { RequestStatus } from './../../models/requests.js';
import { archiveTypes } from './../../services/archive-service.js';

export default Vue.component('archive', {
  props: ['archive', 'isNew'],
  data: function() {
    return {
      isEditing: false,
      isSaving: false,
      uploadedFiles: [],
      archiveTypes: archiveTypes,
    }
  },
  computed: {
    formattedDateFrom: {
      get: function() {
        return this.archive.date_from ? this.archive.date_from.substring(0, 16) : null;
      },
      set: function(value) {
        this.archive.date_from = value ? value + ':00Z' : null;
      }
    },
    formattedDateUntil: {
      get: function() {
        return this.archive.date_until ? this.archive.date_until.substring(0, 16) : null;
      },
      set: function(value) {
        this.archive.date_until = value ? value + ':00Z' : null;
      }
    },
    formattedDateProcessed: {
      get: function() {
        return this.archive.date_processed ? this.archive.date_processed.substring(0, 16) : null;
      },
      set: function(value) {
        this.archive.date_processed = value ? value + ':00Z' : null;
      }
    },
  },
  methods: {
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
    updateArchive: function() {
      this.isSaving = true;

      let saveArchivePromise = null;
      if(this.isNew){
        saveArchivePromise = this.$store.dispatch('archives/createArchive', {archive: this.archive, files: this.uploadedFiles});
      }
      else {
        saveArchivePromise = this.$store.dispatch('archives/updateArchive', {archive: this.archive, newFiles: this.uploadedFiles});
      }

      saveArchivePromise.then(() => {
        this.isEditing = false;
        this.isSaving = false;
        this.$refs.fileInput.value = "";
        this.uploadedFiles = [];
        this.$emit('save', this.archive);
      });
    },
    cancelChanges: function() {
      this.isEditing = false;
      this.$emit('cancel', this.archive);
    },
    deleteArchive: function() {
      this.$store.dispatch('archives/deleteArchive', this.archive);
    },
    deleteArchiveFile: function(fileId) {
      this.$store.dispatch('archives/deleteArchiveFile', fileId).then(response => {
        this.archive.archive_files = archive.archive_files.filter(f => f.id !== fileId);
      });
    },
  },
  template: `
    <div class="archive">
      <div class="archive-preview form" :class="{processed: !!archive.date_processed}" v-if="!isEditing && !isNew">
        <i class="icon fas fa-file-archive"></i>
        <div class="archive-details">
          <h2>{{ archive.key || 'New archive' }}</h2>
          {{ archiveTypes[this.archive.type] }}.
          <span v-if="!!archive.date_processed">Processed {{ relativeDate(archive.date_processed) }}.</span>
          <span v-if="!archive.date_processed">Not yet processed.</span>
        </div>
        <div class="input-group">
          <button class="button" @click="isEditing=true">Edit</button>
        </div>
      </div>
      <div v-if="isEditing || isNew" class="form">
        <div class="input-group">
          <label for="archive-type">Type</label>
          <input type="text" :value="archiveTypes[archive.type]" disabled v-if="!isNew"/>
          <select id="archive-type" v-model="archive.type" v-if="isNew">
            <option v-for="(archiveTypeDisplay, archiveType) in archiveTypes" :value="archiveType" :key="archiveType">{{ archiveTypeDisplay }}</option>
          </select>
        </div>
        <div class="input-group">
          <label for="archive-key">Key</label>
          <input type="text" id="archive-key" v-model="archive.key" v-if="isNew"/>
          <router-link title="Show entries on the timeline" class="fake-input" :to="{ name: 'timeline', query: { source: archive.type + '/' + archive.key}}" v-if="!isNew">
            {{ archive.type }}/{{ archive.key }}
          </router-link>
        </div>
        <div class="input-group">
          <label for="archive-description">Description</label>
          <textarea id="archive-description" v-model="archive.description"></textarea>
        </div>
        <div class="input-group">
          <label for="archive-key">Date from</label>
          <input type="datetime-local" name="date-from" v-model="formattedDateFrom">
        </div>
        <div class="input-group">
          <label for="archive-key">Date to</label>
          <input type="datetime-local" name="date-until" v-model="formattedDateUntil">
        </div>
        <div class="input-group">
          <label for="archive-files">Files</label>
          <div class="files-input">
            <ul>
              <li v-for="archiveFile in archive.archive_files" :key="archiveFile.id">
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
        <div class="input-group">
          <label for="archive-key">Date processed</label>
          <input type="datetime-local" name="date-until" v-model="formattedDateProcessed"/>
        </div>
        <div class="input-group" v-if="isNew">
          <button :disabled="isSaving || !(archive.key && archive.description)" class="button" @click="updateArchive">Create archive</button>
          <button :disabled="isSaving" class="button" @click="cancelChanges">Cancel</button>
        </div>
        <div class="input-group" v-if="!isNew">
          <button :disabled="isSaving || !(archive.key && archive.description)" class="button" @click="updateArchive">Save changes</button>
          <button :disabled="isSaving" class="button" @click="deleteArchive">Delete archive</button>
          <button :disabled="isSaving" class="button" @click="cancelChanges">Cancel</button>
        </div>
      </div>
    </div>
  `
});