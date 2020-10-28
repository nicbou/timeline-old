import SpinnerComponent from './spinner.js';

export default Vue.component('timeline', {
  data: function() {
    return {}
  },
  computed: {
    timelineDate: function() {
      return this.$store.state.timeline.timelineDate;
    },
    relativeTimelineDate: function() {
      return moment.duration(this.timelineDate.diff(moment().startOf('day'))).humanize(true);
    },
    entries: function() {
      return this.$store.state.timeline.entries;
    },
  },
  created: function () {
    this.$store.dispatch('timeline/getEntries');
  },
  methods: {
    pickTimelineDate: function(event) {
      const newDate = moment(event.target.valueAsNumber);
      return this.$store.dispatch('timeline/setTimelineDate', newDate);
    },
    moveTimelineDate: function(quantity, unit) {
      const newDate = moment(this.$store.state.timeline.timelineDate).add(quantity, unit);
      return this.$store.dispatch('timeline/setTimelineDate', newDate);
    },
  },
  template: `
    <div id="timeline" class="container">
      <button @click="moveTimelineDate(-1, 'years')">-1Y</button>
      <button @click="moveTimelineDate(-1, 'months')">-1M</button>
      <button @click="moveTimelineDate(-1, 'weeks')">-1W</button>
      <button @click="moveTimelineDate(-1, 'days')">-1D</button>
      <input type="date" :value="timelineDate.format('YYYY-MM-DD')" @change="pickTimelineDate"/>
      <button @click="moveTimelineDate(1, 'days')">+1D</button>
      <button @click="moveTimelineDate(1, 'weeks')">+1W</button>
      <button @click="moveTimelineDate(1, 'months')">+1M</button>
      <button @click="moveTimelineDate(1, 'years')">+1Y</button>
      <h2>
        {{ timelineDate.format('LLLL') }}
        <small>{{ relativeTimelineDate }}</small>
      </h2>
      <div class="tiles">
        <div class="tile" v-for="entry in entries" v-if="entry.extra_attributes.previews" :key="entry.id">
          <img
            :alt="entry.title"
            :src="entry.extra_attributes.previews.small"/>
        </div>
      </div>
    </div>
  `
});