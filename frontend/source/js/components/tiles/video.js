export default Vue.component('video-tile', {
  props: ['entry'],
  computed: {
    tileStyle: function() {
      if(this.entry.extra_attributes.width && this.entry.extra_attributes.height) {
        return {
          width: `${this.entry.extra_attributes.width / this.entry.extra_attributes.height * 200}px`,
        }
      }
    },
    hasGeolocation: function() {
      return !!this.entry.extra_attributes.location;
    },
  },
  methods: {
    videoHoverStart: function() {
      this.$refs.videoElement.play()
    },
    videoHoverEnd: function() {
      this.$refs.videoElement.pause()
      this.$refs.videoElement.currentTime = 0;
    },
  },
  template: `
    <div class="tile" :style="tileStyle" @click="$emit('select', entry)">
      <video
        :alt="entry.title"
        :src="entry.extra_attributes.previews.thumbnail"
        @mouseleave="videoHoverEnd"
        @mouseover="videoHoverStart"
        loop
        ref="videoElement"/>
      <div class="tile-icons">
        <i v-if="hasGeolocation" class="fas fa-map-marker-alt"></i>
        <i class="fas fa-play-circle"></i>
      </div>
    </div>
  `
});