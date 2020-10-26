import SpinnerComponent from './spinner.js';

export default Vue.component('timeline', {
  data: function() {
    return {}
  },
  computed: {
    timelineDate: function() {
      return this.$store.state.timeline.timelineDate;
    },
    entries: function() {
      return this.$store.state.timeline.entries;
    },
  },
  created: function () {
    this.$store.dispatch('timeline/getEntries');
  },
  methods: {
    setTimelineDate: function(quantity, unit) {
      const newDate = moment(this.$store.state.timeline.timelineDate).add(quantity, unit);
      return this.$store.dispatch('timeline/setTimelineDate', newDate);
    },
  },
  template: `
    <div id="timeline" class="container">
      <button @click="setTimelineDate(-1, 'days')">Prev</button>
      <button @click="setTimelineDate(1, 'days')">Next</button>
      <h2>{{ timelineDate }}</h2>
      {{ entries }}
      <div class="timeline-items">
        <div class="timeline-item" v-for="entry in entries" v-if="entry.extra_attributes.preview" :key="entry.id">
          <span class="title">{{ entry.title }}</span>
          <img
            :alt="entry.title"
            :src="entry.extra_attributes.previews.small"/>
        </div>
      </div>
    </div>
  `
});