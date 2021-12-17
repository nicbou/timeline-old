import { RequestStatus } from './../../models/requests.js';
import ArchiveService from './../../services/archive-service.js';

export default Vue.component('settings', {
  data: function() {
    return {}
  },
  created: function() {
  },
  computed: {
  },
  methods: {
  },
  template: `
    <div id="settings">
      <header>
        <h1>Settings</h1>
        <router-link :to="{ name: 'timeline'}" title="Back to timeline" class="button back"><i class="fas fa-times"></i></router-link>
      </header>
      <div class="content-with-sidebar">
        <nav class="sidebar">
          <ul>
            <li><i class="icon fas fa-file-archive"></i> <router-link :to="{ name: 'archives'}">Archives</router-link></li>
            <li><i class="icon fas fa-sign-in-alt"></i> <router-link :to="{ name: 'sources'}">Sources</router-link></li>
            <li><i class="icon fas fa-sign-out-alt"></i> <router-link :to="{ name: 'archives'}">Destinations</router-link></li>
          </ul>
        </nav>
        <main class="content">
          <router-view></router-view>
        </main>
      </div>
    </div>
  `
});