import { RequestStatus } from './../models/requests.js';

export default Vue.component('archives', {
  data: function() {
    return {
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
  },
  template: `
    <div id="archives">
      <header>
        Archives
      </header>
      <div class="content-with-sidebar">
        <nav class="sidebar">
          <ul>
            <li v-for="archive in archives">
              <router-link :to="{ name: 'archive', params: { type: archive.type, key: archive.key }}">{{ archive.key }}</router-link>
            </li>
          </ul>
        </nav>
        <main class="archive-editor content">
          <div v-if="selectedArchive">
            {{ selectedArchive.key }}
          </div>
        </main>
      </div>
    </div>
  `
});