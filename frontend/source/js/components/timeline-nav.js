export default Vue.component('timeline-nav', {
  computed: {
    timelineDate: {
      get() {
        return this.$store.state.timeline.timelineDate.format('YYYY-MM-DD');
      },
      set(newDate) {
        return this.$store.dispatch('timeline/setTimelineDate', moment(newDate));
      }
    },
    timelineDateIso: {
      get() {
        return this.$store.state.timeline.timelineDate;
      },
      set(newDate) {
        return this.$store.dispatch('timeline/setTimelineDate', newDate);
      }
    },
    today: function(){
      return moment().startOf('day');
    },
  },
  methods: {
    pickTimelineDate: function(date) {
      this.timelineDate = moment(date);
    },
    moveTimelineDate: function(quantity, unit) {
      this.timelineDate = moment(this.$store.state.timeline.timelineDate).add(quantity, unit);
    },
  },
  template: `
    <nav id="timeline" class="container">
      <button @click="moveTimelineDate('years', -1)">-1Y</button>
      <button @click="moveTimelineDate('months', -1)">-1M</button>
      <button @click="moveTimelineDate('weeks', -1)">-1W</button>
      <button @click="moveTimelineDate('days', -1)">-1D</button>
      <input type="date" v-model="timelineDate">
      <button @click="pickTimelineDate(today)">Today</button>
      <button @click="moveTimelineDate('days', 1)">+1D</button>
      <button @click="moveTimelineDate('weeks', 1)">+1W</button>
      <button @click="moveTimelineDate('months', 1)">+1M</button>
      <button @click="moveTimelineDate('years', 1)">+1Y</button>
    </nav>
  `
});