import SpinnerComponent from './spinner.js';
import TimelineNav from './timeline-nav.js';
import { RequestStatus } from './../models/requests.js';

export default Vue.component('timeline', {
  data: function() {
    return {}
  },
  computed: {
    timelineDate: function(){
      return this.$store.state.timeline.timelineDate;
    },
    relativeTimelineDate: function() {
      return moment.duration(this.timelineDate.diff(moment().startOf('day'))).humanize(true);
    },
    entries: function() {
      return this.$store.state.timeline.entries;
    },
    isLoading: function() {
      return this.$store.state.timeline.entriesRequestStatus === RequestStatus.PENDING;
    },
  },
  created: function () {
    this.$store.dispatch('timeline/getEntries');
  },
  methods: {
    pickTimelineDate: function(event) {
      this.timelineDate = moment(event.target.valueAsNumber);
    },
    moveTimelineDate: function(quantity, unit) {
      this.timelineDate = moment(this.$store.state.timeline.timelineDate).add(quantity, unit);
    },
  },
  template: `
    <div id="timeline" class="container">
      <timeline-nav></timeline-nav>
      <h2>
        {{ timelineDate.format('LL') }}
        <small>{{ relativeTimelineDate }}</small>
      </h2>
      <spinner v-if="isLoading"></spinner>
      <div class="tiles">
        <tile :entry="entry" v-for="entry in entries" :key="entry.id"></tile>
      </div>
    </div>
  `
});