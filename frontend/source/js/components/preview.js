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
      <img :alt="entry.title" :src="entry.extra_attributes.previews.large || entry.extra_attributes.previews.small"/>
    </div>
  `
});