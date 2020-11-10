import SpinnerComponent from './spinner.js';
import TimelineNav from './timeline-nav.js';
import TimelineTile from './timeline-tile.js';
import Preview from './preview.js';
import { RequestStatus } from './../models/requests.js';

function makeRouteValid(to, from, next) {
  if (to.query.date) {
    const newDate = moment(to.query.date, 'YYYY-MM-DD', true);
    if(newDate.isValid()) {
      next();
      return;
    }
  }
  next({
    name: 'timeline', query: { date: moment().format('YYYY-MM-DD') }
  });
}

export default Vue.component('timeline', {
  data: function() {
    return {
      selectedEntry: null,
      modalVisible: null,
    }
  },
  created: function() {
    this.$store.dispatch('timeline/getEntries');
  },
  watch: {
    '$route.query.date': function() {
      this.$store.dispatch('timeline/getEntries', true)
    }
  },
  beforeRouteEnter: makeRouteValid,
  beforeRouteUpdate: makeRouteValid,
  computed: {
    timelineDate: function(){
      return moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true);
    },
    relativeTimelineDate: function() {
      const duration = this.timelineDate.diff(moment().startOf('day'));
      return duration !== 0 ? moment.duration(duration).humanize(true) : 'today';
    },
    entries: function() {
      return this.$store.state.timeline.entries;
    },
    isLoading: function() {
      return this.$store.state.timeline.entriesRequestStatus === RequestStatus.PENDING;
    },
  },
  methods: {
    selectTile: function(entry) {
      this.selectedEntry = entry;
      this.modalVisible = true;
    },
    closeTile: function() {
      this.modalVisible = false;
      this.selectedEntry = null;
    }
  },
  template: `
    <div>
      <div class="container">
        <h1>{{ timelineDate.format('LL') }}</h1>
        <span class="subtitle">{{ relativeTimelineDate }}</span>
        <timeline-nav id="timeline-nav"></timeline-nav>
      </div>
      <div class="container wide">
        <spinner v-if="isLoading"></spinner>
        <div class="tiles">
          <tile :entry="entry" v-for="entry in entries" :key="entry.id" @click="selectTile"></tile>
        </div>
      </div>
      <preview :entry="selectedEntry" v-if="modalVisible" @close="closeTile"></preview>
    </div>
  `
});