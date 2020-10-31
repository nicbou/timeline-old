export default Vue.component('preview', {
  props: ['entry'],
  methods: {
    close: function(event) {
      this.$emit('close');
    },
  },
  template: `
    <div class="preview">
      <button class="close" @click="close">Close</button>
      <img v-if="entry.extra_attributes.previews.small.endsWith('.jpg')" :alt="entry.title" :src="entry.extra_attributes.previews.large"/>
      <video autoplay controls v-if="entry.extra_attributes.previews.small.endsWith('.mp4')" :alt="entry.title" :src="entry.extra_attributes.previews.small"/>
    </div>
  `
});