export default Vue.component('tile', {
  props: ['entry'],
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
    <div class="tile" v-if="entry.extra_attributes.previews">
      <img
        :alt="entry.title"
        :src="entry.extra_attributes.previews.small"/>
    </div>
  `
});