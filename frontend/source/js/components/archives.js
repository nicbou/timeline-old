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
      <nav>
        Archives
      </nav>
      <div class="content-with-sidebar">
        <div class="sidebar">
          <ul>
            <li v-for="archive in archives">
              {{ archive.key }}
            </li>
          </ul>
        </div>
        <main class="archive-editor">
          Hello
        </main>
      </div>
    </div>
  `
});