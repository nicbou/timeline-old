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
    },
    isVideo: function() {
      return (
        this.entry.extra_attributes.previews
        && this.entry.extra_attributes.previews.small
        && this.entry.extra_attributes.previews.small.endsWith('.mp4')
      );
    },
    isImage: function() {
      return (
        this.entry.extra_attributes.previews
        && this.entry.extra_attributes.previews.small
        && this.entry.extra_attributes.previews.small.endsWith('.jpg')
      );
    },
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
    videoHoverStart: function() {
      this.$refs.videoElement.play()
    },
    videoHoverEnd: function() {
      this.$refs.videoElement.pause()
      this.$refs.videoElement.currentTime = 0;
    },
  },
  template: `
    <div class="tile" v-if="entry.extra_attributes.previews" :style="tileStyle" :class="tileClasses" @click="$emit('click', entry)">
      <img loading="lazy" v-if="isImage" :alt="entry.title" :src="entry.extra_attributes.previews.small"/>
      <video ref="videoElement" @mouseover="videoHoverStart" @mouseleave="videoHoverEnd" v-if="isVideo" :alt="entry.title" :src="entry.extra_attributes.previews.small" loop/>
    </div>
  `
});