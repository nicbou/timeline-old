export default Vue.component('post-preview', {
  props: ['entry'],
  template: `
    <post-tile :entry="entry"></post-tile>
  `
});