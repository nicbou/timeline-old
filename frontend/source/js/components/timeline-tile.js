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
    mimetype: function(){
      if (this.entry.extra_attributes) {
        return this.entry.extra_attributes.mimetype;
      }
      return undefined;
    }
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
    <div class="tile" v-if="entry.extra_attributes.previews" :style="tileStyle" :class="tileClasses" @click="$emit('click', entry)">
      <img 
        :alt="entry.title" :src="entry.extra_attributes.previews.small"
        loading="lazy" 
        v-if="mimetype.startsWith('image')"/>
      <video
        :alt="entry.title"
        :src="entry.extra_attributes.previews.small"
        @mouseleave="videoHoverEnd"
        @mouseover="videoHoverStart"
        loop
        ref="videoElement"
        v-if="mimetype.startsWith('video')"/>
    </div>
  `
});