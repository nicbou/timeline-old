function getNestedProperty(obj, ...args) {
  return args.reduce((obj, level) => obj && obj[level], obj)
}

export default Vue.component('tile', {
  props: ['entry'],
  computed: {
    tileStyle: function() {
      if(this.entry.extra_attributes.width && this.entry.extra_attributes.height) {
        return {
          width: `${this.entry.extra_attributes.width / this.entry.extra_attributes.height * 200}px`,
        }
      }
    },
    tileClasses: function() {
      return [this.entry.schema.replace('.', '-')]
    }
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
    <div class="tile" v-if="entry.extra_attributes.previews" :style="tileStyle" :class="tileClasses" @click="$emit('click', entry)">
      <img
        :alt="entry.title"
        :src="entry.extra_attributes.previews.small"
        loading="lazy"/>
    </div>
  `
});