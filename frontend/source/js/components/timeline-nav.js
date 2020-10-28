export default Vue.component('timeline-nav', {
  computed: {
    timelineDate: {
      get() {
        return this.$store.state.timeline.timelineDate;
      },
      set(newDate) {
        newDate = moment.min(newDate, this.today);
        return this.$store.dispatch('timeline/setTimelineDate', moment(newDate));
      }
    },
    timelineDateIso: {
      get() {
        return this.timelineDate.format('YYYY-MM-DD');
      },
      set(newDate) {
        return this.timelineDate = moment(newDate);
      }
    },
    today: function(){
      return moment().startOf('day');
    },
    showTomorrow: function() {
      return moment(this.timelineDate).add('days', 1).diff(this.today) <= 0
    },
    showNextWeek: function() {
      return moment(this.timelineDate).add('weeks', 1).diff(this.today) <= 0
    },
    showNextMonth: function() {
      return moment(this.timelineDate).add('months', 1).diff(this.today) <= 0
    },
    showNextYear: function() {
      return moment(this.timelineDate).add('years', 1).diff(this.today) <= 0
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
      <input type="date" v-model="timelineDateIso">
      <button @click="pickTimelineDate(today)">Today</button>
      <button :disabled="!showTomorrow" @click="moveTimelineDate('days', 1)">+1D</button>
      <button :disabled="!showNextWeek" @click="moveTimelineDate('weeks', 1)">+1W</button>
      <button :disabled="!showNextMonth" @click="moveTimelineDate('months', 1)">+1M</button>
      <button :disabled="!showNextYear" @click="moveTimelineDate('years', 1)">+1Y</button>
    </nav>
  `
});