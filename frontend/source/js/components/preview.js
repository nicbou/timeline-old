export default Vue.component('preview', {
  props: ['entry'],
  data: function() {
    return {}
  },
  computed: {
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
    <div class="preview">
      <img :alt="entry.title" :src="entry.extra_attributes.previews.large || entry.extra_attributes.previews.small"/>
    </div>
  `
});