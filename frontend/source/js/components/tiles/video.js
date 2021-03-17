export default Vue.component('video-tile', {
  props: ['entry'],
  computed: {
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
    <div class="tile" @click="$emit('select', entry)" v-if="entry.extra_attributes.previews">
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