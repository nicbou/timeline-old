export default Vue.component('preview', {
  props: ['entry'],
  computed: {
    mimetype: function(){
      if (this.entry.extra_attributes) {
        return this.entry.extra_attributes.mimetype;
      }
      return undefined;
    }
  },
  methods: {
    close: function(event) {
      this.$emit('close');
    }
  },
  template: `
    <div class="preview">
      <button class="close" @click="close">Close</button>
      <img v-if="mimetype.startsWith('image')" :alt="entry.title" :src="entry.extra_attributes.previews.large"/>
      <video autoplay controls v-if="mimetype.startsWith('video')" :alt="entry.title" :src="entry.extra_attributes.previews.small"/>
    </div>
  `
});