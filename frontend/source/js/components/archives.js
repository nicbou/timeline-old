import { RequestStatus } from './../models/requests.js';

export default Vue.component('archives', {
  created: function() {
    this.$store.dispatch('archives/getArchives');
  },
  computed: {
    archives: function() {
      return this.$store.state.archives.archives;
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
              {{ archive.key }}
            </li>
          </ul>
        </nav>
        <main class="archive-editor content">
          Hello
        </main>
      </div>
    </div>
  `
});