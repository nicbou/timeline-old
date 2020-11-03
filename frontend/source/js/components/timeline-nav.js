export default Vue.component('timeline-nav', {
  computed: {
    timelineDate: {
      get() {
        return moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true);
      },
      set(newDate) {
        const routeParams = {
          name: 'timeline',
          query: {
            date: moment.min(newDate, this.today).format('YYYY-MM-DD'),
          }
        };
        return this.$router.push(routeParams);
      }
    },
    timelineDateIso: {
      get() {
        return this.$store.state.route.query.date;
      },
      set(newDate) {
        return this.timelineDate = moment(newDate, 'YYYY-MM-DD', true);
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
      this.timelineDate = moment(this.timelineDate).add(quantity, unit);
    },
  },
  template: `
    <div>
      <button class="button" @click="moveTimelineDate('years', -1)">-1Y</button>
      <button class="button" @click="moveTimelineDate('months', -1)">-1M</button>
      <button class="button" @click="moveTimelineDate('weeks', -1)">-1W</button>
      <button class="button" @click="moveTimelineDate('days', -1)">-1D</button>
      <input class="input" type="date" v-model="timelineDateIso" :max="today.format('YYYY-MM-DD')">
      <button class="button" @click="pickTimelineDate(today)">Today</button>
      <button class="button" :disabled="!showTomorrow" @click="moveTimelineDate('days', 1)">+1D</button>
      <button class="button" :disabled="!showNextWeek" @click="moveTimelineDate('weeks', 1)">+1W</button>
      <button class="button" :disabled="!showNextMonth" @click="moveTimelineDate('months', 1)">+1M</button>
      <button class="button" :disabled="!showNextYear" @click="moveTimelineDate('years', 1)">+1Y</button>
    </div>
  `
});